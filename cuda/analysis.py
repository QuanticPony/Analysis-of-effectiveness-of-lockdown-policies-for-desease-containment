import matplotlib.pyplot as plt
from simulation_functions import *

if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 110
    TOTAL_POPULATION = 42.7e6
    
        
    files = {}
    mode = 'r'
    for k,v in param_to_index.items():
        files.update({k: open(f"generated_data\data_by_country\{COUNTRY}\{k}.dat", mode)})
        
    for k,f in files.items():
        fig, ax = plt.subplots()
        
        lenf = sum(1 for _ in f)
        k_array = np.zeros(lenf)
        f.seek(0)
        for i, value in enumerate(f):
            k_array[i] = np.float64(value)
        
        ax.hist(k_array, 300, density=True)
        ax.set_title(k.capitalize())
        fig.savefig(f'images\images_by_country\{COUNTRY}\{k}_histogram.png')
        plt.show()