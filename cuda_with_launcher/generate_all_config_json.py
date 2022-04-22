import pandas

from configuration import *


data_location = 'real_data/'
deaths_db = pandas.read_csv(data_location + "Deaths_worldwide_1Aug.csv")
countries_db = deaths_db["Country"].drop_duplicates()

population_db = pandas.read_csv(data_location + 'Population_worldwide.csv')
# countries_db = population_db["name"]


country_list = []
with open("real_data/country_list.txt", "r") as country_list_file:
    for line in country_list_file:
        country_list.append(line.strip('\n'))

no_country_list = []
with open("real_data/no_country_list.txt", "r") as country_list_file:
    for line in country_list_file:
        no_country_list.append(line.strip('\n'))

print(country_list)
print(no_country_list)

try:
    for i, country in countries_db.iteritems():
        if country in country_list:
            continue
        if country in no_country_list:
            continue
        partial_db = population_db[population_db["name"]==country]
        # print(partial_db.head())
        population = int(float(partial_db["pop2020"])*1000)
        print(country + ' : ' + str(population))

        first_day_deaths_list = prepare_deaths_p_active(country, plot=True)

        config = read_configuration(country)
        config["total_population"] = population
        config["first_day_deaths_list"] = date_to_str(first_day_deaths_list)
        # config["first_day_deaths_list"] = "2020-01-22"

        try:
            min_days = int(input("Introducir mínimo:"))
        except Exception as e:
            no_country_list.append(country)
            try:
                os.remove(f"configurations/{country}.json")
            except Exception as e:
                print(f"fallo al borrar configurations/{country}.json")
            continue
        
        country_list.append(country)

        max_days = int(input("Dias máximos:"))

        config["min_days"] = min_days
        config["max_days"] = max_days
        save_configuration(config, sufix='')


except KeyboardInterrupt as e:
    with open("real_data/country_list.txt", "w") as country_list_file:
        country_list_file.writelines([c for c in country_list])

    with open("real_data/no_country_list.txt", "w") as country_list_file:
        country_list_file.writelines([c for c in country_list])
