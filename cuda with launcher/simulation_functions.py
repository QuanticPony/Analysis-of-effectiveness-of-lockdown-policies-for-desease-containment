from math import ceil

import cupy as cp
import matplotlib.pyplot as plt
import numpy as np
from phaseportrait.sliders import Slider

from evolution import *
from parameters_control import *
from configuration import smooth_deaths_list

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

    LOG_SQUARE_THRESHOLD = 10000
    
    __time_ref = 0

    while (_time<max_days).any():
    # while __time_ref<max_days:
        
        evolve(params, fixed_params, state, p_active[__time_ref])
        deaths = state[5]*total_population
        
        deaths_ref = 0 + deaths_list[_time * (_time>=0)] #TODO: mirar si esto hace falta * (_time>=0)
        # deaths_ref = 0 + deaths_list[__time_ref]
        

        ## ABS
        # log_diff +=  cp.abs(
        #         (deaths-deaths_ref)/((deaths + 1*(deaths==0) -deaths_ref)*(deaths>deaths_ref) + deaths_ref + 1*(deaths_ref==0)) 
        #     )

        ## SQUEARE
        # diff = (deaths - deaths_ref)/(deaths + 1*(deaths==0))
        # log_diff += 10*cp.square(diff) * (deaths_ref>=0) * (_time<max_days) * (deaths_ref>LOG_SQUARE_THRESHOLD)

        ## LOG
        diff = deaths/(deaths_ref + 1 *(deaths_ref==0))# * (deaths_ref<0)
        diff += 1 * (deaths_ref==0)
        log_diff += cp.abs(cp.log(diff)) * (_time<max_days)  * (deaths_ref<=LOG_SQUARE_THRESHOLD)#* (1+ 1*(diff>1)) 
        
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
        
    def plot(self):
        for p, s in self.sliders.items():
            try:
                self.parameters[param_to_index[p]] = s.value
            except KeyError:
                self.fixed_params[fixed_params_to_index[p]] = s.value
        
        self.state = np.zeros(7, dtype=np.float64) 
        self.state[1] = 1- 1/self.total_population
        self.state[3] = 1/self.total_population
        
        time_list =  range(len(self.deaths_list)+1)
        self.ax.plot(time_list[:self.max_days], smooth_deaths_list(self.deaths_list[:self.max_days]).get() , label='smooth data')
        self.ax.plot(time_list[:self.max_days], self.deaths_list[:self.max_days], label='real data')
        
        time = -1 + self.parameters[param_to_index['first_i']]
        deaths_list = np.zeros(self.max_days)
        log_diff = 0
        actual_time = -1
        while actual_time < self.max_days-1:
            p_active = self.p_active[int(time) if time >= 0 else 0] 
            deaths_ref = self.deaths_list[int(time) if time >= 0 else 0] 
            
            time += 1
            actual_time  += 1
            evolve(self.parameters, self.fixed_params, self.state, p_active)

            deaths_list[actual_time] = self.state[5]*self.total_population
  
            diff = deaths_list[actual_time] - deaths_ref
            log_diff += 0.0001*cp.square(diff) * (deaths_ref>=200) * (time<self.max_days)

            diff = deaths_list[actual_time]/(deaths_ref + 1 *(deaths_ref==0)) * (deaths_ref<200)
            diff += 1 * (diff==0)
            log_diff += cp.abs(cp.log(diff)) * (time<self.max_days)
            
            
        self.ax.plot(time_list[:self.max_days], deaths_list, '-', color='black', label=f'{log_diff}')

        self.ax.set_title('Muertes diarias (España)')
        self.ax.legend()
        # self.ax.set_ylim(0, max(self.deaths_list[:self.max_days]))
        
        # self.ax2 = self.ax.twinx()
        # self.ax2.plot(time_list[:self.max_days], self.p_active[:self.max_days], color='green', label='p_active')
        # self.ax2.tick_params(axis ='y', labelcolor = 'green') 
        # self.ax2.legend()
