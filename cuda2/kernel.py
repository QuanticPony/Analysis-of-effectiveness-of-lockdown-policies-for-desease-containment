import matplotlib.pyplot as plt
from analysis import *

from simulation_functions import *

if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 110
    TOTAL_POPULATION = 42.7e6
    N_SIMULATIONS = 1000000
    N_EXECUTIONS = 5
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
        
        best_params, best_log_diff = get_best_parameters(params, log_diff, 0.1)
        
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
                fig_, ax_ = plot_states(best_params, fixed_params, best_states, deaths_list_smooth, p_active, max_days=MAX_DAYS+40, total_population=TOTAL_POPULATION)
                fig_.savefig(f'images\images_by_country\{COUNTRY}\{execution}_bests.png')
        
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
            
            # for k,i in param_to_index.items():
            #     print(f"<{k}> = {(cp.mean(best_param[i])+best_param[i])/2} ∓ {np.sqrt(cp.var(best_params[i]))}")
            print(best_log_diff[0], best_log_diff[1])
            
            best_states = prepare_states(best_params)
            fig_, ax_ = plot_states(best_params, fixed_params, best_states, deaths_list, p_active, max_days=MAX_DAYS+40, total_population=TOTAL_POPULATION)
            fig_.savefig(f'images\images_by_country\{COUNTRY}\{execution}_bests.png')
            
            
            for k,i in param_to_index.items():
                fig, ax = plt.subplots()
                
                ax.hist(params[i].get(), 30, density=True)
                ax.hist(best_params[i].get(), 30, density=True)#, weights=1/best_log_diff.get())
                y_min, y_max = ax.get_ylim()
                ax.vlines(best_param[i,0].get(), ymin=y_min, ymax=y_max, color='red')
                ax.vlines(best_param[i,1].get(), ymin=y_min, ymax=y_max, color='orange')
                ax.vlines(best_param[i,2].get(), ymin=y_min, ymax=y_max, color='purple')
                ax.set_title(k.capitalize())

            # plt.show()
        
          
        
        if VISUALIZE_CORRELATIONS:
            correlations(best_params, 15)
            break
        
        if VISUALIZE:
            break