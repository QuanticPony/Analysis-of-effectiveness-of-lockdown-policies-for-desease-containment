import os

import cupy as cp
import matplotlib.pyplot as plt
import numpy as np

from evolution import *
from parameters_control import *

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
    # time = params[param_to_index['first_i']]
    deaths = cp.zeros([NEW_MAX_DAYS, params.shape[1]])
    _range = cp.arange(0, params.shape[1]) 
    _time = cp.zeros(params.shape[1], dtype=cp.int32)
    # _time[:] = time[:]
    
    recovered_array = cp.zeros(params.shape[1])
    

    __time = 0
    # while (_time<NEW_MAX_DAYS).any():
    while __time<NEW_MAX_DAYS:
        
        evolve(params, fixed_params, states, p_active[0+_time * (_time>=0)])
        
        # deaths[_time * (_time>=0) * (NEW_MAX_DAYS>_time),_range] += states[5,_range]*TOTAL_POPULATION * (_time<NEW_MAX_DAYS) * (_time>=0)
        deaths[__time, _range] += states[5,_range]*TOTAL_POPULATION
        recovered_array[_range] += states[6, _range] * (_time==113)
        
        _time += 1
        __time += 1
        
    #######################################
    ## Recovered plot
    fig_rec, ax_rec = plt.subplots()
    ax_rec.hist(recovered_array.get()*100, 15)
    ax_rec.set_title('Recovered % at May 15 2020')
    ax_rec.set_ylabel('Relative frecuency')
    ax_rec.set_xlabel('Recovered %')
    filename_path = f'images/images_by_country/{COUNTRY}/'
    os.makedirs(filename_path, exist_ok=True)
    fig_rec.savefig(f'{filename_path}/recovered_histogram.png')
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



    fig_, ax_ = plt.subplots()

    time_list =  np.arange(NEW_MAX_DAYS)

    ax_.plot(time_list[:MAX_DAYS], deaths_list.get()[0:MAX_DAYS], '-.', color='red', label='real data')
    ax_.plot(time_list[MAX_DAYS:NEW_MAX_DAYS], deaths_list.get()[MAX_DAYS:NEW_MAX_DAYS], '*', color='red')
    ax_.plot(time_list[:MAX_DAYS], smooth_deaths_list.get()[0:MAX_DAYS], color='black', label='smooth')
    ax_.plot(time_list[MAX_DAYS:NEW_MAX_DAYS], smooth_deaths_list.get()[MAX_DAYS:NEW_MAX_DAYS], '-.', color='black')
    
    ax_.fill_between(time_list, _5p, _95p, alpha=0.2)
    ax_.plot(time_list, _median, '-.', color='purple', label='median')
    
    ax_p_active = ax_.twinx()
    ax_p_active.plot(time_list[:NEW_MAX_DAYS], p_active.get()[:NEW_MAX_DAYS], '-.', color='green', label='p_active google')
    # ax_p_active.plot(time_list[:NEW_MAX_DAYS]-6, p_active.get()[:NEW_MAX_DAYS], '-.', color='orange', label='p_active offset')
    ax_p_active.set_ylabel('Movility reduction')
    ax_p_active.legend(loc='upper center')
    ax_p_active.set_ylim([0,1])
    
    ax_.set_xlabel('Days after 22 January 2020')
    ax_.set_ylabel('Daily fatalities')
    ax_.set_title('Fatalities per day')
    
    ax_.legend(loc='center left')
    ax_.set_xlim(xmin=0)
    ax_.set_ylim([0,max(deaths_list.get()[:NEW_MAX_DAYS])*1.1])
    filename_path = f"images/images_by_country/{COUNTRY}/"
    os.makedirs(filename_path, exist_ok=True)
    fig_.savefig(f'{filename_path}/bests_{name}.png')
    plt.close(fig_)



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



