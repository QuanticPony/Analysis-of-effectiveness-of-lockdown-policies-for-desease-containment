

from cuda_with_launcher_SEID.kernel import main, progress_bar
from cuda_with_launcher_SEID.configuration import read_configuration, save_configuration, update_configuration, save_deaths_list
from cuda_with_launcher_SEID.evolution import evolve
from cuda_with_launcher_SEID.parameters_control import Params_Manager, param_to_index, fixed_params_to_index
import cupy as cp
import numpy as np
import matplotlib.pyplot as plt


SAVE_DATA = True
ANALYZE_DATA = False
ERASE_PREV_DATA = True

TOTAL_ITERATIONS = 1

country = "SEID"

configuration_ref = read_configuration(country, sufix='', prefix='used/', v2=True)
configuration = configuration_ref.copy()

for i, (n_simulations, percentage) in enumerate(zip([1e4, 1e5, 1e6], [10, 1, 0.1])):
    configuration = configuration_ref.copy()
    configuration["simulation"]["n_simulations"] = int(n_simulations)
    progress_bar(country, i, 3, len=25)
    for i in range(TOTAL_ITERATIONS):
        
        percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, percentage, name=percentage, save_pictures= (i==TOTAL_ITERATIONS-1), files_sufix=f"_{percentage}")
        # update_configuration(configuration, configuration_ref, percentiles)

        save_configuration(configuration, sufix='_new_{percentage}', prefix='used/')

progress_bar(country, 1, 1, len=25)
exit()

from cuda_with_launcher_SEID.analysis import plot_the_plots

plot_the_plots('SEID')
exit()

from cuda_with_launcher_SEID.kernel import main, progress_bar
from cuda_with_launcher_SEID.configuration import read_configuration, save_configuration, update_configuration, save_deaths_list
from cuda_with_launcher_SEID.evolution import evolve
from cuda_with_launcher_SEID.parameters_control import Params_Manager, param_to_index, fixed_params_to_index
import cupy as cp
import numpy as np
import matplotlib.pyplot as plt


SAVE_DATA = True
ANALYZE_DATA = True
ERASE_PREV_DATA = True
SAVE_PERCENTAGE = 0.1

TOTAL_ITERATIONS = 2

RESTART_PARAMS = True
FINAL_IMAGE = True
ONLY_ONE_IMAGE = False

country = "SEID"


configuration_ref = read_configuration(country, sufix='', prefix='used/', v2=True)
configuration = configuration_ref.copy()
configuration["simulation"]["n_simulations"] = 2000000

if not ONLY_ONE_IMAGE:
    for i in range(TOTAL_ITERATIONS):
        progress_bar(country, i, TOTAL_ITERATIONS + (1 if FINAL_IMAGE else 0), len=25)

        percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=i, save_pictures= (i==TOTAL_ITERATIONS-1) )
        # update_configuration(configuration, configuration_ref, percentiles)

    else: 
        if FINAL_IMAGE:
            progress_bar(country, TOTAL_ITERATIONS,TOTAL_ITERATIONS + 1, len=25)
        else:
            progress_bar(country, TOTAL_ITERATIONS,TOTAL_ITERATIONS, end='\n', len=25)
    
    # save_configuration(configuration, sufix='', prefix='used/')
    
    if FINAL_IMAGE:
        #! quitar
        configuration['simulation']["n_simulations"] = 2000000
        configuration["simulation"]["n_executions"] = 2
        main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name="final", save_pictures=True)
        progress_bar(country, TOTAL_ITERATIONS+1,TOTAL_ITERATIONS+1, end='\n', len=25)
    
else:
    configuration['simulation']["n_simulations"] = 2000000
    configuration["simulation"]["n_executions"] = 2
    main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name="final", save_pictures=True)