import numpy as np
from .. import analysis
# ================================================================================
# analyse part ========================================================================
# ================================================================================

# To analyse single neuron ep data extracted from database, a good sequence is as below:
# 1. use decode_singleneuron_xxxx function to analyse the data you extracted from database.
# 2. use singleneuron_analysis function to transfer the df to a dict containing all comparisons.

def singleneuron_array_analysis(array, baseline, ci, **kwargs):
    """
    This function is used to analyse whether the response period have increased activity by 
    giving the response array.

    The array should be only response period. No baseline required. 
    The length of the array should be what you want to analyse.
    baseline and ci are for baseline period.
    If you need to define the activation/sensitization should happen in some range like 1h, 
    you can use kwargs basic_range, set a number like 4 to test if it happen in first 4 numbers.
    the activation / sensitization standard is baseline + ci
    """
    
    array = np.array(array)
    array1 = array > (baseline + ci)
    array2 = np.append([0], array1[:-1])
    array3 = np.append(array1[1:], [array1[-1]*array1[-2]])
    array_final = ((array1 * array2 + array1 * array3) > 0) *1
    
    result = {'immediate': array[0]>baseline+ci,
              'longterm_activation': np.sum(array_final) > 0
             }
    
    if 'basic_range' in kwargs.keys():
        test_period = array_final[0:kwargs['basic_range']]
        result['longterm_activation'] = np.sum(test_period) > 0

    if result['immediate']:
        if baseline != 0:
            result['immed_mag'] = array[0]/baseline
        else:
            result['immed_mag'] = array[0]/kwargs['alter_baseline']
    else:
        result['immed_mag'] = np.nan
        
    if result['longterm_activation']:
        result['delay'] = np.where(array_final == 1)[0][0]
        result['duration'] = np.sum(array_final)
        result['delta'] = np.sum(array*array_final)/result['duration']-baseline
        if baseline != 0:
            result['magnification'] = np.sum((array * array_final) / baseline)/result['duration']
        else:
            result['magnification'] = np.sum((array * array_final) / kwargs['alter_baseline'])/result['duration']
    else:
        result['delay'] = np.nan#None
        result['duration'] = np.nan#None
        result['magnification'] = np.nan#None
    
    return(result)


# The following two decode fn seems repeated with the function in jupyter lab (get_singleneuron_mech_df and get_singleneuron_spon_df). And I think it will be easier 
# that directly output a df instead of output dict then combine to a df. So these two decode fn will be depricated in the future.
def decode_singleneuron_mech(data, key, rootpath, response_points = 8):
    # This function is to help you build data df based on the data extracted from database
    # data is a dict extract from database.
    # key is the treatment key.
    # response_points defines how many response points you want to analyze.
    result = {}
    result['filepath'] = os.path.join(rootpath, data['file_path'])
    result['data'] = np.loadtxt(result['filepath'], delimiter = ',')
    treatpoint = data['treat_point'][key]
    
    result['th_data'] = result['data'][treatpoint:treatpoint+response_points,0] 
    result['th_baseline'] = data['result'][key]['th_baseline']
    result['th_ci'] = data['result'][key]['th_ci']
    
    result['th_sensitization'] = data['result'][key]['neuron_sensitization_th_whe']
    if result['th_sensitization'] == 'Y':
        tmp = singleneuron_array_analysis(result['th_data'], result['th_baseline'], result['th_ci'], basic_range = 8)
        result['th_delay'] = tmp['delay']
        result['th_duration'] = tmp['duration']
        result['th_magnification'] = tmp['magnification']
        result['th_area'] = tmp['duration'] * tmp['magnification']
    else:
        result['th_delay'] = np.nan
        result['th_duration'] = np.nan
        result['th_magnification'] = np.nan
        result['th_area'] = np.nan
    
    result['sth_data'] = result['data'][treatpoint:treatpoint+response_points,1] 
    result['sth_baseline'] = data['result'][key]['sth_baseline']
    result['sth_ci'] = data['result'][key]['sth_ci']
    result['sth_sensitization'] = data['result'][key]['neuron_sensitization_sth_whe']
    if result['sth_sensitization'] == 'Y':
        tmp = singleneuron_array_analysis(result['sth_data'], result['sth_baseline'], result['sth_ci'], basic_range = 8)
        result['sth_delay'] = tmp['delay']
        result['sth_duration'] = tmp['duration']
        result['sth_magnification'] = tmp['magnification']
        result['sth_area'] = tmp['duration'] * tmp['magnification']
    else:
        result['sth_delay'] = np.nan
        result['sth_duration'] = np.nan
        result['sth_magnification'] = np.nan
        result['sth_area'] = np.nan
        
    result['sensitized_by_all_force'] = ['N','Y'][1*(result['th_sensitization']=='Y' and result['sth_sensitization']=='Y')]
    result['sensitized_by_either_force'] = ['N','Y'][1*(result['th_sensitization']=='Y' or result['sth_sensitization']=='Y')]
    result['']
    return(result)

def decode_singleneuron_spon(data, key, rootpath, response_points = 18, **kwargs):
    """
    This function is to help you build data df based on the data extracted from database
    data is a dict extract from database.
    key is the treatment key.
    response_points defines how many response points you want to analyze.

    If you want to get a response period activity / sensitivity value, like time point 4 to
    time point 6 activity average value, set spon_activity_name_list which is the output label name list,
    and spon_activity_timepoint_list which is the required time points list (shape is n * 2).
    For sensitivity, you need to set th_value_name_list, th_value_timepoint_list, sth_value_name_list, 
    sth_value_timepoint_list.
    the element in timepoint_list should be [start, end] and count the sequence only in response period.
    """
    result = {}
    result['filepath'] = os.path.join(rootpath, data['file_path'])
    result['data'] = np.loadtxt(result['filepath'], delimiter = ',')
    treatpoint = data['treat_point'][key]
    
    result['res_data'] = result['data'][treatpoint:treatpoint+response_points] 
    result['baseline'] = data['result'][key]['neuron_activation_baseline_average']
    result['ci'] = data['result'][key]['neuron_activation_baseline_CI']

    if 'spon_activity_name_list' in kwargs.keys():
        if len(kwargs['spon_activity_name_list']) > 0:
            for i in len(kwargs['spon_activity_name_list']):
                result[kwargs['spon_activity_name_list'][i]] = result['res_data'][kwargs['spon_activity_timepoint_list'][i,0] : kwargs['spon_activity_timepoint_list'][i,1]] / result['baseline']
    
    try:
        result['immed_activation'] = data['result'][key]['neuron_immediate_activation']
    except:
        if result['res_data'][0] > (result['baseline'] + result['ci']):
            result['immed_activation'] = 'Y'
        else:
            result['immed_activation'] = 'N'
           
    result['activation'] = data['result'][key]['neuron_delay_activation']
    if result['activation'] == 'Y':
        tmp = singleneuron_array_analysis(result['res_data'], result['baseline'], result['ci'], basic_range = 12)
        result['act_delay'] = tmp['delay']
        result['act_duration'] = tmp['duration']
        result['act_magnification'] = tmp['magnification']
        result['act_area'] = tmp['duration'] * tmp['magnification']
    else:
        result['act_delay'] = np.nan
        result['act_duration'] = np.nan
        result['act_magnification'] = np.nan
        result['act_area'] = np.nan
        
    return(result)

def singleneuron_analysis(df):
    res = {}
    res['activation rate'] = analysis.build_chi_character(df['activation'].values)
    if 'immed_activation' in df.columns:
        res['immediate activation rate'] = analysis.build_chi_character(df['immed_activation'].values)
    
    if 'immed_activation_mag' in df.columns:
        res['immediate activation mag'] = analysis.build_ttest_character(df['immed_activation_mag'].values)

    if 'acti_duration' in df.columns:
        res['activation duration'] = analysis.build_ttest_character(df['acti_duration'].values)

    if 'acti_delay' in df.columns:
        res['activation delay'] = analysis.build_ttest_character(df['acti_delay'].values)

    if 'acti_magnitude' in df.columns:
        res['activation magnitude'] = analysis.build_ttest_character(df['acti_magnitude'].values)

    res['threshold sensitization rate'] = analysis.build_chi_character(df['th'].values)
    res['threshold sensitization duration'] = analysis.build_ttest_character(df['th_duration'].values)
    res['threshold sensitization delay'] = analysis.build_ttest_character(df['th_delay'].values)
    res['threshold sensitization magnitude'] = analysis.build_ttest_character(df['th_magnitude'].values)

    res['threshold sensitization delta change'] = analysis.build_ttest_character(df['th_deltachange'].values)

    res['super threshold sensitization rate'] = analysis.build_chi_character(df['sth'].values)
    res['super threshold sensitization duration'] = analysis.build_ttest_character(df['sth_duration'].values)
    res['super threshold sensitization delay'] = analysis.build_ttest_character(df['sth_delay'].values)
    res['super threshold sensitization magnitude'] = analysis.build_ttest_character(df['sth_magnitude'].values)
    
    res['all force sensitization duration'] = analysis.build_ttest_character(np.append(df['th_duration'].values, df['sth_duration'].values))
    res['all force sensitization delay'] = analysis.build_ttest_character(np.append(df['th_delay'].values, df['sth_delay'].values))

    if 'area_activated' in df.columns:
        res['activation AUC'] = analysis.build_ttest_character(df['area_activated'].values)
    
    res['threshold sensitization AUC'] = analysis.build_ttest_character(df['th_area_activated'].values)
    res['super threshold sensitization AUC'] = analysis.build_ttest_character(df['sth_area_activated'].values)

    tmp = [['N', 'Y'][(((x=='Y') + (y=='Y')) > 0)*1] for (x,y) in zip(df['th'].values, df['sth'].values) if x in ['Y', 'N'] and y in ['Y', 'N']]
    res['sensitization rate of any force'] = analysis.build_chi_character(np.array(tmp))

    tmp = [['N', 'Y'][(x=='Y') * (y=='Y')] for (x,y) in zip(df['th'].values, df['sth'].values) if x in ['Y', 'N'] and y in ['Y', 'N']]
    res['sensitization rate of both force'] = analysis.build_chi_character(np.array(tmp))

    tmp = [(x=='Y') + (y=='Y') for (x,y) in zip(df['th'].values, df['sth'].values) if x in ['Y', 'N'] and y in ['Y', 'N']]
    res['sensitization score'] = analysis.build_ttest_character(np.array(tmp))

    tmp = [x for x in df['th'].values if x in ['Y', 'N']] + [x for x in df['sth'].values if x in ['Y', 'N']]
    res['sensitization rate of each force'] = analysis.build_chi_character(np.array(tmp))
    return(res)
    