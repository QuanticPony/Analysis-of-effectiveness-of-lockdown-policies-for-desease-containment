from math import ceil
import cupy as cp
import datetime
import matplotlib.pyplot as plt
import numpy as np
from phaseportrait.sliders import Slider

from set_parameters import *
from evolution import *

COUNTRY = 'Spain'
MAX_DAYS = 140
N = 47.5e6

epi_poblation_to_index = {
    'sh' : 0,
    's' : 1,
    'e' : 2,
    'i' : 3,
    'pd' : 4,
    'd' : 5,
    'r' : 6,
}






###############################################




def str_to_date(string, *, strange=False):
    _d = string.split('/')
    if strange:
        return datetime.date(int(_d[2])+2000, int(_d[0]), int(_d[1]))
    return datetime.date(int(_d[0]), int(_d[1]), int(_d[2]))

def date_to_str(date):
    return f"{date.year}-{date.month:>02d}-{date.day:>02d}"
    return date.strftime('%Y-%m-%d')

# Conseguir el array de las muertes diarias. Indice indica la cantidad de días desde first_day_deaths_list

def prepare_deaths_list(requested_country):
    "Returns tuple: `(deaths_list, first_day_deaths_list, lenght_deaths_list)`."
    deaths_complete_db = pandas.read_csv(r'real_data\Deaths_worldwide_1Aug.csv')
    deaths_partial_db = deaths_complete_db[deaths_complete_db['Country']==requested_country]

    first_day_deaths_list = str_to_date(deaths_partial_db['Date'].values[0], strange=True)
    lenght_deaths_list = deaths_partial_db['Date'].size

    deaths_list = cp.zeros(lenght_deaths_list, dtype=cp.int32)
    for _country, date, _cumdeath, death in deaths_partial_db.values:
        deaths_list[(str_to_date(date, strange=True)-first_day_deaths_list).days] = death
    return (deaths_list, first_day_deaths_list, lenght_deaths_list)
    
def plot_deaths(deaths_list):
    fig,ax = plt.subplots()
    ax.plot(range(len(deaths_list)), deaths_list.get())
    ax.grid(True)
    return fig, ax
    
def smooth_deaths_list(deaths_list):
    deaths_list_smooth = cp.zeros(len(deaths_list), dtype=cp.float64)
    for i in range(len(deaths_list)):
        _zeros = 0
        _min = -3 if i > 3 else 0
        _max = 4 if len(deaths_list)-i > 3 else 1
        for j in range(_min,_max):
            if deaths_list[i+j] >= 0:
                deaths_list_smooth[i] += deaths_list[i+j]/(_max-_min)
            else:
                _zeros += 1
            if _zeros > 0:
                deaths_list_smooth[i] *= (_max-_min)/(_max-_min-_zeros)
    return deaths_list_smooth
    
def save_deaths_list(requested_country, deaths_list):
    cp.save(f"real_data/data_by_country/{requested_country}_deaths.npy", deaths_list)

def load_deaths_list(requested_country):
    return cp.load(f"real_data/data_by_country/{requested_country}_deaths.npy")


#! TODO: la movilidad está puesta como porcentaje de reducción o aumento relativo. 
#! Habría que poner inicialmente 1 como movilidad y luego irá bajando? asumo? ni idea.

def prepare_p_active_list(requested_country, first_day_deaths_list, lenght_deaths_list, using='transit_stations_percent_change_from_baseline'):
    "Returns `p_array : cp.ndarray`."
    p_active_complete_db =  pandas.read_csv(r'real_data\reducedgoogledataset.csv',
        dtype = {'country_region_code':'str',
            'country_region':'str',
            'sub_region_1':'str',
            'sub_region_2':'str',
            'metro_area':'str',
            'iso3166_2_code':'str',
            'census_fips_code':'str',
            'retail_and_recreation_percent_change_from_baseline':'float32',
            'grocery_and_pharmacy_percent_change_from_baseline':'float32',
            'parks_percent_change_from_baseline':'float32',
            'transit_stations_percent_change_from_baseline':'float32',
            'workplaces_percent_change_from_baseline':'float32',
            'residential_percent_change_from_baseline':'float32'}
        )
        
    aux  = p_active_complete_db[p_active_complete_db['country_region']==requested_country]
    p_active_partial_db = aux[aux['sub_region_1'].isna()]
    del(aux)
    p_active = cp.ones(lenght_deaths_list, dtype=cp.float64)
    for day in range(lenght_deaths_list):
        p_value = p_active_partial_db[
            p_active_partial_db['date']==date_to_str(first_day_deaths_list+datetime.timedelta(day))
            ][using]
        if not p_value.empty:
        
            __p = float(p_value.values[0])
            if __p < 0:  #! solución a valores positivos
                p_active[day] += float(p_value.values[0]) * 0.01
                
    return p_active

def plot_p_active(p_active):
    fig,ax = plt.subplots()
    ax.plot(range(len(p_active)), p_active.get())
    ax.grid(True)
    return fig, ax

def save_p_active(requested_country, p_active):
    cp.save(f"real_data/data_by_country/{requested_country}_p_active.npy", p_active)

def load_p_active(requested_country):
    return cp.load(f"real_data/data_by_country/{requested_country}_p_active.npy")





###############################################



 
def evolve_gpu(params, fixed_params, state, p_active, deaths_list, log_diff, max_days=MAX_DAYS, total_poblation=N):
    
    AJUSTE = 1
    time = -1
    
    while time<max_days:
        time+=1
        evolve(params, fixed_params, state, time, p_active)
        deaths = state[5]*total_poblation
        
        if deaths_list[time]>0:
            diff = deaths/deaths_list[time]
        if deaths_list[time]<1:
            diff = deaths + 1
            

        log_diff += cp.abs(cp.log(diff)) * ((diff<1)*AJUSTE + 1) 

        continue
        

        if deaths_list[time]>0:
            diff = deaths/deaths_list[time]
        if deaths_list[time]<1:
            diff = deaths + 1
            
        log_diff += cp.log(diff) * (2/(1+cp.exp(AJUSTE*(1-diff)))+1)*AJUSTE
        continue
        
def evolve_gpu_no_diff(params, fixed_params, state, p_active, max_days=MAX_DAYS):
    time = 0
    while time<max_days:
        evolve(params, fixed_params, state, time, p_active)
        time+=1






###############################################




## Seleccionar los 5% mejores
def get_best_parameters(params, log_diff, save_percentage):
    "Retuns the best `save_percentage`% `params` of the simulations given their `log_diff` with real data." 
    log_diff_index_sorted = cp.argsort(log_diff)
    # Para comprobar que indices tomar en el sort
    # print(log_diff[log_diff_index_sorted[0]], log_diff[log_diff_index_sorted[-1]])
    
    save_count = ceil(log_diff.size*save_percentage*0.01)
    # save_count = 6

    saved_params = cp.zeros((len(param_to_index),save_count), dtype=cp.float64)
    saved_log_diff = cp.zeros(save_count, dtype=cp.float64)

    for i in range(save_count):
        saved_params[:,i] = params[:,log_diff_index_sorted[i]]
        saved_log_diff[i] = log_diff[log_diff_index_sorted[i]]
    return saved_params, saved_log_diff

def prepare_states(params):
    "Creates and returns `state` from given `params`"
    state = cp.zeros((7,params.shape[1]), dtype=cp.float64)
    state[1] = 1-params[4]
    state[3] = params[4]
    return state


# Volver a ejecutar los mejores para plotearlos
def plot_states(params, fixed_params, state, deaths_list, p_active, max_days=MAX_DAYS, total_population=N):
    fig, ax = plt.subplots()
    
    time_list =  range(len(deaths_list)+1)
    
    
    time = 0
    while time < max_days:
        evolve(params, fixed_params, state, time, p_active)

        ax.plot([time for i in range(params.shape[1])], state[5].get()*total_population, ',', color='black')
        # colors = ['purple', 'green', 'blue', 'orange', 'red', 'black', 'pink']
        # for i in range(state.shape[0]):
        #     ax.plot([time for _ in range(state.shape[1])], state[i,:].get()*total_population, '.', color=colors[i])

        time+=1

    ax.plot(time_list[:max_days], deaths_list.get()[:max_days], color='red', label='real data')
    ax.set_title('Deaths per day')
    ax.legend()
    ax.set_ylim(0, max(deaths_list.get()[:max_days]))
    ax2 = ax.twinx()
    ax2.plot(time_list[:max_days], p_active[:max_days].get(), color='green', label='p_active')
    ax2.tick_params(axis ='y', labelcolor = 'green') 
    ax2.legend()
    return fig, ax



def median(array):
    return percentil(array, 50)
    
def percentil(array, i):
    index = array.size * i / 100
    decimal, complete = np.modf(index)
    complete = int(complete)
    if decimal==0:
        return array[complete+1]
    return (array[complete] + array[complete+1])/2


def plot_percentiles(params, fixed_params, state, deaths_list, p_active, max_days=MAX_DAYS, total_population=N):
    fig, ax = plt.subplots()
    
    time_list =  range(len(deaths_list)+1)
    
    time = 0
    
    deaths_plotted = np.zeros((len(deaths_list)+1,3))

    
    while time < max_days:
        evolve(params, fixed_params, state, time, p_active)
        copy_deaths = (state[5].get()*N).copy()
        copy_deaths.sort()
        percentil(copy_deaths, 5)
        time+=1
        
    ax.plot(time_list[:max_days], deaths_plotted[:,0][:max_days], '-.', color='red', label='percentil 5')
    ax.plot(time_list[:max_days], deaths_plotted[:,1][:max_days], '-.', color='orange', label='median')
    ax.plot(time_list[:max_days], deaths_plotted[:,2][:max_days], '-.', color='yellow', label='percentil 95')
    ax.fill_between(time_list[:max_days], deaths_plotted[:,0][:max_days], deaths_plotted[:,2][:max_days], alpha=0.2)

    ax.plot(time_list[:max_days], deaths_list.get()[:max_days], color='black', label='real data')
    ax.set_title('Deaths per day')
    ax.legend()
    ax.set_ylim(0, max(deaths_list.get()[:max_days]))
    return fig, ax




def correlations(params, n_bins):
    from matplotlib.ticker import NullFormatter
    
    for i_n, i in param_to_index.items():
        for j_n, j in param_to_index.items():
            if i < j:
                
                try:
                    x = params[i,:].get()
                    y = params[j,:].get()
                except AttributeError:
                    x = params[i,:]
                    y = params[j,:]
                
                nullfmt = NullFormatter()         # no labels
                
                # definitions for the axes
                left, width = 0.1, 0.65
                bottom, height = 0.1, 0.65
                bottom_h = left_h = left + width + 0.02
                
                rect_scatter = [left, bottom, width, height]
                rect_histx = [left, bottom_h, width, 0.2]
                rect_histy = [left_h, bottom, 0.2, height]
                
                # start with a rectangular Figure
                fig = plt.figure(1, figsize=(8, 8))
                
                axScatter = plt.axes(rect_scatter)
                axHistx = plt.axes(rect_histx)
                axHistx.set_title("$"+ i_n +"$")
                axHisty = plt.axes(rect_histy)
                axHisty.set_title("$"+ j_n +"$")
                
                # no labels
                axHistx.xaxis.set_major_formatter(nullfmt)
                axHisty.yaxis.set_major_formatter(nullfmt)
                
                # the scatter plot:
                # axScatter.scatter(x, y)
                
                
                # now determine nice limits by hand:
                xymax = [np.max(np.fabs(x)), np.max(np.fabs(y))]
                xymin = [np.min(np.fabs(x)), np.min(np.fabs(y))]
                
                axScatter.set_xlim((xymin[0], xymax[0]))
                axScatter.set_ylim((xymin[1], xymax[1]))
                
                xbins = np.linspace(xymin[0], xymax[0], n_bins)
                ybins = np.linspace(xymin[1], xymax[1], n_bins)
                
                axScatter.hist2d(x, y, bins=[xbins, ybins])
                axHistx.hist(x, bins=xbins)
                axHisty.hist(y, bins=ybins, orientation='horizontal')
                
                axHistx.set_xlim(axScatter.get_xlim())
                axHisty.set_ylim(axScatter.get_ylim())
                
                fig.savefig(f'images\images_by_country\{COUNTRY}\correlation_{i_n}_{j_n}.png')
                plt.close(fig)




#############################################











class Simulation:
    _name_='Simulation_PhasePortrait'
    
    def add_slider(self, param_name, *, valinit=None, valstep=0.1, valinterval=10):
        self.sliders.update({param_name: Slider(self, param_name, valinit=valinit, valstep=valstep, valinterval=valinterval)})

        self.fig.subplots_adjust(bottom=0.25)

        self.sliders[param_name].slider.on_changed(self.sliders[param_name])
        
    def __init__(self, deaths_list, p_active, fixed_params, max_days=MAX_DAYS, total_population=N) -> None:
        self.fig, self.ax = plt.subplots()
        
        self.fixed_params = fixed_params
        self.max_days = max_days
        self.total_population = total_population
        
        self.state = np.zeros(7, dtype=np.float64)
        self.parameters = np.zeros(5, dtype=np.float64)
        
        self.p_active = p_active
        self.deaths_list = deaths_list
        
        self.sliders = {}
        
    def plot(self):
        for p, s in self.sliders.items():
            try:
                self.parameters[param_to_index[p]] = s.value
            except KeyError:
                self.fixed_params[fixed_params_to_index[p]] = s.value
        
        self.state = np.zeros(7, dtype=np.float64) 
        self.state[1] = 1-self.parameters[4]
        self.state[3] = self.parameters[4]
        
        time_list =  range(len(self.deaths_list)+1)
        self.ax.plot(time_list[:self.max_days], smooth_deaths_list(self.deaths_list[:self.max_days]).get() , label='smooth data')
        self.ax.plot(time_list[:self.max_days], self.deaths_list[:self.max_days], label='real data')
        
        time = -1
        deaths_list = np.zeros(self.max_days)
        log_diff = 0
        while time < self.max_days-1:
            time+=1
            evolve(self.parameters, self.fixed_params, self.state, time, self.p_active)

            deaths_list[time] = self.state[5]*self.total_population
  
            # log_diff += np.abs(deaths_list[time]/(self.deaths_list[time]+0.0001)-1)
            if self.deaths_list[time]>0:
                diff = deaths_list[time]/self.deaths_list[time]
                log_diff += cp.abs(cp.log(diff))
                continue
            if self.deaths_list[time]<1:
                diff = deaths_list[time] + 1
                log_diff += cp.abs(cp.log(diff))
                continue
            
            
        self.ax.plot(time_list[:self.max_days], deaths_list, '-', color='black', label=f'{log_diff}')

        self.ax.set_title('Muertes diarias (España)')
        self.ax.legend()
        # self.ax.set_ylim(0, max(self.deaths_list[:self.max_days]))
        
        # self.ax2 = self.ax.twinx()
        # self.ax2.plot(time_list[:self.max_days], self.p_active[:self.max_days], color='green', label='p_active')
        # self.ax2.tick_params(axis ='y', labelcolor = 'green') 
        # self.ax2.legend()