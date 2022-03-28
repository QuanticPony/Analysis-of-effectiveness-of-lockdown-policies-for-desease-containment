from numpy import percentile
from kernel import main
from configuration import generate_configuration, read_configuration, prepare_deaths_p_active, save_configuration

if __name__=='__main__':

    COUNTRY = 'Spain'
    SAVE_DATA = True
    ANALYZE_DATA = True
    ERASE_PREV_DATA = True
    SAVE_PERCENTAGE = 0.5

    # prepare_deaths_p_active(COUNTRY)
    configuration = read_configuration(COUNTRY)
    configuration_ref = configuration.copy()

    for i in range(0, 10):
        # generate_configuration(c)
        
        percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE, name=i)
        for k, v in percentiles.items():
            dist = v["max"] - v["min"]
            if k not in ["IFR", "what", "initial_i"]:
                configuration["params"][k]["min"] = max(v["min"] - dist/3, configuration_ref["params"][k]["min"])
                configuration["params"][k]["max"] = min(v["max"] + dist/3, configuration_ref["params"][k]["max"])
            if k=="initial_i":
                configuration["params"][k]["min"] = max(v["min"] * 0.9, configuration_ref["params"][k]["min"])
                configuration["params"][k]["max"] = min(v["max"] * 1.1, configuration_ref["params"][k]["max"])

    save_configuration(configuration)
        

    # for c in ['Italy', 'United Kingdom of Great Britain', 'Colombia', 'France']:
        # generate_configuration(c)
        # prepare_deaths_p_active(c)
        # configuration = read_configuration(c)
        # percentiles = main(configuration, SAVE_DATA, ANALYZE_DATA, ERASE_PREV_DATA, SAVE_PERCENTAGE)
        
