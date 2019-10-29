import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
from matplotlib.markers import TICKDOWN

def paired_analysis_idx(array_length):
    """
    This function is to grap two element from an array in each round. 
    The title should has the same length as array representing 
    array element title. This function can help to do paired t test or draw significant line.
    """
    pair = []
    level = []
    levelflag = 1
    headstart = 0
    length = array_length
    for gap in range(1,length):
        for head in range(gap):
            tmphead = head
            tail = tmphead + gap
            while tail <= length -1:
                newpair = [tmphead, tail]
                pair.append(newpair)
                level.append(levelflag)
                tmphead = tail
                tail = tmphead+gap
            levelflag = min(levelflag + 1, level[-1]+1)
    return(pair, level)

def group_value_to_dict_element(array):
    res = dict()
    try:  # <=========this place need to idenfity if is come from pd, if yes, do this
        array = array[~pd.isnull(array)]
    except:
        pass
    res['array'] = array
    res['n'] = len(array)
    res['mean'] = np.mean(array)
    res['stdev'] = np.std(array)
    res['sterr'] = res['stdev']/math.sqrt(res['n'])
    return(res)

def identify_value_type(array):
    variable = list(set(array))
    if len(variable) == 2:
        return('logic')
    else:
        return('value')

def analysis_between_groups(result_array, group_titles, n_fig_of_each_row = 3):
    """
    When we analyse a group of data, we will get a dict containing series
    of analysis feature. If the analysis method is the same, different group
    will get a dict with same key words. This function is to plot along
    the keys to show different between groups. Right now it only tested two groups.
    """
    def __intersection__(lists): 
        lst1 = lists[0]
        for i in range(1, len(lists)):
            tmplst = lists[i]
            lst1 = list(set(lst1) & set(tmplst))
        return(lst1)
    
    keys = list(result_array[0].keys())
    n_rows = math.ceil(len(keys)/n_fig_of_each_row)
    plt.rcParams["figure.figsize"] = [6 * n_fig_of_each_row, 6 * n_rows] 
    #plt.subplots_adjust(wspace = 1)
    #fig, axs = plt.subplots(n_rows, n_fig_of_each_row)
    fig = plt.figure()
    
    for i in range(len(keys)):
        axrow = int(i / n_fig_of_each_row)
        axcol = i % n_fig_of_each_row
        
        ax = fig.add_subplot(n_rows, n_fig_of_each_row, i+1)
        key = keys[i]
        dictarray = [x[key] for x in result_array]
        analysis = __intersection__([x[key]['analysis_method'] for x in result_array])
        if 'box' in analysis:
            ax_barplot(ax, dictarray, key, group_titles)
        elif 'scatter' in analysis:
            ax_scatter(ax, dictarray, key, group_titles)
    #fig.tight_layout()
    fig.subplots_adjust(hspace = 0.5, wspace = 0.7)
    plt.show()

#============================================================================================================
# plot methods ==============================================================================================
#============================================================================================================
def ax_barplot(ax, result_array, title, group_titles):
    # result_array is an array containing dict results from different groups.
    # This function will use bar plot to show the figure.
    # ax is the subplot from plt.subplot(n,m)
    
    def label_diff(ax,pair,text,X,topy,level):
        x = (X[pair[0]]+X[pair[1]])/2
        y = (1+0.1*level)*topy
        ax.annotate(text, xy=(x,y), zorder=10, ha = 'center', va = 'center', backgroundcolor='w')
        ax.plot([X[pair[0]], X[pair[1]]], [y, y],'-',lw=1,color = 'grey', marker = TICKDOWN,markersize = 3)

    def pvalue_text(p):
        if p > 0.05:
            text = 'p=%.2f' % p
        elif p <= 0.05 and p > 0.01:
            text = '* p=%.3f' % p
        elif p<=0.01 and p > 0.005:
            text = '** p=%.4f' % p
        else:
            text = '*** p=%.1e' % p
        return(text)
    
    # This code should set before make subplot. It is the fundmental.
    # It works for jupyter notebook. But I'm not sure if it works to output.
    width = 3/(4*len(result_array)-1)

    colors = plt.cm.Pastel2(np.linspace(0,1,8)) # Fist get cmap Pastel2. Then define set to how many pieces.
    
    xlocation = 4*np.arange(len(result_array))*width/3 + 0.5*width
    ax.set_xticks(xlocation)
    ax.set_xticklabels(group_titles)

    yvalue = [x['mean'] for x in result_array]
    errvalue = [x['sterr'] for x in result_array]

    ax.bar(xlocation, yvalue, width, 
            yerr = errvalue,
            color=colors)
        
    ax.set_title(title)
    
    topy = max([x['mean']+x['sterr'] for x in result_array])
    plist, level = paired_analysis_idx(len(result_array))
    for i in range(len(plist)):
        p = stats.mannwhitneyu(np.array(result_array[plist[i][0]]['array']).astype(float), 
                                np.array(result_array[plist[i][1]]['array']).astype(float))[1]
        if p < 0.05:
            label_diff(ax, plist[i], pvalue_text(p), xlocation, topy, level[i])
    
    ax.set_ylim(0.0, topy*(1+0.2*len(plist)))


def ax_scatter(ax, result_arrays, title, group_titles):
    markerlist = ['s', '^']
    colors = plt.cm.tab10(np.linspace(0,1,10))
    
    for i in range(len(result_arrays)):
        array = result_arrays[i]
        X = np.array([x[0] for x in array['array']])
        Y = np.array([x[1] for x in array['array']])
        #C = np.array([x[2] for x in array['array']])
        
        ax.scatter(X, Y, c=colors[i], s=2, marker = ',', alpha = 0.3)
    ax.set_xlabel(result_arrays[0]['character_columns'][0])
    ax.set_ylabel(result_arrays[0]['character_columns'][1])
    ax.legend(group_titles)
    ax.set_title(title)

def ax_3dscatter(ax, result_arrays, title, group_titles):
    markerlist = ['s', '^']
    for i in range(len(result_arrays)):
        array = result_arrays[i]
        X = np.array([x[0] for x in array['array']])
        Y = np.array([x[1] for x in array['array']])
        Z = np.array([x[2] for x in array['array']])
        ax.scatter(X, Y, Z, marker=markerlist[i], alpha = 0.3)
        #ax.plot_wireframe(X,Y,Z, marker = markerlist[i], alpha = 0.2)
    ax.set_xlabel(result_arrays[0]['character_columns'][0])
    ax.set_ylabel(result_arrays[0]['character_columns'][1])
    ax.set_ylabel(result_arrays[0]['character_columns'][2])
    ax.legend(group_titles)
    ax.set_title(title)

def ax_hist2d(ax, result_arrays, title, group_titles):
    pass