import cupy as cp
import cupy.random as cprand

import pandas

N_SIMULATIONS = 5000000

###########################
## PRIORS
###########################

def set_permability(params, *, size=N_SIMULATIONS):
    #'permability'
    params[0]  = cprand.random(size, dtype=cp.float64)*0.2

def set_lambda(params, *, size=N_SIMULATIONS):
    #'lambda'
    params[1] = cprand.random(size, dtype=cp.float64) *0.6 + 0.1

def set_IFR(params, *, size=N_SIMULATIONS):
    #'IFR'
    params[2] = cprand.random(size, dtype=cp.float64)*0.055+0.0001

def set_what(params, *, size=N_SIMULATIONS): # xi
    #'what'
    params[3] = cprand.random(size, dtype=cp.float64)*(1/7-1/21)+ 1/21 #!TODO  * 1/7 y 1/21

def set_initial_i(params, *, size=N_SIMULATIONS):
    #'initial_i'
    params[4] = cprand.random(size, dtype=cp.float64)*3E-10
    
def set_params(params, *, size=N_SIMULATIONS):
    set_permability(params, size=size)
    set_lambda(params, size=size)
    set_IFR(params, size=size)
    set_what(params, size=size)
    set_initial_i(params, size=size)
    
#######################################################################################  
    
## FIXED PARAMETERS

def set_home_size(fixed_params, country, pd_dataframe):
    #'home_size'
    #! TODO: tamaño del hogar. Tengo que buscarlo? O tienen ya referencias?
    fixed_params[0] = 2.3

def set_k_average_active(fixed_params, country, pd_dataframe):
    #'k_average_active'
    fixed_params[1] = cp.float64(pd_dataframe[pd_dataframe['Country']==country]['kaverage'])

def set_k_average_confined(fixed_params, country, pd_dataframe):
    #'k_average_confined'
    fixed_params[2] = cp.float64(pd_dataframe[pd_dataframe['Country']==country]['kaverage'])

def set_eta(fixed_params):
    #'eta'
    fixed_params[3] = 1/5.2
        
def set_mu(fixed_params):
    #'mu'
    fixed_params[4] = 1/4.2
    
def set_fixed_params(fixed_params, country, *, data_location='real_data'):
    k_active_db = pandas.read_csv(data_location+r'\kaverageall_locationsPLOSComp.csv')
    k_conf_db = pandas.read_csv(data_location+r'\kaveragehomePLOSComp.csv')
    
    set_mu(fixed_params)
    set_eta(fixed_params)
    set_home_size(fixed_params, country, 0)
    set_k_average_active(fixed_params, country, k_active_db)
    set_k_average_confined(fixed_params, country, k_conf_db)