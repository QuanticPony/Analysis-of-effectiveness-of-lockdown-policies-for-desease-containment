from .configuration import *
from .parameters_control import *
from .simulation_functions import *
from .plots_funtions import *
from .analysis import *

def progress_bar(prefix, progress, total, *, sufix="", end='\r', len=10):
    per = len * progress/float(total)
    print(f"\r{prefix} -> ||{'▮'*int(per) + '▯'*(len-int(per))} ||{per*100/len:.2f}%  {sufix}", end=end)


def main(configuration, save_data: bool, analyze_data: bool, erase_prev_data: bool, save_percentage: float, name="", save_pictures=False):

    ## Leer configuracion y abrir ficheros de guardado de datos
    country = configuration["country"]
    if save_data:
        files = open_save_files(country, erase_prev=erase_prev_data)

    

    ## Crear el generador de parametros
    parameters_manager = Params_Manager(configuration)

    fixed_params = cp.zeros(len(fixed_params_to_index), dtype=cp.float64)
    parameters_manager.set_fixed_params(fixed_params)

    _n_simulations = configuration["simulation"]["n_simulations"]
    params = cp.zeros( (len(param_to_index),_n_simulations) , dtype=cp.float64)
    log_diff = cp.zeros(_n_simulations, dtype=cp.float64)
    


    ## Cargar muertes y p_active
    deaths_list = load_deaths_list(country)
    deaths_list_smooth = smooth_deaths_list(deaths_list)
    p_active = smooth_deaths_list(load_p_active(country))



    ## Bucle principal
    for execution in range(configuration["simulation"]["n_executions"]):

        ## Preparar ejecución
        log_diff[:] = 0
        parameters_manager.set_params(params)
        states = prepare_states(params, configuration["total_population"])

        ## Simular estados
        evolve_gpu(params, fixed_params, states, p_active, deaths_list_smooth, log_diff, configuration)
        
        ## Buscar mejores simulaciones
        best_params, best_log_diff = get_best_parameters(params, log_diff, save_percentage)
        

        
        ## Graficar mejores simulaciones
        if execution==0:
            recovered_array = plot_states(best_params, fixed_params, deaths_list, deaths_list_smooth, p_active, configuration, name=name)

        ## Guardar datos generados
        if save_data:
            parameters_manager.save_parameters(files, best_params, best_log_diff, recovered_array.get())
                    

    ## Cerrar archivos
    if save_data:
        close_save_files(files)

    ## Histogramas y correlaciones
    if analyze_data:
        return plot_the_plots(country, save_pictures=save_pictures)