from numpy import percentile
import datetime
from cuda_with_launcher.configuration import get_all_countries
from kernel import main
from configuration import generate_configuration, read_configuration, prepare_deaths_p_active, save_configuration, date_to_str

if __name__=='__main__':

    # COUNTRY = 'Spain'
    SAVE_DATA = True
    ANALYZE_DATA = True
    ERASE_PREV_DATA = True
    SAVE_PERCENTAGE = 0.1

    # configuration = read_configuration(COUNTRY)
    # configuration_ref = configuration.copy()


    TOTAL_ITERATIONS = 10
    
    FINAL_IMAGE = False


    #! Todos los paises
    all_countries = get_all_countries()
    for c in all_countries:
        print(f"Comenzando {c}:")
        configuration_ref = read_configuration(c)

        configuration = configuration_ref.copy()
        configuration["simulation"]["n_simulations"] = 1000000
        configuration["simulation"]["n_executions"] = 1

        for i in range(TOTAL_ITERATIONS):
            print(f"\n\tIteración {i+1}/{TOTAL_ITERATIONS}")

            percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=i, save_pictures= (i==TOTAL_ITERATIONS-1) )
            for k, v in percentiles.items():
                distm = v["med"] - v["min"]
                distM = v["max"] - v["med"]
                
                if k in ["offset", "lambda", "permeability"]:
                    configuration["params"][k]["min"] = max(v["min"] - distm*(distm/distM), configuration_ref["params"][k]["min"])
                    configuration["params"][k]["max"] = min(v["max"] + distM*(distM/distm), configuration_ref["params"][k]["max"])
                if k=="initial_i":
                    configuration["params"][k]["min"] = max(v["min"] - distm*(distm/distM), configuration_ref["params"][k]["min"])
                    configuration["params"][k]["max"] = min(v["max"] + distM*(distM/distm), configuration_ref["params"][k]["max"])

        save_configuration(configuration, sufix='_new')
        print("\n\n")

    exit()

    #! Solo un país
    if not FINAL_IMAGE:
        for i in range(TOTAL_ITERATIONS):

            percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=i, save_pictures= (i==TOTAL_ITERATIONS-1) )
            for k, v in percentiles.items():
                dist = v["max"] - v["min"]
                if k not in ["IFR", "what", "initial_i"]:
                    configuration["params"][k]["min"] = max(v["min"] - dist/3, configuration_ref["params"][k]["min"])
                    configuration["params"][k]["max"] = min(v["max"] + dist/3, configuration_ref["params"][k]["max"])
                if k=="initial_i":
                    configuration["params"][k]["min"] = max(v["min"] - dist/2, configuration_ref["params"][k]["min"])
                    configuration["params"][k]["max"] = min(v["max"] + dist*2, configuration_ref["params"][k]["max"])

        save_configuration(configuration)
    
    else:
        configuration['simulation']["n_simulations"] *= 1
        main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=TOTAL_ITERATIONS, save_pictures=True)
        

    # for c in ['Italy', 'United Kingdom of Great Britain', 'Colombia', 'France', 'Poland', 'Spain', 'Germany', 'Portugal', 'Greece']:
        # generate_configuration(c)
        # first_day_deaths_list = prepare_deaths_p_active(c)
        # configuration = read_configuration(c)
        # configuration.update({'first_day_deaths_list': first_day_deaths_list.strftime(r"%Y-%m-%d")})
        # save_configuration(configuration)
        # percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE)
        
