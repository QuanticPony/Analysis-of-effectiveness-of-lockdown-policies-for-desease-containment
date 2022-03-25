from cProfile import label
import matplotlib.pyplot as plt
import numpy as np

from simulation_functions import smooth_deaths_list, prepare_deaths_list, prepare_p_active_list, save_p_active

types = ['retail_and_recreation_percent_change_from_baseline',#]
'grocery_and_pharmacy_percent_change_from_baseline',
'parks_percent_change_from_baseline',
'transit_stations_percent_change_from_baseline',
'workplaces_percent_change_from_baseline',
'residential_percent_change_from_baseline']

    
if __name__=='__main__':
    COUNTRY = 'United Kingdom of Great Britain'
    MAX_DAYS = 140
    
    fig, ax = plt.subplots()
    
    (deaths_list, first_deaths_list_day, deaths_list_lenght) =  prepare_deaths_list(COUNTRY)
    
    ax.plot(deaths_list.get(), color='black')
    for i, t in enumerate(types):
        
        p_active = prepare_p_active_list(COUNTRY, first_deaths_list_day, deaths_list_lenght, using=t).get()
        # p_active_ = np.tanh(2*p_active)**2
        ax.plot(smooth_deaths_list(p_active).get(), label=str(i))
        # ax.plot(smooth_deaths_list(p_active_).get(), label=str(i+1))
        
    # save_p_active(COUNTRY, p_active)

    ax.grid()
    ax.legend()
    plt.show()