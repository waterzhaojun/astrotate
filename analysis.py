import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
from matplotlib.markers import TICKDOWN
from matplotlib.ticker import PercentFormatter
from datetime import datetime
import os
import pdfkit



def check_df_group_num(df):
    lss = list(set(df.group))
    lss.sort()
    for i in lss:
        tmp = df.query('group == @i')
        print('%s number = %d' % (i,len(tmp)))
    
def build_df_from_res_arrays(res_arrays,key,group_titles):
    """
    Sometimes a df need to use for analysis or sns plot. So this function is to create a df
    from res dict by giving key.
    So far I just tested float numbers, didn't test for chi square needed numbers.
    This is just a temperay function. I may build a better one in the future.
    """
    df = pd.DataFrame(columns = ['group','value'])
    for i in range(len(res_arrays)):
        tmpre = res_arrays[i]
        tmplen = len(tmpre[key]['array'])
        df = pd.concat([df,pd.DataFrame(data={'group':[group_titles[i]]*tmplen,
                                             'value':tmpre[key]['array']
                                            })],axis = 0)
    return(df)

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
    
def paired_analysis_idx_with_control(array_length, control_idx):
    result = []
    all_idx = np.arange(array_length).astype(int)
    all_idx = np.delete(all_idx, control_idx)
    for i in all_idx:
        result.append([control_idx, i])
    return(result)

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

def df2res(df, analyze_columns, analyze_method, key_name=None, **kwargs):
    # analyze method is choose from either 'ttest' or 'chi'
    # This is an important function. Updated at 8/12/2020.
    assert len(analyze_columns) == len(analyze_method)
    if key_name is not None:
        assert len(analyze_columns) == len(key_name)
        keys = key_name
    else:
        keys = analyze_columns
    result = {}
    for i in range(len(analyze_columns)):
        if analyze_method[i] == 'ttest':
            result[keys[i]] = analysis.build_ttest_character(df.loc[:,analyze_columns[i]].values)
        elif analyze_method[i] == 'chi':
            result[keys[i]] = analysis.build_chi_character(
                df.loc[:,analyze_columns[i]].values,
                posSymbol = kwargs.get('posSymbol', 'Y'),
            )
    return(result)

def analysis_between_groups_description(result_array,group_titles,savepath,title,**kwargs):   
    """
    This function is to create a pdf showing multiple result dict comparing result.
    The default value compare method is mannwhitney u test. You can change it by setting value_compare_method.
    The default population compare method is fisher exact. You can change it by setting population_compare_method.
    """
    value_compare_method = kwargs.get('value_compare_method', stats.mannwhitneyu)
    value_compare = lambda array, fn:fn(array[0],array[1])
    population_compare_method = kwargs.get('population_compare_method', stats.fisher_exact)
    population_compare = lambda array, fn:fn(array)

    html =  "<html>\n<head></head>\n<style>p { margin: 0 !important; }</style>\n<body>\n"

    #title = "Single neuron activation sensitization analysis"
    html += '\n<center><h1>' + title + '</h1></center>\n'
    html += '\n<center>Last update: ' + datetime.today().strftime('%B-%d-%Y') + '</center>\n'
    html += '\n'
    html += '<p>Note: In this report, the value comparison was measured by %s, the population comparison was measured by %s.' % (value_compare_method.__name__, population_compare_method.__name__)
    html += '<p>'

    if len(result_array) != len(group_titles):
        raise Exception('result_array and group_titles should have same length.')
    
    if kwargs.get('control',False):
        control_idx = result_array.index(kwargs['control'])
        paired_compair = paired_analysis_idx_with_control(len(result_array), control_idx)
    else:
        paired_compair = paired_analysis_idx(len(result_array))[0]
    keys = list(result_array[0].keys())
    #if os.path.exists(savepath):
    #    print('overwrite old analysis file...')
    #    os.remove(savepath)
    tmpsavepath = savepath[0:-3]+'html'
    with open(tmpsavepath, 'a+') as f:
        f.write(html)
        for k in keys:
            for pair in paired_compair:
                datatype = result_array[pair[0]][k]['dataType']
                if datatype == 'avgStd':
                    try:
                        sta,p = value_compare(
                            [np.array(result_array[pair[0]][k]['array']).astype(float), 
                            np.array(result_array[pair[1]][k]['array']).astype(float)],
                            value_compare_method
                        )
                        f.write('<p>=============================================')
                        tmp = '%s (%s vs %s): \n%f+/-%f n=%d vs %f+/-%f n=%d, pvalue=%f, statistic=%f' % (k, group_titles[pair[0]], group_titles[pair[1]], 
                                                                            result_array[pair[0]][k]['mean'], result_array[pair[0]][k]['sterr'],result_array[pair[0]][k]['n'],
                                                                            result_array[pair[1]][k]['mean'], result_array[pair[1]][k]['sterr'],result_array[pair[1]][k]['n'],
                                                                            p, sta)
                        if p < 0.05:
                            tmp = '<font color="red"><b>' + tmp + '</b></font>'
                        f.write('<p>'+tmp)
                    except:
                        f.write('<p>=============================================')
                        tmp = 'There is en error when comparing %s (%s vs %s): \n%f+/-%f n=%d vs %f+/-%f n=%d. Please comfirm the value.' % (
                            k, group_titles[pair[0]], group_titles[pair[1]], 
                            result_array[pair[0]][k]['mean'], result_array[pair[0]][k]['sterr'], result_array[pair[0]][k]['n'],
                            result_array[pair[1]][k]['mean'], result_array[pair[1]][k]['sterr'],result_array[pair[1]][k]['n'])
                        tmp = '<font color="gray"><b>' + tmp + '</b></font>'
                        f.write('<p>'+tmp)

                elif datatype == 'population':
                    try:
                        sta, p = population_compare(
                            [[result_array[pair[0]][k]['pos'], result_array[pair[0]][k]['neg']], 
                            [result_array[pair[1]][k]['pos'], result_array[pair[1]][k]['neg']]],
                            population_compare_method
                        )
                        f.write('<p>=============================================')
                        tmp = '%s (%s vs %s): \n%d of %d vs %d of %d, p=%f, statistic=%f' % (k, group_titles[pair[0]], group_titles[pair[1]], 
                                                                            result_array[pair[0]][k]['pos'], result_array[pair[0]][k]['n'],
                                                                            result_array[pair[1]][k]['pos'], result_array[pair[1]][k]['n'],
                                                                            p, sta)
                        if p < 0.05:
                            tmp = '<font color="red"><b>' + tmp + '</b></font>'
                        f.write('<p>'+tmp)
                    except:
                        f.write('<p>=============================================')
                        tmp = 'There is en error when comparing %s (%s vs %s): \n%d of %d vs %d of %d. Please comfirm the value.' % (
                            k, group_titles[pair[0]], group_titles[pair[1]], 
                            result_array[pair[0]][k]['pos'], result_array[pair[0]][k]['n'],
                            result_array[pair[1]][k]['pos'], result_array[pair[1]][k]['n'])
                        tmp = '<font color="gray"><b>' + tmp + '</b></font>'
                        f.write('<p>'+tmp)
                        
        f.write("\n</body>\n</html>")   
    pdfkit.from_file(tmpsavepath, savepath)
    os.remove(tmpsavepath)


#============================================================================================================
# description methods ==============================================================================================
#============================================================================================================
def description_ttest(result_list, key, group_titles, method = 'mann whitney u test'):
    """
    I think I will deprecate this function. I need a function to help group description function print ttest result.
    But the input just need array and compare function, not result_list. I will deprecate it when I finished building 
    a new function.
    """
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


class Result():
    """
    I am building this class. Not finish yet.
    """
    def __init__(self,df, group_title):
        self.df = df
        self.group = group_title
        # self.result = self.analyze() 

    def analyze(self):
        return(None)
