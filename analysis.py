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
    # since now have build_ttest_character, better not use this function
    # I will deprecate it finally.
    res = dict()
    array = array[~pd.isnull(array)]
    
    res['array'] = array
    res['n'] = len(array)
    res['mean'] = np.mean(array)
    res['stdev'] = np.std(array)
    res['sterr'] = res['stdev']/math.sqrt(res['n'])
    return(res)

def build_chi_character(array, posSymbol = 'Y', method = 'polarbar'):
    array = array[~pd.isnull(array)]
    res = {}
    res['array'] = [int(x == posSymbol) for x in array]
    res['n'] = len(array)
    res['pos'] = sum(res['array'])
    res['neg'] = res['n'] - res['pos']
    res['percentage'] = res['pos'] / res['n']
    res['analysis_method'] = method
    res['dataType'] = 'population'
    return(res)

def build_ttest_character(array, method = 'box'):
    res = dict()
    array = array[~pd.isnull(array)]
    
    res['array'] = array
    res['n'] = len(array)
    res['mean'] = np.mean(array)
    res['stdev'] = np.std(array)
    res['sterr'] = res['stdev']/math.sqrt(res['n'])
    res['analysis_method'] = method
    res['dataType'] = 'avgStd'
    return(res)


def identify_value_type(array):
    variable = list(set(array))
    if len(variable) == 2:
        return('logic')
    else:
        return('value')

def analysis_singleKey_between_groups(result_array, key, group_titles, savepath = None):
    """
    This function is to analyse the key between result array element
    """
    def __intersection__(lists): 
        lst1 = lists[0]
        for i in range(1, len(lists)):
            tmplst = lists[i]
            lst1 = list(set(lst1) & set(tmplst))
        return(lst1)
    
    fig = plt.figure()
    
    ax = fig.add_subplot(n_rows, n_fig_of_each_row, i+1)
    
    dictarray = [x[key] for x in result_array]
    analysis = __intersection__([x[key]['analysis_method'] for x in result_array])
    if 'box' in analysis:
        ax_barplot(ax, dictarray, key, group_titles)
    elif 'scatter' in analysis:
        ax_scatter(ax, dictarray, key, group_titles)
    #fig.tight_layout()
    fig.subplots_adjust(hspace = 0.5, wspace = 0.7)
    if savepath != None:
        plt.savefig(savepath)
    plt.show()

def plot_singleKey_between_groups(result_array, key, anaFun):
    """
    This function is to plot the key between result array element
    """
    pass

def analysis_between_groups(result_array, group_titles, n_fig_of_each_row = 3, savepath = None):
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
            try:
                ax_barplot(ax, dictarray, key, group_titles)
            except:
                pass
        elif 'scatter' in analysis:
            try:
                ax_scatter(ax, dictarray, key, group_titles)
            except:
                pass
    #fig.tight_layout()
    fig.subplots_adjust(hspace = 0.5, wspace = 0.7)
    if savepath != None:
        plt.savefig(savepath)
    plt.show()

def analysis_between_groups_description(result_array, group_titles):
    """
    These function is to describe the comparison between groups.
    use Mann–Whitney U test for mean and std comparison.
    use fisher for population comparison.
    """
    def __intersection__(lists): 
        lst1 = lists[0]
        for i in range(1, len(lists)):
            tmplst = lists[i]
            lst1 = list(set(lst1) & set(tmplst))
        return(lst1)

    paired_compair = paired_analysis_idx(len(result_array))[0]
    
    keys = list(result_array[0].keys())
    for k in keys:
        for pair in paired_compair:
            datatype = result_array[pair[0]][k]['dataType']
            if datatype == 'avgStd':
                try:
                    aou, p = stats.mannwhitneyu(np.array(result_array[pair[0]][k]['array']).astype(float), 
                                                np.array(result_array[pair[1]][k]['array']).astype(float))
                    print('=======================================')
                    print('%s (%s vs %s): \n%f+/-%f n=%d vs %f+/-%f n=%d, p=%f, aou=%f' % (k, group_titles[pair[0]], group_titles[pair[1]], 
                                                                        result_array[pair[0]][k]['mean'], result_array[pair[0]][k]['sterr'],result_array[pair[0]][k]['n'],
                                                                        result_array[pair[1]][k]['mean'], result_array[pair[1]][k]['sterr'],result_array[pair[1]][k]['n'],
                                                                        p, aou))
                except:
                    pass
                    #print('=======================================')
                    #print('%s (%s vs %s): This comparison has problem. Please check the data')
            elif datatype == 'population':
                try:
                    aou, p = stats.fisher_exact([[result_array[pair[0]][k]['pos'], result_array[pair[0]][k]['neg']], 
                                                 [result_array[pair[1]][k]['pos'], result_array[pair[1]][k]['neg']]
                                                 ])
                    print('=======================================')
                    print('%s (%s vs %s): \n%d of %d vs %d of %d, p=%f, aou=%f' % (k, group_titles[pair[0]], group_titles[pair[1]], 
                                                                        result_array[pair[0]][k]['pos'], result_array[pair[0]][k]['n'],
                                                                        result_array[pair[1]][k]['pos'], result_array[pair[1]][k]['n'],
                                                                        p, aou))
                except:
                    pass
                    #print('========================================')
                    #print('%s (%s vs %s): This comparison has problem. Please check the data')
                                    
#============================================================================================================
# description methods ==============================================================================================
#============================================================================================================
def description_ttest(result_list, key, group_titles, method = 'mann whitney u test'):
    if method == 'mann whitney u test':
        anamethod = stats.mannwhitneyu
    plist, __ = paired_analysis_idx(len(result_list))
    for pair in plist:
        cfront = ''
        cback = ''
        p = anamethod(np.array(result_list[pair[0]][key]['array']).astype(float), np.array(result_list[pair[1]][key]['array']).astype(float))[1]
        if p<0.05:
            cfront = '\033[0;31m'
            cback = '\033[0m'
        print('%s (n=%d) vs %s (n=%d) by %s: \n%f+/-%f vs %f+/-%f %sp = %f%s ' % (group_titles[pair[0]], result_list[pair[0]][key]['n'],
                                                                            group_titles[pair[1]], result_list[pair[1]][key]['n'], 
                                                                            method, 
                                                                            result_list[pair[0]][key]['mean'], result_list[pair[0]][key]['sterr'],
                                                                            result_list[pair[1]][key]['mean'], result_list[pair[1]][key]['sterr'],
                                                                            cfront, p, cback))
            

#============================================================================================================
# plot methods ==============================================================================================
#============================================================================================================
def ax_barplot(ax, result_array, title, group_titles):
    # result_array is an array containing dict results from different groups.
    # This function will use bar plot to show the figure.
    # ax is the subplot from plt.subplot(n,m)
    
    def label_diff(ax,pair,text,X,ylevel):
        x = (X[pair[0]]+X[pair[1]])/2
        y = ylevel
        ax.annotate(text, xy=(x,y), zorder=10, ha = 'center', va = 'center', backgroundcolor='w')
        ax.plot([X[pair[0]], X[pair[1]]], [y, y],'-',lw=1,color = 'grey', marker = TICKDOWN,markersize = 3)

    def pvalue_text(p):
        if p > 0.05:
            text = ''# % p
        elif p <= 0.05 and p > 0.01:
            text = '*'# % p
        elif p<=0.01 and p > 0.005:
            text = '**'# % p
        else:
            text = '***'# % p
        return(text)
    
    # This code should set before make subplot. It is the fundmental.
    # It works for jupyter notebook. But I'm not sure if it works to output.
    width = 3/(4*len(result_array)-1)

    colors = plt.cm.Pastel2(np.linspace(0,1,8)) # Fist get cmap Pastel2. Then define set to how many pieces.
    
    xlocation = 4*np.arange(len(result_array))*width/3 + 0.5*width
    ax.set_xticks(xlocation)
    ax.set_xticklabels(group_titles, rotation=45)

    yvalue = [x['mean'] for x in result_array]
    errvalue = [x['sterr'] for x in result_array]

    ax.bar(xlocation, yvalue, width, 
            yerr = errvalue,
            color=colors)
        
    ax.set_title(title)
    
    standardy = max([x['mean']+x['sterr'] for x in result_array])
    plist, level = paired_analysis_idx(len(result_array))
    levelempty = [0]*len(plist)
    
    for i in range(len(plist)):
        p = stats.mannwhitneyu(np.array(result_array[plist[i][0]]['array']).astype(float), 
                                np.array(result_array[plist[i][1]]['array']).astype(float))[1]
        
        if p < 0.05:
            levelempty[level[i]-1] = 1
            label_diff(ax, plist[i], pvalue_text(p), xlocation, standardy + standardy * 0.12 * sum(levelempty[0:level[i]]))
    
    ax.set_ylim(0.0, standardy + standardy * 0.12 * sum(levelempty) +0.1 * standardy)


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

def ax_polarbar(ax, result_arrays, title, group_title):
    arr = [x['percentage'] for x in result_arrays]
    N = len(arr)

    # width of each bin on the plot
    width = (2*np.pi) / N

    ax.bar([0, width, 2*width, 3*width], math.ceil(max(arr)/0.1)*0.1, width=width, alpha = 0.1)
    ax.bar([0, width, 2*width, 3*width], arr, width=0.8*width, alpha = 0.6, edgecolor = 'grey')

    # set the lable go clockwise and start from the top
    ax.set_theta_zero_location("N")
    # clockwise
    #ax.set_theta_direction(-1)
    ytop = math.ceil(max(arr)/0.1)*0.1

    # set the label
    #ticks = ['0:00', '3:00', '6:00', '9:00', '12:00', '15:00', '18:00', '21:00']
    xlocation = [0, width, 2*width, 3*width]#np.arange(N)*width
    ax.set_xticks([0, width, 2*width, 3*width])
    ax.set_xticklabels(group_title)
    ax.set_ylim = [0,ytop]
    ax.set_yticks(np.linspace(0,ytop,N+1)[0:-1])
    ax.set_yticklabels([])
    for i in range(N):
        ax.text(xlocation[i], max(arr[i]/2, 0.3), "{:.1%}".format(arr[i]), 
                horizontalalignment='center',
                verticalalignment='center')




