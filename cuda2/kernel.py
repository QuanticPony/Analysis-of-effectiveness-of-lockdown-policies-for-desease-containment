from cProfile import label
import matplotlib.pyplot as plt
from analysis import *

from simulation_functions import *

if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 120
    TOTAL_POPULATION = 47.5e6
    N_SIMULATIONS = 2000000
    N_EXECUTIONS = 1
    VISUALIZE = False
    SAVE_DATA = True
    VISUALIZE_CORRELATIONS = False

    fixed_params = cp.zeros(len(fixed_params_to_index), dtype=cp.float64)
    set_fixed_params(fixed_params, COUNTRY)
    
    deaths_list = load_deaths_list(COUNTRY)
    deaths_list_smooth = smooth_deaths_list(deaths_list)
    p_active = load_p_active(COUNTRY)
    

    if SAVE_DATA:
        files = {}
        mode = 'a'
        for k,v in param_to_index.items():
            files.update({k: open(f"generated_data\data_by_country\{COUNTRY}\{k}.dat", mode)})
        files.update({'log_diff': open(f"generated_data\data_by_country\{COUNTRY}\log_diff.dat", mode)})



    for execution in range(N_EXECUTIONS):
        states = cp.zeros((7,N_SIMULATIONS), dtype=cp.float64)
        params = cp.zeros((len(param_to_index),N_SIMULATIONS), dtype=cp.float64)
        log_diff = cp.zeros((N_SIMULATIONS), dtype=cp.float64)

        set_params(params, size=N_SIMULATIONS)
        states[1] = 1-params[4]
        states[3] = params[4]
        
        
        evolve_gpu(params, fixed_params, states, p_active, deaths_list_smooth, log_diff, max_days=MAX_DAYS, total_poblation=TOTAL_POPULATION)
        
        best_params, best_log_diff = get_best_parameters(params, log_diff, 5)
        
        if SAVE_DATA:
            for i, l in enumerate(best_log_diff):
                if l<100:
                    for k,f in files.items():
                        if k=='log_diff':
                            f.write(str(best_log_diff[i]))
                            f.write('\n')
                        else:
                            f.write(str(best_params[param_to_index[k]][i]))
                            f.write('\n') 
                    
            #! Esto habría que quitarlo más adelante
        if execution==0:
            best_states = prepare_states(best_params)

            time = 0
            _5p = []
            _95p = []
            _median = []

            while time<MAX_DAYS+40:
                time+=1
                evolve(best_params, fixed_params, best_states, time, p_active)
                deaths = best_states[5]*TOTAL_POPULATION
                deaths.sort()
                _median.append(median(deaths).get())
                _5p.append(percentil(deaths, 5).get())
                _95p.append(percentil(deaths, 95).get())

            fig_, ax_ = plt.subplots()
            time_list =  range(MAX_DAYS+40)

            ax_.fill_between(time_list, _5p, _95p, alpha=0.2)
            ax_.plot(time_list, _median, '-.', color='purple', label='median')

            ax_.plot(time_list[:MAX_DAYS], deaths_list.get()[:MAX_DAYS], color='red', label='real data')
            ax_.plot(time_list[MAX_DAYS:MAX_DAYS+40], deaths_list.get()[MAX_DAYS:MAX_DAYS+40], '-.', color='red', label='real data')
            ax_.set_title('Deaths per day')
            ax_.legend()
            ax_.set_ylim([0, max(deaths_list[:MAX_DAYS+40])*1.1])
            fig_.savefig(f'images\images_by_country\{COUNTRY}\{execution}_bests.png')
            plt.close(fig_)
                
        
        if VISUALIZE:
            best_param = cp.zeros((len(param_to_index),3), dtype=cp.float64)
            for i in range(best_params.shape[0]):
                _copy = best_params[i].copy()
                _copy.sort()
                _median = median(_copy)
                _5p = percentil(_copy, 5)
                _95p = percentil(_copy, 95)
                best_param[i][0] = _5p
                best_param[i][1] = _median
                best_param[i][2] = _95p
                
            best_state = prepare_states(best_param)
            fig, ax = plot_percentiles(best_param, fixed_params, best_state, deaths_list_smooth, p_active, max_days=MAX_DAYS+40, total_population=TOTAL_POPULATION)
            fig.savefig(f'images\images_by_country\{COUNTRY}\{execution}_percentiles.png')
            plt.close(fig)
        
        if VISUALIZE_CORRELATIONS:
            correlations(best_params, 15)
            break
        
        if VISUALIZE:
            break