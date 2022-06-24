import matplotlib.pyplot as plt

from .simulation_functions import *
from .configuration import *
from .parameters_control import *

if __name__=='__main__':
    
    COUNTRY = 'Colombia'
    MAX_DAYS = 180
    TOTAL_POPULATION = 50882891


    fixed_params = cp.zeros(5, dtype=cp.float64)
    
    configuration = read_configuration(COUNTRY, prefix='used/', sufix='')
    p_controller = Params_Manager(configuration)
    p_controller.set_fixed_params(fixed_params)
    
    deaths_list = load_deaths_list(COUNTRY)
    deaths_list_smooth = smooth_deaths_list(deaths_list)
    p_active = load_p_active(COUNTRY)
    # f1, a1 = plot_deaths(deaths_list)
    # f2, a2 = plot_p_active(p_active)

    
    s = Simulation(deaths_list_smooth.get(), p_active.get(), fixed_params.get(), MAX_DAYS, TOTAL_POPULATION)

    # s.add_slider('permability', valinit=0.0, valinterval=[0,1], valstep=0.01)
    # s.add_slider('lambda', valinit=0.38, valinterval=[0,0.7], valstep=0.01)
    # s.add_slider('IFR', valinit=0.002, valinterval=[0,0.008], valstep=0.0001)
    # s.add_slider('what', valinit=0.07, valinterval=[0,0.2], valstep=0.001)
    # s.add_slider('initial_i', valinit=1e-13, valinterval=[0, 0.001/TOTAL_POPULATION], valstep=0.00001/(TOTAL_POPULATION))
        
    for k in param_to_index:    
        s.add_slider(k, valinit=configuration['params'][k]['min'], 
                     valinterval=[configuration['params'][k]['min'],
                                  configuration['params'][k]['max']], 
                     valstep=(configuration['params'][k]['max'] -configuration['params'][k]['min'])/100)
        
    s.plot()
    plt.show()