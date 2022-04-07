import pandas

from configuration import *


data_location = 'real_data/'
# deaths_db = pandas.read_csv(data_location + "Deaths_worldwide_1Aug.csv")
# countries_db = deaths_db["Country"].drop_duplicates()

population_db = pandas.read_csv(data_location + 'Population_worldwide.csv')
countries_db = population_db["name"]

for i, country in countries_db.iteritems():
    
    try:
        partial_db = population_db[population_db["name"]==country]
        # print(partial_db.head())
        population = float(partial_db["pop2020"])
        print(country + ' : ' + str(population))

        config = read_configuration(country)
        config["total_population"] = population
        save_configuration(config, sufix='')

    except Exception as e:
        print(e)
        print(f"Fallo en {country}")    