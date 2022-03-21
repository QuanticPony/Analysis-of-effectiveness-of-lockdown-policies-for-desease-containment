import matplotlib.pyplot as plt

from simulation_functions import *

if __name__=='__main__':
    COUNTRY = 'United Kingdom of Great Britain'
    
    (deaths_list, first_deaths_list_day, deaths_list_lenght) =  prepare_deaths_list(COUNTRY)
    
    save_deaths_list(COUNTRY, deaths_list)
    
    p_active = prepare_p_active_list(COUNTRY, first_deaths_list_day, deaths_list_lenght, 
                          using='retail_and_recreation_percent_change_from_baseline')
    
    f1, a1 = plot_deaths(deaths_list)
    f2, a2 = plot_p_active(p_active)
    
    # save_deaths_list(COUNTRY, deaths_list)
    save_p_active(COUNTRY, p_active)
    
    plt.show()