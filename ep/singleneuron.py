import numpy as np
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
        if baseline != 0:
            result['magnification'] = np.sum((array * array_final) / baseline)/result['duration']
        else:
            result['magnification'] = np.sum((array * array_final) / kwargs['alter_baseline'])/result['duration']
    else:
        result['delay'] = np.nan#None
        result['duration'] = np.nan#None
        result['magnification'] = np.nan#None
    
    return(result)