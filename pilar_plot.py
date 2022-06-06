from matplotlib.ticker import NullFormatter
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def pilar_plot(x_data, y_data, x_label, y_label, *, x_lim=(None, None), y_lim=(None, None), weights=None, histogram_bins=50, colormap='magma', histogram_color='steelblue', font_size=14):
    """Makes a Pilar's style plot.
    
    Parameters
    ______
    x_data: array
        Raw data of x axis.
    y_data: array
        Raw data of y axis.
    x_label: str
        X axis' label.
    y_label: str
        Y axis' label.

    Keywords
    ______
    x_lim: tuple(2)
        min and max limits of x axis.
    y_lim: tuple(2)
        min and max limits of y axis.
    weights: array
        Weights of data pairs for histograms.
    histogram_bins: int default=50
        Number of bins in histograms.
    colormap: str default='magma'
        Colormap used in 2d histogram.
    histogram_color: str default='steelblue'
        Color used in lateral histograms.
    font_size: float default=14
        Font size for labels and tick labels.
    
    Returns
    ______
    Figure, xy_Histogram_axes, x_Histogram_axes, y_Histogram_axes
    """


    x = x_data.copy()
    y = y_data.copy()

    nullfmt = NullFormatter()  # no labels

    # definitions for the axes sizes and positions
    left, width = 0.20, 0.65
    bottom, height = 0.20, 0.65
    bottom_h = left_h = left + width + 0.03

    # corners of axis boxes
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.12]
    rect_histy = [left_h, bottom, 0.12, height]
                    

    fig = plt.figure(figsize=(5, 5))
    plt.rc('font', size=font_size) 
    
    # center histogram axis
    axHist2d = plt.axes(rect_scatter)
    
    # top histogram axis
    axHistx = plt.axes(rect_histx) 
    axHistx.tick_params(top=False, right=False, left=False, bottom=False)
    axHistx.tick_params(which='minor', top=False, right=False, left=False, bottom=False)

    # right histogram axis
    axHisty = plt.axes(rect_histy) 
    axHisty.tick_params(top=False, right=False, left=False, bottom=False)
    axHisty.tick_params(which='minor', top=False, right=False, left=False, bottom=False)

    
    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHistx.yaxis.set_major_formatter(nullfmt)
    axHisty.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)


    # histograms limits:
    xymax = [np.max(x) if x_lim[1] is None else x_lim[1], np.max(y) if y_lim[1] is None else y_lim[1]]
    xymin = [np.min(x) if x_lim[0] is None else x_lim[0], np.min(y) if y_lim[0] is None else y_lim[0]]
    
    # define bins positions for x and y axis
    xbins = np.linspace(xymin[0], xymax[0], histogram_bins)
    ybins = np.linspace(xymin[1], xymax[1], histogram_bins)

    # make nice x and y ticks and labels

    axHist2d.tick_params(top=False, right=False, left=False, bottom=False)
    axHist2d.tick_params(labelsize=font_size)

    axHist2d.set_xticks(np.linspace(xymin[0], xymax[0], 3))
    axHist2d.set_xticklabels(list(map(lambda x: f"${x:.1f}$", np.linspace(xymin[0], xymax[0], 3))))
    axHist2d.set_yticks(np.linspace(xymin[1], xymax[1], 5))
    axHist2d.set_yticklabels(list(map(lambda x: f"${x:.1f}$", np.linspace(xymin[0], xymax[0], 5))))

    # make histogram 2d
    axHist2d.hist2d(x, y, bins=[xbins, ybins], weights=weights, cmap=colormap)
    
    # top histogram interpolation with kde gaussian kernel
    x_smoooth = np.linspace(start=xymin[0], stop=xymax[0], num=250)
    gkdex = stats.gaussian_kde(dataset=x, weights=weights)
    axHistx.plot(x_smoooth, gkdex.evaluate(x_smoooth), linestyle='solid', color=histogram_color, lw=1.3, alpha=0.7)
    axHistx.fill_between(x_smoooth, np.zeros(250), gkdex.evaluate(x_smoooth), alpha=0.4, color=histogram_color)
    axHistx.set_ylim(ymin=0)
    axHistx.spines['right'].set_visible(False)
    axHistx.spines['top'].set_visible(False)
    axHistx.spines['left'].set_visible(False)
    axHistx.spines['bottom'].set_visible(False)

    # right histogram interpolation with kde gaussian kernel
    y_smoooth = np.linspace(start=xymin[1], stop=xymax[1], num=250)
    gkdey = stats.gaussian_kde(dataset=y, weights=weights)
    axHisty.plot(gkdey.evaluate(y_smoooth), y_smoooth, linestyle='solid', color=histogram_color, lw=1.3, alpha=0.7)
    axHisty.fill_betweenx(y_smoooth, np.zeros(250), gkdey.evaluate(y_smoooth), alpha=0.4, color=histogram_color)
    axHisty.set_xlim(xmin=0)
    axHisty.spines['right'].set_visible(False)
    axHisty.spines['top'].set_visible(False)
    axHisty.spines['left'].set_visible(False)
    axHisty.spines['bottom'].set_visible(False)

    # set labels
    axHist2d.set_xlabel("$"+ x_label +"$", fontsize=font_size)
    axHist2d.set_ylabel("$"+ y_label +"$")
    
    # set histogram lims
    axHist2d.set_xlim((xymin[0], xymax[0]))
    axHist2d.set_ylim((xymin[1], xymax[1]))
    axHistx.set_xlim((xymin[0], xymax[0]))
    axHisty.set_ylim((xymin[1], xymax[1]))
    
    return fig, axHist2d, axHistx, axHisty



if __name__=='__main__':
    x = np.random.normal(scale=1.5, size=5000)
    y = np.random.normal(scale=1, size=5000)

    fig, axHist2d, axHistx, axHisty = pilar_plot(x, y, "x", r"\left<x\right>^{NN}",
        x_lim=(-5, 5), y_lim=(-5,5))
    plt.show()