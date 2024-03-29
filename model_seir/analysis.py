from math import modf
import matplotlib.pyplot as plt
import pandas
from .configuration import open_save_files
from .simulation_functions import *
import seaborn
import numpy as np
from scipy import stats


def median(array):
    return percentil(array, 50)
    
def percentil(array, i):
    index = array.size * i / 100
    decimal, complete = modf(index)
    complete = int(complete)
    if decimal==0:
        return array[complete+1]
    return (array[complete] + array[complete+1])/2

def correlations(params, n_bins, weights, country, with_seaborn=False):
    if with_seaborn:
        db = pandas.DataFrame(columns=param_to_index.keys())
        for p in param_to_index:
            db[p] = params[param_to_index[p]]

        g = seaborn.PairGrid(db, corner=True, diag_sharey=False)
        g.map_lower(seaborn.kdeplot, levels=4, color=".2")
        # g.map_upper(seaborn.histplot)
        g.map_diag(seaborn.kdeplot)
        g.savefig(f'images\images_by_country\{country}\correlations.png')
        return
    
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
                bottom_h = left_h = left + width + 0.04
                
                rect_scatter = [left, bottom, width, height]
                rect_histx = [left, bottom_h, width, 0.2]
                rect_histy = [left_h, bottom, 0.2, height]
                
                # start with a rectangular Figure
                with plt.style.context('science'):
                    fig = plt.figure(1, figsize=(5, 5))

                    labels = {
                        'lambda' :  r"$\lambda$",
                        'permeability' : r"$\phi$",
                        'initial_i' : r"$I/N$",
                        'what' : r"$\xi$",
                        'offset' : r"$offset$",
                        'IFR' : r"$IFR$",
                        'log_diff' : r"Distancia a función objetivo",
                        'eta': r"$\eta$",
                        'mu': r"$\mu$"
                    }
                    
                    axScatter = plt.axes(rect_scatter)
                    axHistx = plt.axes(rect_histx)
                    axHistx.tick_params(top=False, right=False, left=False)
                    axHistx.tick_params(which='minor', top=False, right=False, left=False)

                    # axHistx.set_yticks([], minor=False)
                    # axHistx.set_xticks([], minor=False)

                    axHisty = plt.axes(rect_histy)
                    axHisty.set_xlabel("Frecuencia relativa")
                    # axHisty.set_title("$"+ labels[j_n] +"$")
                    axHisty.tick_params(bottom=False, right=False, top=False)
                    axHisty.tick_params(which='minor', bottom=False, right=False, top=False)
                    # axHisty.set_yticks([], minor=False)
                    # axHisty.set_xticks([], minor=False)
                    
                    # no labels
                    axHistx.xaxis.set_major_formatter(nullfmt)
                    axHistx.yaxis.set_major_formatter(nullfmt)
                    axHisty.xaxis.set_major_formatter(nullfmt)
                    axHisty.yaxis.set_major_formatter(nullfmt)
                
                    # the scatter plot:
                    # axScatter.scatter(x, y)
                    
                    
                    # now determine nice limits by hand:
                    xymax = [np.max(x), np.max(y)]
                    xymin = [np.min(x), np.min(y)]
                    
                    axScatter.set_xlim((xymin[0], xymax[0]))
                    axScatter.set_ylim((xymin[1], xymax[1]))

                    xbins = np.linspace(xymin[0], xymax[0], n_bins)
                    ybins = np.linspace(xymin[1], xymax[1], n_bins)

                    
                    axScatter.hist2d(x, y, bins=[xbins, ybins], weights=weights)


                    
                    x_smoooth = np.linspace(start=x.min(), stop=x.max(), num=250)
                    gkdex = stats.gaussian_kde(dataset=x, weights=weights)
                    axHistx.plot(x_smoooth, gkdex.evaluate(x_smoooth), linestyle='solid', lw=1.3, alpha=0.7)
                    axHistx.fill_between(x_smoooth, np.zeros(250), gkdex.evaluate(x_smoooth), alpha=0.4)
                    axHistx.set_ylim(ymin=0)
                    axHistx.spines['right'].set_visible(False)
                    axHistx.spines['top'].set_visible(False)
                    axHistx.spines['left'].set_visible(False)
                    # axHistx.hist(x, bins=xbins, weights=weights)

                    
                    y_smoooth = np.linspace(start=y.min(), stop=y.max(), num=250)
                    gkdey = stats.gaussian_kde(dataset=y, weights=weights)
                    axHisty.plot(gkdey.evaluate(y_smoooth), y_smoooth, linestyle='solid', lw=1.3, alpha=0.7)
                    axHisty.fill_betweenx(y_smoooth, np.zeros(250), gkdey.evaluate(y_smoooth), alpha=0.4)
                    axHisty.set_xlim(xmin=0)
                    axHisty.spines['right'].set_visible(False)
                    axHisty.spines['top'].set_visible(False)
                    axHisty.spines['bottom'].set_visible(False)
                    # axHisty.hist(y, bins=ybins, orientation='horizontal', weights=weights)


                    axScatter.set_xlabel("$"+ labels[i_n] +"$")
                    axScatter.set_ylabel("$"+ labels[j_n] +"$")
                    
                    axHistx.set_xlim(axScatter.get_xlim())
                    axHisty.set_ylim(axScatter.get_ylim())
                    
                    fig.savefig(f'images\images_by_country\{country}\correlation_{i_n}_{j_n}.png')
                    fig.savefig(f'images\images_by_country\{country}\correlation_{i_n}_{j_n}.pdf')
                    plt.close(fig)



def plot_the_plots(country, *, save_pictures=True, only_correlations=False, with_seaborn=False):
        
    files = open_save_files(country, mode='r')
    
        
    lenf = sum(1 for _ in files['log_diff'])
    params = np.zeros([len(files.keys()), lenf])
    log_diff = np.zeros(lenf)
    files['log_diff'].seek(0)
    
    for k, v in param_to_index.items():
        for i, value in enumerate(files[k]):
            params[param_to_index[k], i] = np.float64(value)
    for i,value in enumerate(files['log_diff']):
        log_diff[i] = np.float64(value)

    weights = np.exp(-log_diff/log_diff.min())
            
    if save_pictures or only_correlations:
        correlations(params, 30, weights, country, with_seaborn=with_seaborn)

    percentiles = {}
                
    for k,f in files.items():
        # TODO: cambiar?
        if k=='recovered':
            continue
        
        
        if k not in ['log_diff', 'recovered']:
            k_array = params[param_to_index[k]].copy()
        else:
            k_array = log_diff.copy()
            
        k_array_copy = k_array.copy()
        k_array_copy.sort()

        k_array_median = median(k_array_copy)
        k_array_percentil_5 = percentil(k_array_copy, 5)
        k_array_percentil_95 = percentil(k_array_copy, 95)
        if k not in ['log_diff', 'recovered']:
            percentiles.update({
                k:{
                    "min" : k_array_percentil_5,
                    "med" : k_array_median,
                    "max" : k_array_percentil_95
                }})
        
        if not save_pictures:
            continue

        with plt.style.context('science'):
            fig, ax = plt.subplots()

            x = np.linspace(start=k_array.min(), stop=k_array.max(), num=250)
            
            
            if k == 'offset':
                k_array = list(map(int, k_array))
                ax.hist(k_array, np.arange(min(k_array)-0.5, max(k_array)+0.5, 1), density=True, align='mid', weights=weights)
            else:
                if k!='log_diff':
                    bins = np.linspace(k_array.min(), k_array.max(), 20)
                    ax.hist(k_array, bins=bins, density=True, weights=weights, alpha=0.5, linewidth=0.8, edgecolor="tab:grey", fill=False)
                    gkde = stats.gaussian_kde(dataset=k_array, weights=weights)
                else:
                    ax.hist(k_array, 20, density=True, alpha=0.3)
                    gkde = stats.gaussian_kde(dataset=k_array)


            ax.plot(x, gkde.evaluate(x), linestyle='solid', color="tab:blue", lw=1.3, alpha=0.7)
            ax.fill_between(x, np.zeros(x.shape[0]), gkde.evaluate(x), alpha=0.4)
            
            # ax.set_yticks([])
            ax.set_yticklabels([])
            
            y_min, y_max = ax.get_ylim()
            ax.vlines(k_array_median, ymin=y_min, ymax=gkde.evaluate(k_array_median), label='Mediana', color='orange')
            ax.vlines(k_array_percentil_5, ymin=y_min, ymax=gkde.evaluate(k_array_percentil_5), label='Percentil 5', color='red')
            ax.vlines(k_array_percentil_95, ymin=y_min, ymax=gkde.evaluate(k_array_percentil_95), label='Percentil 95', color='purple')
            ax.set_ylabel('Frecuencia relativa')
            
            ax.set_xlabel(f"{k}")
            ax.set_ylim(ymin=0)
            ax.set_xlim(x.min(), x.max())
            # ax.set_title(k.capitalize())

            label = {
                'lambda' :  r"$\lambda$",
                'permeability' : r"$\phi$",
                'initial_i' : r"$I/N$",
                'what' : r"$\xi$",
                'offset' : r"$offset$",
                'IFR' : r"$IFR$",
                'log_diff' : r"Distancia a función objetivo",
                'eta': r"$\eta$",
                'mu': r"$\mu$"
            }[k]
            
            # if k=='initial_i':
            #     ax.set_xscale('log')

            ax.set_xlabel(label)
            # ax.set_title(label)
            
            # ax.legend()
            
            fig.savefig(f'images\images_by_country\{country}\{k}_histogram.png')
            fig.savefig(f'images\images_by_country\{country}\{k}_histogram.pdf')
            plt.close(fig)
            # plt.show()
    return percentiles
        
        
        
        
if __name__=='__main__':
    
    COUNTRY = 'SEID'
    MAX_DAYS = 220
    plot_the_plots(COUNTRY, only_correlations=True)
