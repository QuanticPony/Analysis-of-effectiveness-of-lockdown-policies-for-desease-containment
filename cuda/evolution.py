import cupy as cp
import cupy.random as cprand
import cupy.cuda as cuda

from set_parameters import *

def evolve_gpu(params: cp.ndarray, state: cp.ndarray):
    ...
    
    
    
def P_home_is_secure(params, fixed_params, state):
    'pow((1 - i), sigma - 1)'
    return cp.power((1 - state[3]), fixed_params[0] - 1)

def P_secure_in_home(params, fixed_params, state, time, p_active):
    '(1-p_active)*sh*(1-permeability)'
    return (1 - p_active[time]) * P_home_is_secure(params, fixed_params, state) * (1 - params[0])

def P_infection(params, fixed_params, state, time, p_active):
    'p_active*(p_successfull_infection) + (1+p_active)*(p_successfull_infection)'
    P_not_successful_infection = 1 - params[1] * state[3]

    P_active_infections = p_active[time] * (
        1 - cp.power(P_not_successful_infection, fixed_params[1])
    )
    P_conf_infections = (1 - p_active[time]) * (
        1 - cp.power(P_not_successful_infection, fixed_params[2])
    )
    return P_active_infections + P_conf_infections


def evolve(params, fixed_params, state, time, p_active):
    p_infection = P_infection(params, fixed_params, state, time, p_active)
    p_home_is_secure = P_home_is_secure(params, fixed_params, state)
    p_secure_in_home = P_secure_in_home(params, fixed_params, state, time, p_active)

    S = state[0] + state[1]

    # sh
    state[0] = S * p_secure_in_home
    
    # s
    state[1] = S * (1-p_secure_in_home) * (1-p_infection)

    # d
    # pd * what
    state[5] = state[4] * fixed_params[3]

    # r
    # (1-IFR)mu * i
    state[6] =  (1-params[2]) * fixed_params[4] * state[3]

    # pd
    # mu*IFR*i + pd*(1-what)
    state[4] = fixed_params[4]*params[2]*state[3] + state[4]*(1-params[3])

    # i
    # e*eta + i*(1-lambda)
    state[3] = state[2]*fixed_params[3] + state[3]*(1-params[1])

    # e
    # S*(1-p_secure_in_home) * p_infection + e*(1-eta)
    state[2] = S*(1-p_secure_in_home)*p_infection + state[3]*(1-fixed_params[3])