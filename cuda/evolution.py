import cupy as cp
import cupy.random as cprand
import cuda

from set_parameters import *

@cuda.jit(device=True)
def evolve_gpu(params: cp.ndarray, state: cp.ndarray):
    ...
    
    
    
def P_home_is_secure(params, state):
    'pow((1 - i), sigma - 1)'
    return cp.power((1 - state[3]), params[3] - 1)

def P_secure_in_home(params, state):
    '(1-p_active)*sh*(1-permeability)'
    return (1 - params) * P_home_is_secure(params, state) * (1 - params[0])

def P_infection(params, state):
    'p_active*(p_successfull_infection) + (1+p_active)*(p_successfull_infection)'
    P_not_successful_infection = 1 - params[6] * state[3]

    P_active_infections = params[1] * (
        1 - cp.power(P_not_successful_infection, params[4])
    )
    P_conf_infections = (1 - params[1]) * (
        1 - cp.power(P_not_successful_infection, params[5])
    )
    return P_active_infections + P_conf_infections

def update_probabilities(params, state):
    P_active = set_p_of_active(params, )
    P_active = P_active_function(self, t, p_active, step_time)
    P_infection = P_infection(params, state)
    P_home_is_secure = P_home_is_secure(params, state)
    P_secure_in_home = P_secure_in_home(params, state)