#%%
import geopandas as gp
import pandas as pd
import matplotlib.pyplot as plt
from . import parameters_control
from . import analysis
import numpy as np
from .configuration import get_all_countries, read_configuration
import seaborn

def crear_gp_world():
    # world_filepath = gp.datasets.get_path('naturalearth_lowres')
    # world = gp.read_file(world_filepath)
    world = gp.read_file("real_data/gp_world_ref.csv", GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")

    dict_ = {param:0 for param in parameters_control.all_params}

    world = world.assign(**dict_)

    #! Por si tengo que borrar alguna columna
    # df.drop(['column_name1', 'column_name2'], axis=1, inplace=True)

    with open("real_data/gp_world.csv", 'w') as file:
        world.to_csv(file)
        

def crear_gp_world_gdp():
    # world_filepath = gp.datasets.get_path('naturalearth_lowres')
    # world = gp.read_file(world_filepath)
    world = gp.read_file("real_data/gp_world.csv", GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")

    dict_ = {param:0 for param in ['gdp', 'gdp_nominal']}

    world = world.assign(**dict_)

    #! Por si tengo que borrar alguna columna
    # df.drop(['column_name1', 'column_name2'], axis=1, inplace=True)

    with open("real_data/gp_world.csv", 'w') as file:
        world.to_csv(file)

def read_geo_frame():
    w = gp.read_file("real_data/gp_world.csv", GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")
    return w

def save_geo_frame(frame):
    with open("real_data/gp_world.csv", 'w') as file:
        frame.to_csv(file)


def update_geo_frame(frame):
    all_countries = get_all_countries()
    world_gdp = pd.read_csv("real_data/gp_world_gdp_capita.csv")
    
    for c in frame['name']:
        if c not in all_countries:
            frame.loc[lambda w: w['name']==c, "score"] = np.nan
            for v in parameters_control.all_params+['gdp','gdp_capita', 'gdp_nominal']:
                frame.loc[lambda w: w['name']==c, v] = np.nan
            for v in parameters_control.all_params:
                frame.loc[lambda w: w['name']==c, v+'_err'] = np.nan
            continue
        
        for v in parameters_control.all_params:
            frame.loc[lambda w: w['name']==c, "score"] = np.nan
            frame.loc[lambda w: w['name']==c, v] = np.nan
            frame.loc[lambda w: w['name']==c, v+'_err'] = np.nan
        for v in ['gdp', 'gdp_capita', 'gdp_nominal']:
            try:
                frame.loc[lambda w: w['name']==c, v] = float(world_gdp.loc[lambda w: w['Country']==c, v])
            except Exception as e:
                print(c)
                frame.loc[lambda w: w['name']==c, v] = np.nan
        try:
            files = analysis.open_save_files(c, erase_prev=False, mode='r')
        except FileNotFoundError:
            continue

        for v,f in files.items():
            if v=='recovered':
                continue
            v_array = []
            for l in f:
                v_array.append(float(l))
            v_array = np.array(v_array)

            if len(v_array) > 0:
                frame.loc[lambda w: w['name']==c, v] = analysis.median(v_array)
                frame.loc[lambda w: w['name']==c, v+"_err"] = v_array.std()

        config = read_configuration(c, prefix="used/", sufix='', v2=True)
        frame.loc[lambda w: w['name']==c, "score"] = config["score"]

    frame['field_1']        = frame['field_1'].astype('int64', errors='ignore')
    frame['pop_est']        = frame['pop_est'].astype('int64', errors='ignore')
    # frame['continent']      = frame['continent'].astype('int64', errors='ignore')
    # frame['name']           = frame['name'].astype('int64', errors='ignore')
    # frame['iso_a3']         = frame['iso_a3'].astype('int64', errors='ignore')
    frame['gdp_md_est']     = frame['gdp_md_est'].astype('float64', errors='ignore')
    frame['IFR']            = frame['IFR'].astype('float64', errors='ignore')
    frame['initial_i']      = frame['initial_i'].astype('float64', errors='ignore')
    frame['lambda']         = frame['lambda'].astype('float64', errors='ignore')
    frame['log_diff']       = frame['log_diff'].astype('float64', errors='ignore')
    frame['offset']         = frame['offset'].astype('float64', errors='ignore').astype('int64', errors='ignore')
    frame['permeability']   = frame['permeability'].astype('float64', errors='ignore')
    frame['recovered']      = frame['recovered'].astype('float64', errors='ignore')
    frame['what']           = frame['what'].astype('float64', errors='ignore')
    frame['gdp']            = frame['gdp'].astype('float64', errors='ignore')
    frame['gdp_nominal']    = frame['gdp_nominal'].astype('float64', errors='ignore')
    frame['gdp_capita']     = frame['gdp_capita'].astype('float64', errors='ignore')
    return frame


#%%
if __name__=='__main__':
    # crear_gp_world_gdp()

    world = read_geo_frame()
    world = update_geo_frame(world)
    # save_geo_frame(world)
    # exit()

    # world.plot('permeability', cmap='viridis', legend=True, figsize=(12,8), missing_kwds={'color': 'lightgrey'})
    # plt.title('World Population')

    
    corr = world.corr('pearson') 
    # fig, ax = plt.subplots(figsize=(10,10))

    # corr.style.background_gradient(cmap='coolwarm')
    w_p = world[["gdp_capita", "permeability", "offset"]]
    # seaborn.heatmap(corr, cmap="coolwarm", annot=True, ax=ax, square=True)
    g = seaborn.pairplot(w_p, diag_kind='kde', corner=True)
    g.map_lower(seaborn.kdeplot, levels=4, color=".2")
    # ax.set_xticks(range(corr.select_dtypes(['number']).shape[1]), corr.select_dtypes(['number']).columns, fontsize=14, rotation=45)
    # ax.set_yticks(range(corr.select_dtypes(['number']).shape[1]), corr.select_dtypes(['number']).columns, fontsize=14)

    # ax.set_title("Correlación Pearson")




    # df = gp.read_file(gp.datasets.get_path("naturalearth_lowres"))
    # df.plot('pop_est', cmap='viridis', legend=True, figsize=(12,8))

    # print(world.head())
    # print(df.head())

    plt.show()
    

    
    
    fig, ax = plt.subplots()
        
    ax.tick_params(left=True,
                bottom=True,
                labelleft=True,
                labelbottom=True)
    
    x = 'gdp_nominal'
    y = 'permeability'
    
    
    # ax.hist(world['offset'])
#%%
    for index, row in world.iterrows():
        if not np.isnan(row[y]):
            ax.scatter(row[x], row[y], s=min(world['log_diff']/float(row["log_diff"])))
            ax.annotate(row["name"], (row[x], row[y]))
    ax.set_title(f"Permeabilidad frente a GDP")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    
    

    

    # df = gp.read_file(gp.datasets.get_path("naturalearth_lowres"))
    # df.plot('pop_est', cmap='viridis', legend=True, figsize=(12,8))

    # print(world.head())
    # print(df.head())

    plt.show()