import cupy as cp
import cupy.random as cprand

import pandas

N_SIMULATIONS = 5000000

param_to_index = {
    'permability' : 0,
    'lambda' : 1,
    'IFR' : 2,
    'what' : 3,
    'initial_i' : 4,
    'eta' : 5,
    'mu' : 6,
}

fixed_params_to_index = {
    'home_size' : 0,
    'k_average_active' : 1,
    'k_average_confined' : 2,
}

###########################
## PRIORS
###########################

def set_permability(params, size=N_SIMULATIONS):
    #'permability'
    params[param_to_index['permability']]  = cprand.random(size, dtype=cp.float64)*0.3

def set_lambda(params, size=N_SIMULATIONS):
    #'lambda'
    params[param_to_index['lambda']] = cprand.random(size, dtype=cp.float64) * (0.20-0.05) + 0.05

def set_IFR(params, size=N_SIMULATIONS):
    #'IFR'
    params[param_to_index['IFR']] = cprand.random(size, dtype=cp.float64) * (0.011-0.009) + 0.009

def set_what(params, size=N_SIMULATIONS): # xi
    #'what'
    params[param_to_index['what']] = cprand.random(size, dtype=cp.float64) * (1/6-1/32) + 1/32 #! * 1/7 y 1/21

def set_initial_i(params, size=N_SIMULATIONS):
    #'initial_i'
    params[param_to_index['initial_i']] = cprand.random(size, dtype=cp.float64) * 8E-8
    
def set_mu_variable(params, size=N_SIMULATIONS):
    #'mu'
    params[param_to_index['mu']] = cprand.random(size, dtype=cp.float64) * (0.5-0.1) + 0.1 # 1/4.2

def set_eta_variable(params, size=N_SIMULATIONS):
    #'eta
    params[param_to_index['eta']] = cprand.random(size, dtype=cp.float64) * (0.4-0.1) + 0.1
    
def set_params(params, size=N_SIMULATIONS):
    set_permability(params, size=size)
    set_lambda(params, size=size)
    set_IFR(params, size=size)
    set_what(params, size=size)
    set_initial_i(params, size=size)
    
    if 'mu' in param_to_index.keys():
        set_mu_variable(params, size=size)
    
    if 'eta' in param_to_index.keys():
        set_eta_variable(params, size=size)
    
    
#######################################################################################  
    
## FIXED PARAMETERS

def set_home_size(fixed_params, country, pd_dataframe):
    #'home_size'
    #! TODO: tamaño del hogar. Tengo que buscarlo? O tienen ya referencias?
    fixed_params[fixed_params_to_index['home_size']] = 2.5

def set_k_average_active(fixed_params, country, pd_dataframe):
    #'k_average_active'
    fixed_params[fixed_params_to_index['k_average_active']] = cp.float64(pd_dataframe[pd_dataframe['Country']==country]['kaverage'])

def set_k_average_confined(fixed_params, country, pd_dataframe):
    #'k_average_confined'
    fixed_params[fixed_params_to_index['k_average_confined']] = cp.float64(pd_dataframe[pd_dataframe['Country']==country]['kaverage'])

def set_eta(fixed_params):
    #'eta'
    fixed_params[fixed_params_to_index['eta']] = 1/5.2
    
def set_mu(fixed_params):
    #'mu'
    fixed_params[fixed_params_to_index['mu']] =  1/4.2
    
def set_fixed_params(fixed_params, country, *, data_location='real_data'):
    k_active_db = pandas.read_csv(data_location+r'\kaverageall_locationsPLOSComp.csv')
    k_conf_db = pandas.read_csv(data_location+r'\kaveragehomePLOSComp.csv')
    
    set_home_size(fixed_params, country, 0)
    set_k_average_active(fixed_params, country, k_active_db)
    set_k_average_confined(fixed_params, country, k_conf_db)
    if 'mu' in fixed_params_to_index.keys():
        set_mu(fixed_params)

    if 'eta' in fixed_params_to_index.keys():
        set_eta(fixed_params)