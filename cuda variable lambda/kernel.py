import matplotlib.pyplot as plt
import os

from set_parameters import *
from simulation_functions import *
from analysis import *

if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 120
    TOTAL_POPULATION = 47.5e6
    # TOTAL_POPULATION = 51.8e6
    N_SIMULATIONS = 3000000
    N_EXECUTIONS = 1
    VISUALIZE = False
    SAVE_DATA = True
    ANALYZE_DATA = True
    
    ERASE_PREV_DATA = True
    
    N_LAMBDAS = 3

    fixed_params = cp.zeros(len(fixed_params_to_index), dtype=cp.float64)
    set_fixed_params(fixed_params, COUNTRY)
    
    deaths_list = load_deaths_list(COUNTRY)
    # deaths_list = cp.append(cp.zeros(40), deaths_list_)
    deaths_list_smooth = smooth_deaths_list(deaths_list)
    p_active = smooth_deaths_list(load_p_active(COUNTRY))
    

    if SAVE_DATA:
        files = {}
        mode = 'a' if not ERASE_PREV_DATA else 'w'
        for k,v in param_to_index.items():
            filename = f"generated_data\data_by_country\{COUNTRY}\{k}.dat" 
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            files.update({k: open(filename, mode)})
        files.update({'log_diff': open(f"generated_data\data_by_country\{COUNTRY}\log_diff.dat", mode)})
        files.update({'lambdas': open(f"generated_data\data_by_country\{COUNTRY}\lambdas.dat", mode)})



    for execution in range(N_EXECUTIONS):
        states = cp.zeros((7,N_SIMULATIONS), dtype=cp.float64)
        params = cp.zeros((len(param_to_index),N_SIMULATIONS), dtype=cp.float64)
        params_lambda = cp.zeros((N_LAMBDAS, N_SIMULATIONS), dtype=cp.float64)
        log_diff = cp.zeros((N_SIMULATIONS), dtype=cp.float64)

        set_params(params, params_lambda, size=N_SIMULATIONS)
        states[1] = 1- params [param_to_index['initial_i']]
        states[3] = params [param_to_index['initial_i']]
        
        
        evolve_gpu(params, fixed_params, states, p_active, deaths_list_smooth, log_diff, params_lambda=params_lambda, max_days=MAX_DAYS, total_poblation=TOTAL_POPULATION)
        
        best_params, best_log_diff, best_params_lambda = get_best_parameters(params, log_diff, 0.1, params_lambda)
        
        if SAVE_DATA:
            for i, l in enumerate(best_log_diff):
                # if l<100:
                for k,f in files.items():
                    if k=='log_diff':
                        f.write(str(best_log_diff[i]))
                        f.write('\n')
                        continue
                    if k=='lambda':
                        continue
                    if k=='lambdas':
                        f.write('\t'.join(map(str, best_params_lambda[:,i])))
                        f.write('\n')
                    else:
                        f.write(str(best_params[param_to_index[k]][i]))
                        f.write('\n') 
                    
            #! Esto habría que quitarlo más adelante
            if execution==0:
                best_states = prepare_states(best_params, TOTAL_POPULATION)

                _5p = []
                _95p = []
                _median = []
                
                NEW_MAX_DAYS= MAX_DAYS+40
                deaths = cp.zeros([NEW_MAX_DAYS, best_params.shape[1]])
                _range = cp.arange(0, best_params.shape[1]) 
                
                # _time = cp.zeros(best_params.shape[1], dtype=cp.int32)
                # _offset = cp.zeros(best_params.shape[1], dtype=cp.int32)
                # _time[:] = best_params[param_to_index['initial_i']][:]
                # _offset[:] = best_params[param_to_index['offset']][:]
                
                recovered_array = cp.zeros(best_params.shape[1])
                last_infected = cp.zeros(best_params.shape[1])
                reproductive_number = cp.zeros((NEW_MAX_DAYS,best_params.shape[1]))
                
                # p_active_threshold_for_lambda = 0.5
                # _frst_wave_passed = False
                _time = 0
                # while (_time<NEW_MAX_DAYS).any():
                while _time<NEW_MAX_DAYS:
                    _index = int(_time*params_lambda.shape[0]/MAX_DAYS)
                    # if p_active[_index * (_index>=0)]<p_active_threshold_for_lambda or _frst_wave_passed:
                    #     params[param_to_index['lambda']] = params_lambda[1]
                    #     _frst_wave_passed = True
                    # else:
                    #     params[param_to_index['lambda']] = params_lambda[0]
                    # best_params[param_to_index['lambda']] = best_params_lambda[_index if _index<best_params_lambda.shape[0] else best_params_lambda.shape[0]-1]
                    best_params[param_to_index['lambda']] = best_params_lambda[1*(_time>LAMBDA_THRESHOLD) + 1*(_time>LAMBDA_THRESHOLD_2)]
                        
                    index = 0 + _time
                    
                    last_infected[:] = best_states[3]
                    
                    evolve(best_params, fixed_params, best_states, p_active[0+index * (index>=0)])
                    reproductive_number[_time] = (best_states[3] - last_infected)/(last_infected) / fixed_params[fixed_params_to_index['mu']]
                    
                    deaths[_time * (_time>=0) * (NEW_MAX_DAYS>_time),_range] += best_states[5,_range]*TOTAL_POPULATION * (_time<NEW_MAX_DAYS) * (_time>=0)
                    # deaths[__time, _range] += best_states[5,_range]*TOTAL_POPULATION
                    recovered_array[_range] += best_states[6, _range] * (_time==113)
                    
                    _time += 1
                    # __time += 1
                    

                fig_rec, ax_rec = plt.subplots()
                ax_rec.hist(recovered_array.get()*100, 15)
                ax_rec.set_title('Recovered % at May 15 2020')
                ax_rec.set_ylabel('Relative frecuency')
                ax_rec.set_xlabel('Recovered %')
                fig_rec.savefig(f'images/images_by_country/{COUNTRY}/recovered_histogram.png')
                plt.close(fig_rec)
                    
                deaths[0,:] = 0

                time = 0
                while time<NEW_MAX_DAYS:
                    deaths_ = deaths[time, _range].copy()
                    deaths_.sort()
                    _median.append(median(deaths_).get())
                    _5p.append(percentil(deaths_, 5).get())
                    _95p.append(percentil(deaths_, 95).get())
                    time+=1

                fig_, ax_ = plt.subplots()

                time_list =  np.arange(NEW_MAX_DAYS)

                

                ax_.plot(time_list[:MAX_DAYS], deaths_list.get()[0:MAX_DAYS], '-.', color='red', label='real data')
                ax_.plot(time_list[MAX_DAYS:NEW_MAX_DAYS], deaths_list.get()[MAX_DAYS:NEW_MAX_DAYS], '*', color='red')
                ax_.plot(time_list[:MAX_DAYS], deaths_list_smooth.get()[0:MAX_DAYS], color='black', label='smooth')
                ax_.plot(time_list[MAX_DAYS:NEW_MAX_DAYS], deaths_list_smooth.get()[MAX_DAYS:NEW_MAX_DAYS], '-.', color='black')
                
                ax_.fill_between(time_list, _5p, _95p, alpha=0.3)
                ax_.plot(time_list, _median, '-.', color='purple', label='median')
                
                # ax_p_active = ax_.twinx()
                # ax_p_active.plot(time_list[:NEW_MAX_DAYS], p_active.get()[:NEW_MAX_DAYS], '-.', color='green', label='p_active google')
                # ax_p_active.plot(time_list[:NEW_MAX_DAYS]-6, p_active.get()[:NEW_MAX_DAYS], '-.', color='orange', label='p_active offset')
                # ax_p_active.set_ylabel('Movility reduction')
                # ax_p_active.legend(loc='center left')
                # ax_p_active.set_ylim([0,1])
                
                ax_.set_xlabel('Days after 22 January 2020')
                ax_.set_ylabel('Daily fatalities')
                ax_.set_title('Fatalities per day')
                
                ax_.legend()
                ax_.set_xlim(xmin=0)
                ax_.set_ylim([0,max(deaths_list.get()[:NEW_MAX_DAYS])*1.1])
                fig_.savefig(f'images\images_by_country\{COUNTRY}\{execution}_bests.png')
                plt.close(fig_)
                
                
                
                # R0
                fig_reprod, ax_reprod = plt.subplots()
                _5p = []
                _95p = []
                _median = []
                time = 0
                while time<NEW_MAX_DAYS:
                    rp_ = reproductive_number[time, _range].copy()
                    rp_.sort()
                    _median.append(median(rp_).get())
                    _5p.append(percentil(rp_, 5).get())
                    _95p.append(percentil(rp_, 95).get())
                    time+=1
                
                ax_reprod.fill_between(time_list[1:], _5p[1:], _95p[1:], alpha=0.3)
                ax_reprod.plot(time_list[1:], _median[1:], '-.', color='purple', label='median')
                
                ax_reprod.set_ylabel('Reproductive number')
                ax_reprod.set_xlabel('Days after 22 January 2020')
                fig_reprod.savefig(f'images/images_by_country/{COUNTRY}/reproductive_number.png')
                plt.close(fig_reprod)
                
        
        # if VISUALIZE:
        #     print(best_log_diff[0], best_log_diff[1])

            
        #     best_states = prepare_states(best_params, TOTAL_POPULATION)
        #     fig_, ax_ = plot_states(best_params, fixed_params, best_states, deaths_list, p_active, max_days=MAX_DAYS+40, total_population=TOTAL_POPULATION)
        #     fig_.savefig(f'images\images_by_country\{COUNTRY}\{execution}_bests.png')
        #     plt.close(fig_)

        if VISUALIZE:
            break
        
    if ANALYZE_DATA:
        if SAVE_DATA:
            for file in files.values():
                file.close()
        # correlations(best_params, 8)
        plot_the_plots(COUNTRY, MAX_DAYS)
            
        
    if SAVE_DATA:
        for file in files.values():
            file.close()
      
