import datetime
import json
import os

import cupy as cp
import matplotlib.pyplot as plt
import pandas


## Funciones específicas

def str_to_date(string, *, strange=False):
    _d = string.split('/')
    if strange:
        return datetime.date(int(_d[2])+2000, int(_d[0]), int(_d[1]))
    return datetime.date(int(_d[0]), int(_d[1]), int(_d[2]))


def date_to_str(date):
    return f"{date.year}-{date.month:>02d}-{date.day:>02d}"
    return date.strftime('%Y-%m-%d')


def prepare_deaths_list(requested_country):
    "Returns tuple: `(deaths_list, first_day_deaths_list, lenght_deaths_list)`."
    deaths_complete_db = pandas.read_csv(r'real_data\Deaths_worldwide_1Aug.csv')
    deaths_partial_db = deaths_complete_db[deaths_complete_db['Country']==requested_country]

    first_day_deaths_list = str_to_date(deaths_partial_db['Date'].values[0], strange=True)
    lenght_deaths_list = deaths_partial_db['Date'].size

    deaths_list = cp.zeros(lenght_deaths_list, dtype=cp.int32)
    for _country, date, _cumdeath, death in deaths_partial_db.values:
        deaths_list[(str_to_date(date, strange=True)-first_day_deaths_list).days] = death
    return (deaths_list, first_day_deaths_list, lenght_deaths_list)
    

def plot_deaths(deaths_list):
    fig,ax = plt.subplots()
    ax.plot(range(len(deaths_list)), deaths_list.get())
    ax.grid(True)
    return fig, ax
    

def smooth_deaths_list(deaths_list):
    deaths_list_smooth = cp.zeros(len(deaths_list), dtype=cp.float64)
    for i in range(len(deaths_list)):
        _zeros = 0
        _min = -3 if i > 3 else 0
        _max = 4 if len(deaths_list)-i > 3 else 1
        for j in range(_min,_max):
            if deaths_list[i+j] >= 0:
                deaths_list_smooth[i] += deaths_list[i+j]/(_max-_min)
            else:
                _zeros += 1
            if _zeros > 0:
                deaths_list_smooth[i] *= (_max-_min)/(_max-_min-_zeros)
    return deaths_list_smooth


def save_deaths_list(requested_country, deaths_list):
    cp.save(f"real_data/data_by_country/{requested_country}_deaths.npy", deaths_list)


def load_deaths_list(requested_country):
    return cp.load(f"real_data/data_by_country/{requested_country}_deaths.npy")


def prepare_p_active_list(requested_country, first_day_deaths_list, lenght_deaths_list, using='transit_stations_percent_change_from_baseline'):
    "Returns `p_array : cp.ndarray`."
    p_active_complete_db =  pandas.read_csv(r'real_data\reducedgoogledataset.csv',
        dtype = {'country_region_code':'str',
            'country_region':'str',
            'sub_region_1':'str',
            'sub_region_2':'str',
            'metro_area':'str',
            'iso3166_2_code':'str',
            'census_fips_code':'str',
            'retail_and_recreation_percent_change_from_baseline':'float32',
            'grocery_and_pharmacy_percent_change_from_baseline':'float32',
            'parks_percent_change_from_baseline':'float32',
            'transit_stations_percent_change_from_baseline':'float32',
            'workplaces_percent_change_from_baseline':'float32',
            'residential_percent_change_from_baseline':'float32'}
        )
        
    aux  = p_active_complete_db[p_active_complete_db['country_region']==requested_country]
    p_active_partial_db = aux[aux['sub_region_1'].isna()]
    del(aux)
    p_active = cp.ones(lenght_deaths_list, dtype=cp.float64)
    for day in range(lenght_deaths_list):
        p_value = p_active_partial_db[
            p_active_partial_db['date']==date_to_str(first_day_deaths_list+datetime.timedelta(day))
            ][using]
        if not p_value.empty:
        
            __p = float(p_value.values[0])
            if True:#__p < 0:  #! solución a valores positivos
                p_active[day] += float(p_value.values[0]) * 0.01
                
    return p_active


def plot_p_active(p_active):
    fig,ax = plt.subplots()
    ax.plot(range(len(p_active)), p_active.get())
    ax.grid(True)
    return fig, ax


def save_p_active(requested_country, p_active):
    cp.save(f"real_data/data_by_country/{requested_country}_p_active.npy", p_active)


def load_p_active(requested_country):
    return cp.load(f"real_data/data_by_country/{requested_country}_p_active.npy")



## Funciones más generales


def prepare_deaths_p_active(country: str, plot=False):
    (deaths_list, first_deaths_list_day, deaths_list_lenght) =  prepare_deaths_list(country)
    
    save_deaths_list(country, deaths_list)
    
    p_active = prepare_p_active_list(country, first_deaths_list_day, deaths_list_lenght, 
                          using='retail_and_recreation_percent_change_from_baseline')
    
    if plot:
        from simulation_functions import plot_deaths, plot_p_active
        f1, a1 = plot_deaths(deaths_list)
        f2, a2 = plot_p_active(p_active)
    
    save_deaths_list(country, deaths_list)
    save_p_active(country, p_active)


def generate_configuration(country: str, *, data_location='real_data'):
    k_active_db = pandas.read_csv(data_location+r'\kaverageall_locationsPLOSComp.csv')
    k_conf_db = pandas.read_csv(data_location+r'\kaveragehomePLOSComp.csv')

    conf = {
        "country" : country,
        "total_population" : 47.5e6,
        "max_days" : 110,

        "simulation" : { 
            "n_simulations" : 1000000,
            "n_executions" : 1,
        },

        "params" : {
            "offset" : {"min": -10, "max" : 10},
            "permeability" : {"min" : 0, "max" : 0.2},
            "lambda" : {"min" : 0.06, "max" : 0.16},
            "IFR" : {"min" : 0.008, "max" : 0.012},
            "what" : {"min" : 1/16, "max" : 1/6},
            "initial_i" : {"min" : 0, "max" : 1e-8},
        },

        "fixed_params" : {
            'home_size' : 2.5,
            'k_average_active' : float(k_active_db[k_active_db['Country']==country]['kaverage']),
            'k_average_confined' : float(k_conf_db[k_conf_db['Country']==country]['kaverage']),
            'mu' : 1/4.2,
            'eta' : 1/5.2,
        }
    }

    filename = f"configurations/{country}.json" 
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as fp:
        json.dump(conf, fp, indent=4)


def read_configuration(country: str, print_config=False):
    filename = f"configurations/{country}.json" 
    try:
        with open(filename, 'r') as fp:
            conf = json.load(fp)
            if print_config:
                print(conf)
    except Exception as e:
        generate_configuration(country)
        return read_configuration(country, print_config=print_config)
    return conf


def save_configuration(configuration):
    filename = f"configurations/{configuration['country']}_new.json" 
    with open(filename, 'w') as fp:
        json.dump(configuration, fp, indent=4)

        

def open_save_files(country: str, erase_prev=True) -> dict:
    """Open files needed for saving data generated. Returns dict with open files""" 
    from simulation_functions import param_to_index
    
    mode = 'w' if erase_prev else 'a'
    files = {}

    for k,v in param_to_index.items():
        filename = f"generated_data\data_by_country\{country}\{k}.dat" 
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        files.update({k: open(filename, mode)})
    files.update({'log_diff': open(f"generated_data\data_by_country\{country}\log_diff.dat", mode)})

    return files

def close_save_files(files: dict):
    for file in files.values():
        file.close()


if __name__=='__main__':
    COUNTRY = "Spain"
    prepare_deaths_p_active(COUNTRY)
    generate_configuration(COUNTRY)
