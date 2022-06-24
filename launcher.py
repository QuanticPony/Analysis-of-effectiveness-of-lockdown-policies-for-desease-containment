from model.analysis import plot_the_plots
from model.kernel import main, progress_bar
from model.configuration import read_configuration, restart_lambda, restart_offset, restart_permeability, restart_what, save_configuration, get_all_countries, update_configuration, prepare_deaths_p_active

if __name__=='__main__':

    SAVE_DATA = True
    ANALYZE_DATA = True
    ERASE_PREV_DATA = True
    SAVE_PERCENTAGE = 0.05
    
    TOTAL_ITERATIONS = 6
    
    RESTART_PARAMS = True
    
    ONLY_ONE_IMAGE = False
    HALF_RE_PARAMETRIZATION = False

    PHOTO_IN_LAST_ITERATION = False
    FINAL_IMAGE = True

    UPDATE_CONFIGURATION = True
    
    all_countries = get_all_countries()

    # Sufijo añadido al final del nombre de cada país para no sobreescribir configuraciones.
    special_name = '_final_2'


    for i, c in enumerate(all_countries):
        progress_bar(c, 0, 1, len=25)

        try:
            configuration_ref = read_configuration(c, sufix=special_name, prefix='used/', v2=True)
            configuration_ref["simulation"]["n_simulations"] = 1300000
            configuration_ref["simulation"]["n_executions"] = 1
            configuration = configuration_ref.copy()

            if RESTART_PARAMS:
                # Reiniciar desfase en fallecidos
                # restart_offset(configuration)
                restart_permeability(configuration)
                restart_lambda(configuration)
                restart_what(configuration)
                # Reiniciar infectados iniciales.
                # configuration["params"]["initial_i"]["max"] = 0.1/configuration_ref["total_population"]

            
            # Para foto final.
            if not ONLY_ONE_IMAGE:
                configuration['simulation']["n_simulations"] = 3000000
                configuration["simulation"]["n_executions"] = 2

                configuration["params"]["offset"]["min"] = configuration["params"]["offset"]["min"] - 1
                configuration["params"]["offset"]["max"] = configuration["params"]["offset"]["max"] + 1
                main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name="final", save_pictures=True)

            # Para ajustar con ABC.
            else:
                for i in range(TOTAL_ITERATIONS):
                    progress_bar(c, i, TOTAL_ITERATIONS + (1 if FINAL_IMAGE else 0), len=25)

                    percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=f"{i}{special_name}", save_pictures= ((i==TOTAL_ITERATIONS-1) and PHOTO_IN_LAST_ITERATION))
                    update_configuration(configuration, configuration_ref, percentiles)

                    if i==TOTAL_ITERATIONS/2 and HALF_RE_PARAMETRIZATION:
                        # restart_offset(configuration)
                        restart_permeability(configuration)
                        restart_lambda(configuration)
                        restart_what(configuration)
                else: 
                    if FINAL_IMAGE:
                        progress_bar(c, TOTAL_ITERATIONS,TOTAL_ITERATIONS + 1, len=25)
                    else:
                        progress_bar(c, TOTAL_ITERATIONS,TOTAL_ITERATIONS, end='\n', len=25)
                


                # Actualizar archivo de configuraciones.
                if UPDATE_CONFIGURATION:
                    save_configuration(configuration, sufix=special_name+"_2", prefix='used/')
                

                # Foto final.
                if FINAL_IMAGE:
                    # configuration["params"]["offset"]["min"] = percentiles["offset"]["med"]-1
                    # configuration["params"]["offset"]["max"] = percentiles["offset"]["med"]+1

                    # configuration["params"]["permeability"]["min"] = max(0, configuration["params"]["permeability"]["min"] - 0.3)
                    # configuration["params"]["permeability"]["max"] = min(1, configuration["params"]["permeability"]["max"] + 0.3)

                    configuration['simulation']["n_simulations"] = 2000000
                    configuration["simulation"]["n_executions"] = 1
                    main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name="final", save_pictures=True)
                    progress_bar(c, TOTAL_ITERATIONS+1,TOTAL_ITERATIONS+1, end='\n', len=25)
                

        except Exception as e:
            print(f"Problema con {c}: {e}")
            continue