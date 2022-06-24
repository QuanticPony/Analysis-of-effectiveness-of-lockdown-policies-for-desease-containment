import cupy as cp

from .parameters_control import param_to_index, fixed_params_to_index
    
def P_home_is_secure(params, fixed_params, state):
    'pow((1 - i), sigma - 1)'
    return cp.power((1 - state[3]), fixed_params[0] - 1)

def P_secure_in_home(params, fixed_params, state, p_active):
    '(1-p_active)*sh*(1-permeability)'
    return (1 - p_active) * P_home_is_secure(params, fixed_params, state) * (1 - params[0])


def P_infection(params, fixed_params, state, p_active):
    'p_successfull_infection active, p_successfull_infection confined'
    P_not_successful_infection = 1 - params[1] * state[3]

    return (1 - cp.power(P_not_successful_infection, fixed_params[1])) \
            ,(1 - cp.power(P_not_successful_infection, fixed_params[2]))

def evolve(params, fixed_params, state, p_active):
    p_home_is_secure = P_home_is_secure(params, fixed_params, state)
    p_infection_active, p_infection_confined = P_infection(params, fixed_params, state, p_active)
    
    eta = fixed_params[fixed_params_to_index['eta']]
    # eta = params[param_to_index['eta']]
    mu = fixed_params[fixed_params_to_index['mu']]
    # what = fixed_params[fixed_params_to_index['what']]
    what = params[param_to_index['what']]

    S = state[0] + state[1]

    # sh
    state[0] = S * (1-p_active)*p_home_is_secure*(1-params[0])
    
    # s
    delta_S = S * ((p_active) * (p_infection_active) \
                    + (1-p_active) * (1-p_home_is_secure*(1-params[0])) * (p_infection_confined))

    state[1] = (S-state[0]) - delta_S
    # state[1] = S * ((p_active) * (1-p_infection_active) \
    #                 + (1-p_active) * (1-p_home_is_secure)*(1-params[0]) * (1-p_infection_confined) \
    #                 + (1-p_active) * (1-p_home_is_secure)*params[0] * (1-p_infection_active) \
    #                 + (1-p_active) * (p_home_is_secure)*params[0] * (1-p_infection_active))

    # d
    # pd * what
    state[5] = state[4] * what

    # r
    # (1-IFR)mu * i
    state[6] =  (1-params[2]) * mu * state[3] + state[6]

    # pd
    # mu*IFR*i + pd*(1-what)
    state[4] = mu*params[2]*state[3] + state[4]*(1-what)

    # i
    # e*eta + i*(1-mu)
    state[3] = state[2]*eta + state[3]*(1-mu)

    # e
    state[2] = delta_S + state[2]*(1-eta)
                
    # state[2] = S * ((p_active) * p_infection_active \
    #                 + (1-p_active) * (1-p_home_is_secure)*(1-params[0]) * p_infection_confined \
    #                 + (1-p_active) * (1-p_home_is_secure)*params[0] * p_infection_active \
    #                 + (1-p_active) * (p_home_is_secure)*params[0] * p_infection_active) \
    #             + state[2]*(1-eta)