import datetime
import os

import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from .configuration import date_to_spanish
from .evolution import *
from .parameters_control import *

import matplotlib.figure as figure


def prepare_states(params, total_population):
    "Creates and returns `state` from given `params`"
    state = cp.zeros((7,params.shape[1]), dtype=cp.float64)
    state[1] = 1-params[param_to_index['initial_i']]
    state[3] = params[param_to_index['initial_i']]
    return state


# Volver a ejecutar los mejores para plotearlos
def plot_states(params, fixed_params, deaths_list, smooth_deaths_list, p_active, configuration, name=""):
    TOTAL_POPULATION = configuration["total_population"]
    MAX_DAYS = configuration["max_days"]
    COUNTRY = configuration["country"]

    states = prepare_states(params, TOTAL_POPULATION)


    _5p = []
    _95p = []
    _median = []
    
    NEW_MAX_DAYS= MAX_DAYS+40
    time = params[param_to_index['offset']]
    deaths = cp.zeros([NEW_MAX_DAYS, params.shape[1]])
    _range = cp.arange(0, params.shape[1]) 
    _time = cp.zeros(params.shape[1], dtype=cp.int32)
    _time[:] = time[:]
    
    recovered_array = cp.zeros(params.shape[1])
    

    __time_ref = 0
    while (_time<NEW_MAX_DAYS).any():
    # while __time_ref<NEW_MAX_DAYS:
        
        evolve(params, fixed_params, states, p_active[(__time_ref-NEW_MAX_DAYS) * (__time_ref<MAX_DAYS) + NEW_MAX_DAYS])
        
        deaths[_time * (_time>=0) * (NEW_MAX_DAYS>_time),_range] += states[5,_range]*TOTAL_POPULATION * (_time<NEW_MAX_DAYS) * (_time>=0)
        # deaths[__time_ref, _range] += states[5,_range]*TOTAL_POPULATION
        recovered_array[_range] += states[6, _range] * (_time==113)
        
        _time += 1
        __time_ref += 1
        
    #######################################
    ## Recovered plot

    fontsize = 'small'

    with plt.style.context('science'):
        fig_rec, ax_rec = plt.subplots()
        recovered_data = recovered_array.get()*100
        ax_rec.hist(recovered_data, 15, density=True, alpha=0.5, linewidth=0.8, edgecolor="tab:grey", fill=False)
        # ax_rec.set_title(r'Recuperados (%) a 15 Mayo 2020')
        ax_rec.set_ylabel('Frecuencia relativa')
        ax_rec.set_yticklabels([])

        x = np.linspace(start=recovered_data.min(), stop=recovered_data.max(), num=30)
        gkde = stats.gaussian_kde(dataset=recovered_data)
        ax_rec.plot(x, gkde.evaluate(x), linestyle='solid', color="tab:blue", lw=1.3, alpha=0.7)
        ax_rec.fill_between(x, np.zeros(x.shape[0]), gkde.evaluate(x), alpha=0.4)

        ax_rec.vlines(5, 0, gkde.evaluate(5), label="Pollán, Marina, et al.", color='red')
        ax_rec.set_xlabel('Recuperados (\%) a 15 Mayo 2020')
        filename_path = f'images/images_by_country/{COUNTRY}/'
        os.makedirs(filename_path, exist_ok=True)
        fig_rec.savefig(f'{filename_path}/recovered_histogram{name}.png')
        fig_rec.savefig(f'{filename_path}/recovered_histogram{name}.pdf')
        plt.close(fig_rec)
    #######################################
        

    deaths[0,:] = 0

    time = 0
    while time<NEW_MAX_DAYS:
        deaths_ = deaths[time, _range].copy()
        deaths_.sort()
        _median.append(median(deaths_).get())
        _5p.append(percentil(deaths_, 5).get())
        _95p.append(percentil(deaths_, 95).get())
        time+=1


    with plt.style.context('science'):
        w, h = figure.figaspect(2.5/4)
        fig_ = figure.Figure(figsize=(w, h))
        ax_ = fig_.add_axes([0.1, 0.1, 0.8, 0.8])
        # fig_, ax_ = plt.subplots(figsize=(4,2.5))
        _visibility = 0.1

        time_list =  np.arange(NEW_MAX_DAYS)

        linewidth=0.5

        l_reales, = ax_.plot(time_list[:MAX_DAYS], deaths_list.get()[0:MAX_DAYS], linestyle='dashed', linewidth=linewidth , color='red', zorder=2, label="Datos usados")
        # ax_.plot(time_list[MAX_DAYS:NEW_MAX_DAYS], deaths_list.get()[MAX_DAYS:NEW_MAX_DAYS], linestyle='dotted', color='red', zorder=1)
        ax_.plot(time_list[:MAX_DAYS], smooth_deaths_list.get()[0:MAX_DAYS], linewidth=linewidth*1.5 , color='black', zorder=1)
        l_usados, = ax_.plot(time_list[MAX_DAYS:NEW_MAX_DAYS], smooth_deaths_list.get()[MAX_DAYS:NEW_MAX_DAYS], linestyle='dashed', linewidth=linewidth, color='black', zorder=1, label='Datos suavizados')
        
        ax_.fill_between(time_list, _5p, _95p, color="tab:blue", alpha=0.3, zorder=0, lw=0)
        l_modelo, = ax_.plot(time_list, _median, '-.', color='purple', label='Modelo', zorder=1)
        
        ax_p_active = ax_.twinx()
        l_active, = ax_p_active.plot(time_list[:NEW_MAX_DAYS], p_active.get()[:NEW_MAX_DAYS], linestyle='dotted', color='green', zorder=-1, label='p(t) Google')
        # ax_p_active.plot(time_list[:NEW_MAX_DAYS]-6, p_active.get()[:NEW_MAX_DAYS], '-.', color='orange', label='p_active offset')
        ax_p_active.set_ylabel('$p(t)$')
        # ax_p_active.legend(loc='upper center')
        ax_p_active.set_ylim([0,1.1])
        ax_p_active.set_yticks([0.1*i for i in range(0,11,5)])#, alpha=_visibility)
        
        # ax_.set_xlabel('Days after 22 January 2020')
        ax_.set_ylabel('Muertes diarias', fontsize=fontsize)
        # ax_.set_title('Fatalities per day')

        ax_.legend(handles=[l_reales, l_usados, l_modelo, l_active], loc='upper center', bbox_to_anchor=(0.5, 1.2), ncol=2, frameon=False, fontsize=fontsize)
        ax_.set_xlim(xmin=0)
        ax_.set_ylim([0,max(deaths_list.get()[:MAX_DAYS])*1.1])
        
        first_day_deaths_list = datetime.datetime(*(map(int, configuration["first_day_deaths_list"].split('-'))))
        ticks = [i for i in range(10, NEW_MAX_DAYS, 14)]
        ticks_labels = [date_to_spanish((first_day_deaths_list+datetime.timedelta(i)).strftime("%b\n%d")) for i in ticks]
        
        ax_.set_xticks(ticks)#, alpha=_visibility)
        # ax_.set_yticks(ax_.get_yticks()[::2])#, alpha=_visibility)
        ax_.set_xticklabels(ticks_labels, fontsize=fontsize)
        ax_.grid(alpha=_visibility*5)
        
    
        # ax_.spines['bottom'].set(alpha=_visibility) #.set_color('#dddddd')
        # ax_.spines['top'].set(alpha=_visibility) #.set_color('#dddddd') 
        # ax_.spines['right'].set(alpha=_visibility) #.set_color('#dddddd')
        # ax_.spines['left'].set(alpha=_visibility) #.set_color('#dddddd')
        
        # ax_p_active.spines['bottom'].set(alpha=_visibility) #.set_color('#dddddd')
        # ax_p_active.spines['top'].set(alpha=_visibility) #.set_color('#dddddd') 
        # ax_p_active.spines['right'].set(alpha=_visibility) #.set_color('#dddddd')
        # ax_p_active.spines['left'].set(alpha=_visibility) #.set_color('#dddddd')

        
        filename_path = f"images/images_by_country/{COUNTRY}/"
        os.makedirs(filename_path, exist_ok=True)
        fig_.savefig(f'{filename_path}/bests_{name}.png', dpi=600)
        fig_.savefig(f'{filename_path}/pdf_bests_{name}.pdf')
        plt.close(fig_)

    return recovered_array



def get_states_boundaries(days, params, fixed_params, p_active, configuration):
    TOTAL_POPULATION = configuration["total_population"]
    MAX_DAYS = days
    COUNTRY = configuration["country"]

    states = prepare_states(params, TOTAL_POPULATION)

    _5p = []
    _95p = []
    _median = []
    
    NEW_MAX_DAYS= configuration["max_days"] + 40
    time = params[param_to_index['offset']]
    deaths = cp.zeros([NEW_MAX_DAYS, params.shape[1]])
    _range = cp.arange(0, params.shape[1]) 
    _time = cp.zeros(params.shape[1], dtype=cp.int32)
    _time[:] = time[:]
    
    recovered_array = cp.zeros(params.shape[1])
    

    __time_ref = 0
    while (_time<NEW_MAX_DAYS).any():
    # while __time_ref<NEW_MAX_DAYS:
        
        evolve(params, fixed_params, states, p_active[(__time_ref-NEW_MAX_DAYS) * (__time_ref<MAX_DAYS) + NEW_MAX_DAYS])
        
        deaths[_time * (_time>=0) * (NEW_MAX_DAYS>_time),_range] += states[5,_range]*TOTAL_POPULATION * (_time<NEW_MAX_DAYS) * (_time>=0)
        # deaths[__time_ref, _range] += states[5,_range]*TOTAL_POPULATION
        recovered_array[_range] += states[6, _range] * (_time==113)
        
        _time += 1
        __time_ref += 1
        
    deaths[0,:] = 0

    time = 0
    while time<NEW_MAX_DAYS:
        deaths_ = deaths[time, _range].copy()
        deaths_.sort()
        _median.append(median(deaths_).get())
        _5p.append(percentil(deaths_, 5).get())
        _95p.append(percentil(deaths_, 95).get())
        time+=1

    return _5p, _median, _95p



def median(array):
    return percentil(array, 50)
    
def percentil(array, i):
    index = array.size * i / 100
    decimal, complete = np.modf(index)
    complete = int(complete)
    if decimal==0:
        return array[complete+1]
    return (array[complete] + array[complete+1])/2


def plot_percentiles(params, fixed_params, state, deaths_list, p_active, max_days=1, total_population=1):
    fig, ax = plt.subplots()
    
    time_list =  range(len(deaths_list)+1)
    
    time = 0
    
    deaths_plotted = np.zeros((len(deaths_list)+1,3))

    
    while time < max_days:
        evolve(params, fixed_params, state, time, p_active)
        copy_deaths = (state[5].get()*total_population).copy()
        copy_deaths.sort()
        percentil(copy_deaths, 5)
        time+=1
        
    ax.plot(time_list[:max_days], deaths_plotted[:,0][:max_days], '-.', color='red', label='percentil 5')
    ax.plot(time_list[:max_days], deaths_plotted[:,1][:max_days], '-.', color='orange', label='mediana')
    ax.plot(time_list[:max_days], deaths_plotted[:,2][:max_days], '-.', color='yellow', label='percentil 95')
    ax.fill_between(time_list[:max_days], deaths_plotted[:,0][:max_days], deaths_plotted[:,2][:max_days], alpha=0.2)

    ax.plot(time_list[:max_days], deaths_list.get()[:max_days], color='black', label='real data')
    ax.set_title('Muertes diarias')
    ax.legend()
    ax.set_ylim(0, max(deaths_list.get()[:max_days]))
    return fig, ax



