import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import scipy.stats as stats

def paired_analysis_idx(array_length):
    """
    This function is to grap two element in each round. 
    The title should has the same length as array representing 
    array element title
    """
    # total_num = array_length * array_length / 2
    output = []
    for i in range(array_length):
        for j in range(i+1, array_length):
            output.append([i,j])
    return(output)

def group_value_to_dict_element(array):
    res = dict()
    array = array[~pd.isnull(array)]
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

def analysis_between_groups(result_array, group_titles):
    """
    When we analyse a group of data, we will get a dict containing series
    of analysis feature. If the analysis method is the same, different group
    will get a dict with same key words. This function is to plot along
    the keys to show different between groups. Right now it only take two groups.
    """
    keys = list(result_array[0].keys())
    
    for key in keys[1:]:
        print(key)
        
        fig, ax = plt.subplots()
        width = 1/len(result_array)
        for i in range(len(result_array)):
            ax.bar(i/len(result_array), result_array[i][key]['mean'], width, yerr = result_array[i][key]['sterr'])
            
        ax.set_title(key)
        ax.legend(group_titles)
        plt.show()

        plist = paired_analysis_idx(len(result_array))
        for pcompare in plist:
            p = stats.mannwhitneyu(np.array(result_array[pcompare[0]][key]['array']).astype(float), 
                                   np.array(result_array[pcompare[1]][key]['array']).astype(float))
            
            print('%s vs %s: p = %f' % (group_titles[pcompare[0]], group_titles[pcompare[1]], p[1]))
        print('=======================================================')