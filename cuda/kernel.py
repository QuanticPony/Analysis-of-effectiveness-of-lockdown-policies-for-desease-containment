from cProfile import label
import matplotlib.pyplot as plt

from simulation_functions import *

if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 110
    TOTAL_POPULATION = 42.7e6
    N_SIMULATIONS = 500000
    N_EXECUTIONS = 20
    VISUALIZE = False
    SAVE_DATA = True

    fixed_params = cp.zeros(5, dtype=cp.float64)
    set_fixed_params(fixed_params, COUNTRY)
    
    deaths_list = load_deaths_list(COUNTRY)
    deaths_list_smooth = smooth_deaths_list(deaths_list)
    p_active = load_p_active(COUNTRY)
    
    
    if VISUALIZE:
        f1, a1 = plot_deaths(deaths_list)
        a1.plot(range(len(deaths_list_smooth)), deaths_list_smooth.get(), '-', color='red', label='7 day average')
        a1.legend()
        f2, a2 = plot_p_active(p_active)
        saved_params = cp.zeros((5,N_EXECUTIONS*6), dtype=cp.float64)
        saved_log_diff = cp.zeros((N_EXECUTIONS*6), dtype=cp.float64)
    
    if SAVE_DATA:
        files = {}
        mode = 'a'
        for k,v in param_to_index.items():
            files.update({k: open(f"generated_data\data_by_country\{COUNTRY}\{k}.dat", mode)})

    for execution in range(N_EXECUTIONS):
        states = cp.zeros((7,N_SIMULATIONS), dtype=cp.float64)
        params = cp.zeros((5,N_SIMULATIONS), dtype=cp.float64)
        log_diff = cp.zeros((N_SIMULATIONS), dtype=cp.float64)

        set_params(params, size=N_SIMULATIONS)
        states[1] = 1-params[4]
        states[3] = params[4]
        
        
        evolve_gpu(params, fixed_params, states, p_active, deaths_list_smooth, log_diff, max_days=MAX_DAYS, total_poblation=TOTAL_POPULATION)
        
        best_params, best_log_diff = get_best_parameters(params, log_diff, 0.1)
        
        
        # saved_params[:,execution*6:execution*6+6] = best_params[:,:6]
        # saved_log_diff[execution*6:execution*6+6] = best_log_diff[:6]
        
        if SAVE_DATA:
            for k,f in files.items():
                f.write('\n'.join(str(p) for p in best_params[param_to_index[k]].get()))
                f.write('\n')
        
        if VISUALIZE:
            best_states = prepare_states(best_params)
            fig, ax = plot_states(best_params, fixed_params, best_states, deaths_list_smooth, p_active, max_days=MAX_DAYS+40, total_population=TOTAL_POPULATION)
        
            plt.show()
    


    # best_params, best_log_diff = get_best_parameters(saved_params, saved_log_diff, 1)
    # fig, ax = plot_states(best_params, fixed_params, best_states, deaths_list, p_active, max_days=MAX_DAYS, total_population=TOTAL_POPULATION) 
    # plt.show()