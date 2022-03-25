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


def correlations(params, n_bins, log_diff, country):
    from matplotlib.ticker import NullFormatter
    
    for i_n, i in param_to_index.items():
        if 'lambda'==i_n:
            continue
        for j_n, j in param_to_index.items():
            if 'lambda'==j_n:
                continue
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
                
                if i not in []:
                    xbins = np.linspace(xymin[0], xymax[0], n_bins)
                else:
                    n_bins = int(xymax[0] - xymin[0]) +1 
                    xbins = np.arange(int(xymin[0])-0.5, int(xymax[0])+0.5)
                    
                if j not in []:
                    ybins = np.linspace(xymin[1], xymax[1], n_bins)
                else:
                    n_bins = int(xymax[1] - xymin[1]) +1 
                    xbins = np.linspace(xymin[0], xymax[0], n_bins)
                    ybins = np.arange(int(xymin[1])-0.5, int(xymax[1])+0.5)
                
                axScatter.hist2d(x, y, bins=[xbins, ybins], weights=log_diff)
                axHistx.hist(x, bins=xbins, weights=log_diff)
                axHisty.hist(y, bins=ybins, orientation='horizontal', weights=log_diff)
                
                axHistx.set_xlim(axScatter.get_xlim())
                axHisty.set_ylim(axScatter.get_ylim())
                
                fig.savefig(f'images\images_by_country\{country}\correlation_{i_n}_{j_n}.png')
                plt.close(fig)


def plot_the_plots(country=COUNTRY, max_days=MAX_DAYS):
        
    files = {}
    mode = 'r'
    for k,v in param_to_index.items():
        files.update({k: open(f"generated_data\data_by_country\{country}\{k}.dat", mode)})
    files.update({'log_diff': open(f"generated_data\data_by_country\{country}\log_diff.dat", mode)})
    files.update({'lambdas': open(f"generated_data\data_by_country\{country}\lambdas.dat", mode)})
        
        
    lenf = sum(1 for _ in files['IFR'])
    params = np.zeros([len(files.keys()), lenf])
    log_diff = np.zeros(lenf)
    files['IFR'].seek(0)
    
    params_lambdas = []
    
    for k, v in files.items():
        if k=='lambda':
            continue
        if k=='log_diff':
            continue
        if k=='lambdas':
            _values = files[k].readline()
            n_lambdas = len(_values.split())
            params_lambdas = np.zeros((n_lambdas, lenf))
            files[k].seek(0)
            for i, value in enumerate(files[k]):
                for j, v in enumerate(value.split()):
                    params_lambdas[j,i] = np.float64(v)
            continue
        for i, value in enumerate(files[k]):
            params[param_to_index[k], i] = np.float64(value)
            
    for i,value in enumerate(files['log_diff']):
        log_diff[i] = 1/np.float64(value)
            
    correlations(params, 20, log_diff, country)
                
    for k,f in files.items():
        if k=='log_diff':
            continue
        if k=='lambda':
            continue
        if k=='lambdas':
            fig, *ax = plt.subplots(nrows=params_lambdas.shape[0], sharex=True)
            for i, lamb in enumerate(params_lambdas):
                k_array = lamb.copy()
                k_array.sort()
                k_array_median = median(k_array)
                k_array_percentil_5 = percentil(k_array, 5)
                k_array_percentil_95 = percentil(k_array, 95)
                
                ax[0][i].hist(k_array, 25, density=True, weights=log_diff)
                y_min, y_max = ax[0][i].get_ylim()
                ax[0][i].vlines(k_array_median, ymin=y_min, ymax=y_max, label='Median', color='orange')
                ax[0][i].vlines(k_array_percentil_5, ymin=y_min, ymax=y_max, label='Percentile 5', color='red')
                ax[0][i].vlines(k_array_percentil_95, ymin=y_min, ymax=y_max, label='Percentile 95', color='purple')
                ax[0][i].set_ylabel('Relative frecuency')
                ax[0][i].set_xlabel(f"lambda {i}")
                
            fig.savefig(f'images\images_by_country\{country}\lambdas_histogram.png')
            continue
        fig, ax = plt.subplots()
        
        k_array = params[param_to_index[k]].copy()
            
        k_array.sort()
            
        k_array_median = median(k_array)
        k_array_percentil_5 = percentil(k_array, 5)
        k_array_percentil_95 = percentil(k_array, 95)
        
        if k in ['offset']:
            k_array = list(map(int, k_array))
            ax.hist(k_array, np.arange(min(k_array)-0.5, max(k_array)+0.5), density=True, align='mid', weights=log_diff)
        else:
            ax.hist(k_array, 25, density=True, weights=log_diff)
        
        
        y_min, y_max = ax.get_ylim()
        ax.vlines(k_array_median, ymin=y_min, ymax=y_max, label='Median', color='orange')
        ax.vlines(k_array_percentil_5, ymin=y_min, ymax=y_max, label='Percentile 5', color='red')
        ax.vlines(k_array_percentil_95, ymin=y_min, ymax=y_max, label='Percentile 95', color='purple')
        ax.set_ylabel('Relative frecuency')
        
        ax.set_xlabel(f"{k}")
        ax.set_title(k.capitalize())
        # if k=='lambda':
        #     ax.set_xlabel(r"$\lambda$")
        #     ax.set_title(r"$\lambda$")
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
        
        
        fig.savefig(f'images\images_by_country\{country}\{k}_histogram.png')
        # plt.show()
        
        
        
        
if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 60
    plot_the_plots(COUNTRY, MAX_DAYS)