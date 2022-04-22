import geopandas as gp
import matplotlib.pyplot as plt
import configuration
import parameters_control
import analysis
import numpy as np

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

def read_geo_frame():
    w = gp.read_file("real_data/gp_world.csv", GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")
    return w

def save_geo_frame(frame):
    with open("real_data/gp_world.csv", 'w') as file:
        frame.to_csv(file)


def update_geo_frame(frame):
    for c in frame['name']:
        for v in parameters_control.all_params:
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
    return frame



if __name__=='__main__':
    # crear_gp_world()

    world = read_geo_frame()
    world = update_geo_frame(world)
    save_geo_frame(world)

    world.plot('permeability', cmap='viridis', legend=True, figsize=(12,8), missing_kwds={'color': 'lightgrey'})
    # plt.title('World Population')

    

    # df = gp.read_file(gp.datasets.get_path("naturalearth_lowres"))
    # df.plot('pop_est', cmap='viridis', legend=True, figsize=(12,8))

    # print(world.head())
    # print(df.head())

    plt.show()