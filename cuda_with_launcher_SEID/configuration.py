import datetime
import json
import os

import cupy as cp
import matplotlib.pyplot as plt
import pandas

## Funciones específicas

def str_to_date(string, *, strange=False, v2=False):
    if v2:
        return datetime.date.fromisoformat(string)
    _d = string.split('/')

    if strange:
        return datetime.date(int(_d[2])+2000, int(_d[0]), int(_d[1]))
    return datetime.date(int(_d[0]), int(_d[1]), int(_d[2]))


def date_to_str(date):
    return f"{date.year}-{date.month:>02d}-{date.day:>02d}"
    return date.strftime('%Y-%m-%d')


def date_to_spanish(date):
    month = {
        'Jan': 'Ene',
        'Feb': 'Feb',
        'Mar': 'Mar',
        'Apr': 'Abr',
        'May': 'May',
        'Jun': 'Jun',
        'Jul': 'Jul',
        'Aug': 'Ago',
        'Sep': 'Sep',
        'Oct': 'Oct',
        'Nov': 'Nov',
        'Dec': 'Dic',
    }
    a,b = date.split()
    return '\n'.join([month[a],b])


def prepare_deaths_list(requested_country, v2=False):
    "Returns tuple: `(deaths_list, first_day_deaths_list, lenght_deaths_list)`."
    deaths_complete_db = pandas.read_csv(f'./real_data/Deaths_worldwide_1Aug{"_v2" if v2 else ""}.csv')
    deaths_partial_db = deaths_complete_db[deaths_complete_db['Country']==requested_country]
    
    DATE = "Date" if not v2 else "Date_reported"

    first_day_deaths_list = str_to_date(deaths_partial_db[DATE].values[0], strange=True, v2=v2)
    lenght_deaths_list = deaths_partial_db[DATE].size

    deaths_list = cp.zeros(lenght_deaths_list, dtype=cp.int32)
    if not v2:
        for _country, date, _cumdeath, death in deaths_partial_db.values:
            deaths_list[(str_to_date(date, strange=True, v2=v2)-first_day_deaths_list).days] = death
    else:
        for date, _country_code, _country, _WHO_region, _New_cases, _Cumulative_cases, death, _Cumulative_deaths in deaths_partial_db.values:
            deaths_list[(str_to_date(date, strange=True, v2=v2)-first_day_deaths_list).days] = death
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
            if __p < 0:
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


def prepare_deaths_p_active(country: str, plot=False, v2=False):
    (deaths_list, first_deaths_list_day, deaths_list_lenght) =  prepare_deaths_list(country, v2=v2)
    
    save_deaths_list(country, deaths_list)
    
    p_active = prepare_p_active_list(country, first_deaths_list_day, deaths_list_lenght, 
                          using='retail_and_recreation_percent_change_from_baseline')
    
    if plot:
        f1, a1 = plot_deaths(deaths_list)
        f2, a2 = plot_p_active(p_active)
        plt.show()
        
        plt.close(f1)
        plt.close(f2)
    
    save_deaths_list(country, deaths_list)
    save_p_active(country, p_active)
    return first_deaths_list_day


def generate_configuration(country: str, *, data_location='real_data', sufix='_ref', prefix=''):
    if country in ["Venezuela (Bolivarian Republic "]:
        return False

    k_active_db = pandas.read_csv(data_location+r'\kaverageall_locationsPLOSComp.csv')
    k_conf_db = pandas.read_csv(data_location+r'\kaveragehomePLOSComp.csv')
    # population_db = pandas.read_csv(data_location+r'\Population_worldwide.csv')
    # population = float(population_db[population_db['Country']==country]['Population'])

    conf = {
        "country" : country,
        "total_population" : 47.5e6,
        "max_days" : 110,

        "simulation" : { 
            "n_simulations" : 1000000,
            "n_executions" : 1,
        },

        "params" : {
            "offset" : {"min": -20, "max" : 20},
            "permeability" : {"min" : 0, "max" : 1},
            "lambda" : {"min" : 0.05, "max" : 0.30},
            "IFR" : {"min" : 0.007, "max" : 0.013},
            "what" : {"min" : 1/16, "max" : 1/6},
            "initial_i" : {"min" : 0, "max" : 1e-6},
        },

        "fixed_params" : {
            'home_size' : 2.5,
            'k_average_active' : float(k_active_db[k_active_db['Country']==country]['kaverage']),
            'k_average_confined' : float(k_conf_db[k_conf_db['Country']==country]['kaverage']),
            'mu' : 1/4.2,
            'eta' : 1/5.2,
        },
        "first_day_deaths_list": "2020-01-22",
        "min_days": 0
    }

    filename = f"configurations/{prefix}{country}{sufix}.json" 
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as fp:
        json.dump(conf, fp, indent=4)
    return True


def read_configuration(country: str, print_config=False, sufix='_ref', prefix='', v2=False):
    filename = f"configurations/{prefix}{country}{sufix}.json" 
    try:
        with open(filename, 'r') as fp:
            conf = json.load(fp)
            if print_config:
                print(conf)
    except Exception as e:
        prepare_deaths_p_active(country, plot=False, v2=v2)
        f = generate_configuration(country, sufix='_ref', prefix='')
        if f:
            return read_configuration(country, print_config=print_config)
        return
    return conf


def save_configuration(configuration, sufix='_new', prefix=''):
    filename = f"configurations/{prefix}{configuration['country']}{sufix}.json" 
    with open(filename, 'w') as fp:
        json.dump(configuration, fp, indent=4)

        

def open_save_files(country: str, *, erase_prev=True, mode=None, sufix='') -> dict:
    """Open files needed for saving data generated. Returns dict with open files""" 
    from .simulation_functions import param_to_index
    
    _mode = 'w' if erase_prev else 'a'
    if mode is not None:
        _mode = mode
    files = {}

    for k,v in param_to_index.items():
        filename = f"generated_data/data_by_country/{country}/{k}{sufix}.dat" 
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        files.update({k: open(filename, _mode)})
    files.update({'log_diff': open(f"generated_data/data_by_country/{country}/log_diff{sufix}.dat", _mode)})
    files.update({'recovered': open(f"generated_data/data_by_country/{country}/recovered{sufix}.dat", _mode)})

    return files

def close_save_files(files: dict):
    for file in files.values():
        file.close()

def get_all_countries(data_location='real_data/'):
    countries_list = []
    with open("real_data/country_list.txt", 'r') as file:
        for line in file:
            countries_list.append(line.strip('\n'))
    return countries_list



def restart_permeability(config):
    config["params"]["permeability"]["min"] = 0
    config["params"]["permeability"]["max"] = 1

def restart_lambda(config):
    config["params"]["lambda"]["min"] = 0.01
    config["params"]["lambda"]["max"] = 0.20


def restart_offset(config):
    config["params"]["offset"]["min"] = 0
    config["params"]["offset"]["max"] = 20
    
def restart_what(config):
    config["params"]["what"]["min"] = 0.0625
    config["params"]["what"]["max"] = 0.16666666666666666

def update_configuration(config, config_ref, percentiles):
    for k, v in percentiles.items():
        distm = v["med"] - v["min"]
        distM = v["max"] - v["med"]
        dist = (distm + distM)/2
        
        if k in ['lambda', 'IFR', 'what']:
            config["params"][k]["min"] = max(v["min"] - dist*(distM/distm), config_ref["params"][k]["min"])
            config["params"][k]["max"] = min(v["max"] + dist*(distm/distM), config_ref["params"][k]["max"])

        elif k=="offset":
            config["params"][k]["min"] = max(v["min"] - 1 - dist*(distM/(distm+1)), config_ref["params"][k]["min"])
            config["params"][k]["max"] = min(v["max"] + 1 + dist*(distm/(distM+1)), config_ref["params"][k]["max"])


        elif k=="permeability":
            config["params"][k]["min"] = max(v["min"] - dist*(distM/distm), 0)
            config["params"][k]["max"] = min(v["max"] + dist*(distm/distM), 1)    
        
        elif k=="initial_i":
            config["params"][k]["min"] = max(v["med"] - 5*dist*(distM/distm), 0)
            config["params"][k]["max"] = v["med"] + 5*dist*(distm/distM)
        
        else:
            # config["params"][k]["min"] = max(v["min"] - 2*dist*(distM/distm), config_ref["params"][k]["min"])
            # config["params"][k]["max"] = min(v["max"] + 2*dist*(distm/distM), config_ref["params"][k]["max"])
            config["params"][k]["min"] = v["min"] - dist*(distM/distm)
            config["params"][k]["max"] = v["max"] + dist*(distm/distM)


if __name__=='__main__':
    COUNTRY = "Spain"
    prepare_deaths_p_active(COUNTRY)
    generate_configuration(COUNTRY)
