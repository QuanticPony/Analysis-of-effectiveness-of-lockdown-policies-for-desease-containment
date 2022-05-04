from math import ceil

import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from phaseportrait.sliders import Slider

from .evolution import *
from .parameters_control import *
from .configuration import smooth_deaths_list

epi_poblation_to_index = {
    'sh' : 0,
    's' : 1,
    'e' : 2,
    'i' : 3,
    'pd' : 4,
    'd' : 5,
    'r' : 6,
}

 
def evolve_gpu(params, fixed_params, state, p_active, deaths_list, log_diff, configuration):

    total_population = configuration["total_population"]
    max_days = configuration["max_days"]

    time = params[param_to_index['offset']]
    deaths_ref = cp.zeros(params.shape[1])
    _time = cp.zeros(params.shape[1], dtype=cp.int32)
    _time[:] = time[:]
    # max_deaths_ref = max(deaths_list)
    
    __time_ref = 0

    while (_time<max_days).any():
    # while __time_ref<max_days:
        
        evolve(params, fixed_params, state, p_active[__time_ref])
        deaths = state[5]*total_population
        
        deaths_ref = 0 + deaths_list[_time * (_time>=0)] #TODO: mirar si esto hace falta * (_time>=0)
        # deaths_ref = 0 + deaths_list[__time_ref]
        
        diff = cp.abs(deaths-deaths_ref)
        log_diff += cp.log(diff+1) * (_time<max_days)
        
        _time+=1
        __time_ref+=1
        
def evolve_gpu_no_diff(params, fixed_params, state, p_active, max_days=1):
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




class Simulation:
    _name_='Simulation_PhasePortrait'
    
    def add_slider(self, param_name, *, valinit=None, valstep=0.1, valinterval=10):
        self.sliders.update({param_name: Slider(self, param_name, valinit=valinit, valstep=valstep, valinterval=valinterval)})

        self.fig.subplots_adjust(bottom=0.25)

        self.sliders[param_name].slider.on_changed(self.sliders[param_name])
        
    def __init__(self, deaths_list, p_active, fixed_params, max_days=1, total_population=1) -> None:
        self.fig, self.ax = plt.subplots()
        
        self.fixed_params = fixed_params
        self.max_days = max_days
        self.total_population = total_population
        
        self.parameters = np.zeros(len(param_to_index), dtype=np.float64)
        
        self.p_active = p_active
        self.deaths_list = deaths_list
        
        self.sliders = {}
        self.ax2 = self.ax.twinx()
        
    def plot(self):
        for p, s in self.sliders.items():
            try:
                self.parameters[param_to_index[p]] = s.value
            except KeyError:
                self.fixed_params[fixed_params_to_index[p]] = s.value
        
        self.state = np.zeros(7, dtype=np.float64) 
        self.state[1] = 1- self.parameters[param_to_index['initial_i']]
        self.state[3] = self.parameters[param_to_index['initial_i']]
        
        time_list =  range(len(self.deaths_list)+1)
        self.ax.plot(time_list[:self.max_days], smooth_deaths_list(self.deaths_list[:self.max_days]).get() , color='purple', label='smooth data')
        self.ax.plot(time_list[:self.max_days], self.deaths_list[:self.max_days], label='real data', color='red')
            
        deaths_list =  np.zeros(self.max_days)
        log_diff_hist = np.zeros(self.max_days)
        time = int(self.parameters[param_to_index['offset']])
        __time_ref = 0
        log_diff = 0

        # print(time)

        while time<self.max_days:
        # while __time_ref<max_days:
            
            evolve(self.parameters, self.fixed_params, self.state, self.p_active[__time_ref])
            deaths = self.state[5]*self.total_population
            
            deaths_ref = 0 + self.deaths_list[time * (time>=0)] #TODO: mirar si esto hace falta * (time>=0)
            # deaths_ref = 0 + deaths_list[__time_ref]
            if __time_ref < self.max_days:
                deaths_list[__time_ref] = self.state[5]*self.total_population
            
                # diff = (deaths/(deaths_ref + 1*(deaths_ref<1)))
                diff = cp.abs(deaths - deaths_ref)
                # diff = cp.abs(cp.log(deaths+1)-cp.log(deaths_ref+1))
                log_diff_hist[__time_ref] = cp.abs(cp.log(diff + 1))
                # log_diff_hist[__time_ref] = (diff) * (time<self.max_days)
                log_diff += log_diff_hist[__time_ref]
            
            time+=1
            __time_ref+=1
            
        self.ax.plot(time_list[:self.max_days], deaths_list, '-', color='black', label=f'{log_diff}')

        self.ax.set_title('Muertes diarias (España)')
        self.ax2.clear()

        self.ax2.plot(time_list[:self.max_days], log_diff_hist, color='green')
        self.ax.set_yscale('log')
        self.ax.legend()
        # self.ax.set_ylim(0, max(self.deaths_list[:self.max_days]))
        
        # self.ax2 = self.ax.twinx()
        # self.ax2.plot(time_list[:self.max_days], self.p_active[:self.max_days], color='green', label='p_active')
        # self.ax2.tick_params(axis ='y', labelcolor = 'green') 
        # self.ax2.legend()
