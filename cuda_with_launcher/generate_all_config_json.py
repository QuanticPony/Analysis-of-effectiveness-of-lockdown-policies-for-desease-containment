import pandas

from .configuration import *

if __name__=='__main__':
    data_location = 'real_data/'
    # deaths_db = pandas.read_csv(data_location + "Deaths_worldwide_1Aug.csv")
    # countries_db = deaths_db["Country"].drop_duplicates()

    population_db = pandas.read_csv(data_location + 'Population_worldwide.csv')
    # countries_db = population_db["name"]


    country_list = []
    with open("real_data/country_list.txt", "r") as country_list_file:
        for line in country_list_file:
            country_list.append(line.strip('\n'))



    for country in country_list:
        configuration = read_configuration(country, prefix='used/')
        
        partial_db = population_db[population_db["name"]==country]
        print(country)
        population = int(float(partial_db["pop2020"])*1000)
        
        configuration["first_day_deaths_list"] = "2020-01-22"
        configuration["min_days"] = 0
        configuration['total_population'] = population
        configuration["score"] = 0
        save_configuration(configuration, prefix='used/', sufix='')

    exit()
    no_country_list = []
    with open("real_data/no_country_list.txt", "r") as country_list_file:
        for line in country_list_file:
            no_country_list.append(line.strip('\n'))

    # print(country_list)
    # print(no_country_list)

    country_list_total = country_list + no_country_list

    try:
        for i, country in enumerate(country_list_total):
            try:
                with open(f"configurations/used/{country}.json", 'r') as file:
                    pass
                continue
            except FileNotFoundError:
                pass
            if country in country_list:
                continue #! quitar
                country_list.pop(country_list.index(country))
            if country in no_country_list:...
                # config = read_configuration(country)
                # save_configuration(config, prefix="no_used/", sufix='')
                # continue #!poner
            # partial_db = population_db[population_db["name"]==country]
            # # print(partial_db.head())
            # population = int(float(partial_db["pop2020"])*1000)
            # print(country + ' : ' + str(population))

            print(country)
            first_day_deaths_list = prepare_deaths_p_active(country, plot=True)

            # config = read_configuration(country)
            # # config["total_population"] = population
            # config["first_day_deaths_list"] = date_to_str(first_day_deaths_list)
            # # config["first_day_deaths_list"] = "2020-01-22"

            # try:
            #     min_days = int(input("Introducir mínimo:"))
            # except Exception as e:
            #     no_country_list.append(country)
            #     try:
            #         save_configuration(config, prefix="no_used/")
            #         os.remove(f"configurations/{country}.json")
            #     except Exception as e:
            #         print(f"fallo al borrar configurations/{country}.json")
            #     continue
            
            # country_list.append(country)

            # max_days = int(input("Dias máximos:"))

            # config["min_days"] = min_days
            # config["max_days"] = max_days
            # save_configuration(config, sufix='', prefix="used/")
            
        # with open("real_data/country_list.txt", "w") as country_list_file:
        #     country_list_file.write("\n".join(country_list))

        # with open("real_data/no_country_list.txt", "w") as country_list_file:
        #     country_list_file.write("\n".join(no_country_list))


    except KeyboardInterrupt as e:
        pass
        # with open("real_data/country_list.txt", "w") as country_list_file:
        #     country_list_file.write("\n".join(country_list))

        # with open("real_data/no_country_list.txt", "w") as country_list_file:
        #     country_list_file.write("\n".join(no_country_list))
