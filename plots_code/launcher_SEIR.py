from model_seir.kernel import main, progress_bar
from model_seir.configuration import read_configuration, save_configuration, update_configuration, save_deaths_list
from model_seir.evolution import evolve
from model_seir.parameters_control import Params_Manager, param_to_index, fixed_params_to_index
import cupy as cp
import numpy as np
import matplotlib.pyplot as plt


SAVE_DATA = True
ANALYZE_DATA = False
ERASE_PREV_DATA = True

TOTAL_ITERATIONS = 1

country = "SEIR"

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