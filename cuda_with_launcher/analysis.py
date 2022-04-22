from math import floor, modf
import matplotlib.pyplot as plt
from configuration import open_save_files
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


def correlations(params, n_bins, log_diff, country):
    from matplotlib.ticker import NullFormatter
    
    for i_n, i in param_to_index.items():
        for j_n, j in param_to_index.items():
            if i < j:
                
                try:
                    x = params[i,:].get()
                    y = params[j,:].get()
                except AttributeError:
                    x = params[i,:]
                    y = params[j,:]
                
                nullfmt = NullFormatter()         # no labels
                
                # definitions for the axes
                left, width = 0.1, 0.65
                bottom, height = 0.1, 0.65
                bottom_h = left_h = left + width + 0.02
                
                rect_scatter = [left, bottom, width, height]
                rect_histx = [left, bottom_h, width, 0.2]
                rect_histy = [left_h, bottom, 0.2, height]
                
                # start with a rectangular Figure
                fig = plt.figure(1, figsize=(8, 8))
                
                axScatter = plt.axes(rect_scatter)
                axHistx = plt.axes(rect_histx)
                axHistx.set_title("$"+ i_n +"$")
                axHisty = plt.axes(rect_histy)
                axHisty.set_title("$"+ j_n +"$")
                
                # no labels
                axHistx.xaxis.set_major_formatter(nullfmt)
                axHisty.yaxis.set_major_formatter(nullfmt)
                
                # the scatter plot:
                # axScatter.scatter(x, y)
                
                
                # now determine nice limits by hand:
                xymax = [np.max(x), np.max(y)]
                xymin = [np.min(x), np.min(y)]
                
                axScatter.set_xlim((xymin[0], xymax[0]))
                axScatter.set_ylim((xymin[1], xymax[1]))
                
                if i not in [param_to_index['offset']]:
                    xbins = np.linspace(xymin[0], xymax[0], n_bins)
                else:
                    n_bins_ = int(xymax[0] - xymin[0]) +1 
                    xbins = np.arange(int(xymin[0])-0.5, int(xymax[0])+0.5)
                    
                if j not in [param_to_index['offset']]:
                    ybins = np.linspace(xymin[1], xymax[1], n_bins)
                else:
                    n_bins_ = int(xymax[1] - xymin[1]) +1 
                    xbins = np.linspace(xymin[0], xymax[0], n_bins_)
                    ybins = np.arange(int(xymin[1])-0.5, int(xymax[1])+0.5)
                
                axScatter.hist2d(x, y, bins=[xbins, ybins], weights=1/log_diff)
                axHistx.hist(x, bins=xbins, weights=1/log_diff)
                axHisty.hist(y, bins=ybins, orientation='horizontal', weights=1/log_diff)
                
                axHistx.set_xlim(axScatter.get_xlim())
                axHisty.set_ylim(axScatter.get_ylim())
                
                fig.savefig(f'images\images_by_country\{country}\correlation_{i_n}_{j_n}.png')
                plt.close(fig)


def plot_the_plots(country, max_days, *, save_pictures=True):
        
    files = open_save_files(country, mode='r')
    
        
    lenf = sum(1 for _ in files['IFR'])
    params = np.zeros([len(files.keys()), lenf])
    log_diff = np.zeros(lenf)
    files['IFR'].seek(0)
    
    for k, v in param_to_index.items():
        for i, value in enumerate(files[k]):
            params[param_to_index[k], i] = np.float64(value)
    for i,value in enumerate(files['log_diff']):
        log_diff[i] = 1/np.float64(value)
            
    if save_pictures:
        correlations(params, 30, log_diff, country)

    percentiles = {}
                
    for k,f in files.items():
        # TODO: cambiar?
        if k=='recovered':
            continue
        
        
        if k not in ['log_diff', 'recovered']:
            k_array = params[param_to_index[k]].copy()
        else:
            k_array = log_diff.copy()
            
        k_array.sort()
            
        k_array_median = median(k_array)
        k_array_percentil_5 = percentil(k_array, 5)
        k_array_percentil_95 = percentil(k_array, 95)
        if k not in ['log_diff', 'recovered']:
            percentiles.update({
                k:{
                    "min" : k_array_percentil_5,
                    "med" : k_array_median,
                    "max" : k_array_percentil_95
                }})
        
        if not save_pictures:
            continue
        fig, ax = plt.subplots()
        
        if k == 'offset':
            k_array = list(map(int, k_array))
            ax.hist(k_array, np.arange(min(k_array)-0.5, max(k_array)+0.5, 1), density=True, align='mid', weights=1/log_diff)
        else:
            if k!='log_diff':
                ax.hist(k_array, 20, density=True, weights=1/log_diff)
            else:
                ax.hist(k_array, 20, density=True)
        
        
        y_min, y_max = ax.get_ylim()
        ax.vlines(k_array_median, ymin=y_min, ymax=y_max, label='Mediana', color='orange')
        ax.vlines(k_array_percentil_5, ymin=y_min, ymax=y_max, label='Percentil 5', color='red')
        ax.vlines(k_array_percentil_95, ymin=y_min, ymax=y_max, label='Percentil 95', color='purple')
        ax.set_ylabel('Frecuencia relativa')
        
        ax.set_xlabel(f"{k}")
        ax.set_title(k.capitalize())

        label = {
            'lambda' :  r"$\lambda$",
            'permeability' : r"$\phi$",
            'initial_i' : r"$\rho_I$",
            'what' : r"$\xi$",
            'offset' : r"$offset$",
            'IFR' : r"$IFR$",
            'log_diff' : r"Distancia a función objetivo"
        }[k]
        
        # if k=='initial_i':
        #     ax.set_xscale('log')

        ax.set_xlabel(label)
        ax.set_title(label)
        
        ax.legend()
        
        fig.savefig(f'images\images_by_country\{country}\{k}_histogram.png')
        plt.close(fig)
        # plt.show()
    return percentiles
        
        
        
        
if __name__=='__main__':
    
    COUNTRY = 'Switzerland'
    MAX_DAYS = 60
    plot_the_plots(COUNTRY, MAX_DAYS)