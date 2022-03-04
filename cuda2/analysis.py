from math import floor, modf
import matplotlib.pyplot as plt
from simulation_functions import *

def median(array):
    return percentil(array, 50)
    
def percentil(array, i):
    index = array.size * i / 100
    decimal, complete = modf(index)
    complete = int(complete)
    if decimal==0:
        return array[complete+1]
    return (array[complete] + array[complete+1])/2


if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 110
    TOTAL_POPULATION = 42.7e6
    
        
    files = {}
    mode = 'r'
    for k,v in param_to_index.items():
        files.update({k: open(f"generated_data\data_by_country\{COUNTRY}\{k}.dat", mode)})
        
        
    lenf = sum(1 for _ in files['IFR'])
    params = np.zeros([len(files.keys()), lenf])
    files['IFR'].seek(0)
    
    for k, v in param_to_index.items():
        for i, value in enumerate(files[k]):
            params[param_to_index[k], i] = np.float64(value)
            
    correlations(params, 45)
                
    for k,f in files.items():
        fig, ax = plt.subplots()
        
        k_array = params[param_to_index[k]].copy()
            
        k_array.sort()
            
        k_array_median = median(k_array)
        k_array_percentil_5 = percentil(k_array, 5)
        k_array_percentil_95 = percentil(k_array, 95)
        
        ax.hist(k_array, 200, density=True)
        
        y_min, y_max = ax.get_ylim()
        ax.vlines(k_array_median, ymin=y_min, ymax=y_max, label='Median', color='orange')
        ax.vlines(k_array_percentil_5, ymin=y_min, ymax=y_max, label='Percentile 5', color='red')
        ax.vlines(k_array_percentil_95, ymin=y_min, ymax=y_max, label='Percentile 95', color='purple')
        ax.set_ylabel('Relative frecuency')
        
        ax.set_xlabel(f"{k}")
        ax.set_title(k.capitalize())
        if k=='lambda':
            ax.set_xlabel(r"$\lambda$")
            ax.set_title(r"$\lambda$")
        if k=='permability':
            ax.set_xlabel(r"$\phi$")
            ax.set_title(r"$\phi$")
        if k=='initial_i':
            ax.set_xlabel(r"$\rho_I$")
            ax.set_title(r"$\rho_I$")
        if k=='what':
            ax.set_xlabel(r"$\xi$")
            ax.set_title(r"$\xi$")
        ax.legend()
        
        
        fig.savefig(f'images\images_by_country\{COUNTRY}\{k}_histogram.png')
        # plt.show()