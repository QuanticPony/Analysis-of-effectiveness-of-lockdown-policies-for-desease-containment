from matplotlib.ticker import NullFormatter
import matplotlib.pyplot as plt
import numpy as np
    
param_to_index = {
    'permability' : 0,
    'lambda' : 1,
    'IFR' : 2,
    'what' : 3,
    'initial_i' : 4,
}

from matplotlib.patches import Rectangle

def median(array):
    return percentil(array, 50)
    
def percentil(array, i):
    index = array.size * i / 100
    decimal, complete = np.modf(index)
    complete = int(complete)
    if decimal==0:
        return array[complete+1]
    return (array[complete] + array[complete+1])/2


if __name__=='__main__':
    
    COUNTRY = 'Spain'
    MAX_DAYS = 110
    TOTAL_POPULATION = 42.7e6
    n_bins = 15
    
        
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
            

    for i_n, i in param_to_index.items():
        for j_n, j in param_to_index.items():
            if i < j:
                if i_n != 'IFR' or j_n != 'initial_i':
                    continue
                
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
                xymax = [np.max(np.fabs(x)), np.max(np.fabs(y))]
                xymin = [np.min(np.fabs(x)), np.min(np.fabs(y))]
                
                axScatter.set_xlim((xymin[0], xymax[0]))
                axScatter.set_ylim((xymin[1], xymax[1]))
                
                xbins = np.linspace(xymin[0], xymax[0], n_bins)
                ybins = np.linspace(xymin[1], xymax[1], n_bins)
                
                axScatter.hist2d(x, y, bins=[xbins, ybins])
                axHistx.hist(x, bins=xbins)
                axHisty.hist(y, bins=ybins, orientation='horizontal')

                axScatter.add_patch(Rectangle([0.0075, 0.10], 0.005, 0.1, edgecolor='red', fill=False))
                

                axHistx.set_xlim(axScatter.get_xlim())
                axHisty.set_ylim(axScatter.get_ylim())