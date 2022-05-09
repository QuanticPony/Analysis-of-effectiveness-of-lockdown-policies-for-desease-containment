from cuda_with_launcher.kernel import main, progress_bar
from cuda_with_launcher.configuration import read_configuration, restart_lambda, restart_offset, restart_permeability, restart_what, save_configuration, get_all_countries, update_configuration

if __name__=='__main__':

    SAVE_DATA = True
    ANALYZE_DATA = True
    ERASE_PREV_DATA = True
    SAVE_PERCENTAGE = 0.1
    
    TOTAL_ITERATIONS = 8
    
    RESTART_PARAMS = True
    FINAL_IMAGE = False
    ONLY_ONE_IMAGE = False
    HALF_RE_PARAMETRIZATION = False
    
    all_countries = get_all_countries()
    all_countries = ["Morocco"]


    for i, c in enumerate(all_countries):
        # if not (i in range(25,47)):
        #     continue

        progress_bar(c, 0, 1, len=25)
        
        configuration_ref = read_configuration(c, sufix='', prefix='used/', v2=True)
        configuration_ref["simulation"]["n_simulations"] = 1300000
        configuration_ref["simulation"]["n_executions"] = 1
        configuration = configuration_ref.copy()

        if RESTART_PARAMS:
            restart_offset(configuration)
            restart_permeability(configuration)
            restart_lambda(configuration)
            restart_what(configuration)
            # configuration["params"]["initial_i"]["max"] = 0.1/configuration_ref["total_population"]

        
        if not ONLY_ONE_IMAGE:
            for i in range(TOTAL_ITERATIONS):
                progress_bar(c, i, TOTAL_ITERATIONS + (1 if FINAL_IMAGE else 0), len=25)

                percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=i, save_pictures= (i==TOTAL_ITERATIONS-1) )
                update_configuration(configuration, configuration_ref, percentiles)

                if i==TOTAL_ITERATIONS/2 and HALF_RE_PARAMETRIZATION:
                    ## Reinicio todos los parámetros después de haber más o menos ajustado initial_i
                    restart_offset(configuration)
                    restart_permeability(configuration)
                    restart_lambda(configuration)
                    restart_what(configuration)
            else: 
                if FINAL_IMAGE:
                    progress_bar(c, TOTAL_ITERATIONS,TOTAL_ITERATIONS + 1, len=25)
                else:
                    progress_bar(c, TOTAL_ITERATIONS,TOTAL_ITERATIONS, end='\n', len=25)
            
            save_configuration(configuration, sufix='', prefix='used/')
            
            if FINAL_IMAGE:
                #! quitar
                configuration["params"]["offset"]["min"] -= 4
                configuration["params"]["offset"]["max"] += 4

                configuration["params"]["permeability"]["min"] = max(0, configuration["params"]["permeability"]["min"] - 0.3)
                configuration["params"]["permeability"]["max"] = min(1, configuration["params"]["permeability"]["max"] + 0.3)

                configuration['simulation']["n_simulations"] = 2000000
                configuration["simulation"]["n_executions"] = 2
                main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name="final", save_pictures=True)
                progress_bar(c, TOTAL_ITERATIONS+1,TOTAL_ITERATIONS+1, end='\n', len=25)
            
            
        else:
            configuration['simulation']["n_simulations"] = 2000000
            configuration["simulation"]["n_executions"] = 2
            main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name="final", save_pictures=True)