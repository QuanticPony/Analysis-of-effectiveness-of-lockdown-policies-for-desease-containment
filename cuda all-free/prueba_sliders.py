from tkinter.tix import MAX
import matplotlib.pyplot as plt

from simulation_functions import *

if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 140
    TOTAL_POPULATION = 42.7e6
    # N_SIMULATIONS = 100000
    # N_EXECUTIONS = 20

    fixed_params = cp.zeros(5, dtype=cp.float64)
    set_fixed_params(fixed_params, COUNTRY)
    
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
        
    s.add_slider('permability', valinit=0.04, valinterval=[0,0.14], valstep=0.001)
    s.add_slider('lambda', valinit=0.095, valinterval=[0.08,0.12], valstep=0.001)
    s.add_slider('IFR', valinit=0.00955, valinterval=[0.008,0.012], valstep=0.0001)
    s.add_slider('what', valinit=0.08, valinterval=[1/28,1/6], valstep=0.0001)
    s.add_slider('initial_i', valinit=0.75e-7, valinterval=[0, 1e-7], valstep=1e-9)
    s.add_slider('mu', valinit=0.3, valinterval=[0.1, 0.5], valstep=0.01)
        
    s.plot()
    plt.show()