from math import ceil
import cupy as cp
import datetime
import matplotlib.pyplot as plt
import numpy as np

from set_parameters import *
from evolution import *

COUNTRY = 'Spain'

param_to_index = {
    'permability' : 0,
    'lambda' : 1,
    'IFR' : 2,
    'what' : 3,
    'initial_i' : 4,
}

fixed_params_to_index = {
    'home_size' : 0,
    'k_average_active' : 1,
    'k_average_confined' : 2,
    'eta' : 3,
    'mu' : 4
}

epi_poblation_to_index = {
    'sh' : 0,
    's' : 1,
    'e' : 2,
    'i' : 3,
    'pd' : 4,
    'd' : 5,
    'r' : 6,
}



fixed_params = cp.zeros(5, dtype=cp.float64)
set_fixed_params(fixed_params, COUNTRY)

state = cp.zeros((7,N_SIMULATIONS), dtype=cp.float64)
params = cp.zeros((5,N_SIMULATIONS), dtype=cp.float64)
log_diff = cp.zeros((N_SIMULATIONS), dtype=cp.float64)

set_params(params)
state[1] = 1-params[4]
state[3] = params[4]

def str_to_date(string):
    _d = string.split('/')
    return datetime.date(int(_d[2]), int(_d[0]), int(_d[1]))


simulation_time = 0

# Conseguir el array de las muertes diarias. Indice indica la cantidad de días desde first_day_deaths_list
deaths_complete_db = pandas.read_csv(r'real_data\Deaths_worldwide_1Aug.csv')
deaths_partial_db = deaths_complete_db[deaths_complete_db['Country']==COUNTRY]

first_day_deaths_list = str_to_date(deaths_partial_db['Date'].values[0])
lenght_deaths_list = deaths_partial_db['Date'].size

deaths_list = cp.zeros(lenght_deaths_list, dtype=cp.int32)
for country, date, cumdeath, death in deaths_partial_db.values:
    deaths_list[(str_to_date(date)-first_day_deaths_list).days] = death


#! TODO: la movilidad está puesta como porcentaje de reducción o aumento relativo. 
#! Habría que poner inicialmente 1 como movilidad y luego irá bajando? asumo? ni idea.
# p_active_complete_db = pandas.read_csv(r'real_data\reducedgoogledataset.csv')
# p_active_partial_db  = p_active_complete_db[p_active_complete_db['country_region']==COUNTRY]

# p_active_partial_db['transit_stations_percent_change_from_baseline']
p_active = cp.ones(lenght_deaths_list, dtype=cp.float64)
for i in range(lenght_deaths_list):
    if i>30:
        p_active[i]*=0.2


fig, ax = plt.subplots()
N = 34e6
time_list =  range(lenght_deaths_list+1)
ax.plot(time_list[:-1], deaths_list.get(), label='real data')

time = 0
# historial_state = cp.zeros((7,N_SIMULATIONS, lenght_deaths_list+1), dtype=cp.float64)
# for i in range(lenght_deaths_list):
while time<140:
    # historial_state[:,i] = state[:,0]
    evolve(params, fixed_params, state, time, p_active)
    #! El cp.abs está por si acaso. Por que hay veces que con actualizaciones de los datos son negativos
    log_diff += cp.log(cp.abs(state[5]*N/deaths_list[time]))

    #ax.plot([time for i in range(N_SIMULATIONS)], state[5].get()*N, ',', color='black')
    time+=1
# historial_state[:,-1] = state[:,0]

log_diff_index_sorted = cp.argsort(log_diff)
save_count = ceil(N_SIMULATIONS*0.05)

saved_state = cp.zeros((7,save_count), dtype=cp.float64)
saved_params = cp.zeros((5,save_count), dtype=cp.float64)

for i in range(save_count):
    saved_params[:,i] = params[:,log_diff_index_sorted[i]]

saved_state[1] = 1-saved_params[4]
saved_state[3] = saved_params[4]
time = 0
for i in range(lenght_deaths_list):
    # historial_state[:,i] = state[:,0]
    evolve(saved_params, fixed_params, saved_state, time, p_active)

    ax.plot([time for i in range(save_count)], saved_state[5].get()*N, ',', color='black')
    time+=1



# print(fixed_params)
# print('_--------------------------_')
# print(params)



# ax.plot(time_list, historial_state[0,:].get(), label='sh')
# ax.plot(time_list, historial_state[1,:].get(), label='s')
# ax.plot(time_list, historial_state[2,:].get(), label='e')
# ax.plot(time_list, historial_state[3,:].get(), label='i')
# ax.plot(time_list, historial_state[4,:].get(), label='pd')
# ax.plot(time_list, historial_state[5,:].get()*N, ',', color='black', label='d')

# ax.plot(time_list, historial_state[6,:].get(), label='r')
ax.set_title('Deaths per day')
ax.legend()

plt.show()


    

# @cuda.jit
# def mandel_kernel(min_x, max_x, min_y, max_y, image, iters):
#     height = image.shape[0]
#     width = image.shape[1]

#     pixel_size_x = (max_x - min_x) / width
#     pixel_size_y = (max_y - min_y) / height

#     startX, startY = cuda.grid(2)
#     gridX = cuda.gridDim.x * cuda.blockDim.x
#     gridY = cuda.gridDim.y * cuda.blockDim.y

#     for x in range(startX, width, gridX):
#         real = min_x + x * pixel_size_x
#         for y in range(startY, height, gridY):
#             imag = min_y + y * pixel_size_y
#             image[y, x] = mandel_gpu(real, imag, iters)