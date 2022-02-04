import cupy as cp
import cupy.random as cprand
from set_parameters import *

N_SIMULATIONS = 10

COUNTRY = 'Spain'

param_to_index = {
    'permability' : 0,
    'lambda' : 1,
    'IFR' : 2,
    'what' : 3,
}

# De esto se debería sacar el tiempo de simulacion (creo)
p_active: cp.ndarray
p_active_db = pandas.read_csv(r'real_data\Deaths_worldwide_1Aug.csv')

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
params = cp.zeros((4,N_SIMULATIONS), dtype=cp.float64)
set_params(params)


    

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