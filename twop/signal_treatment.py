import numpy as np
from oasis.functions import deconvolve
import copy

def estimate_baseline(array, window_size):
    array2 = np.append([0], array[1:]-array[:-1])
    std = np.quantile(array2,0.75)
    idx = np.where(np.absolute(array2)>std)
    array2 = copy.copy(array)
    array2[np.array(idx).astype(int)] = np.nan
    baseline = np.array([])
    for i in range(len(array2)):
        start = int(max(0,i-window_size/2))
        end = int(min(max(window_size, i+window_size/2), len(array2)))
        tmp = array2[start:end]
        #std=np.std(tmp)
        #tmp=tmp[np.where(tmp>std)]
        
        #tmp = tmp[~np.isnan(tmp)]
        baseline = np.append(baseline, np.nanquantile(tmp, 0.25))
    
    return(baseline)

def deconvolve_astrocyte_signal(array, window_size, standard, **kwargs):
    """
    standard: the threshold value of deconvolved array that considered as a activation.
    window_size: the size of calculate window.
    overpoints_limit: optimize the baseline until the new edited overpoints less than this percentage. it is related with window size.
    return: is dff, deconvolved array, baseline
    """
    baseline = estimate_baseline(array, window_size)
    dff = (array-baseline)/baseline
    tmp = deconvolve(dff, penalty = 1)
    deconv = tmp[0]
    deconv[deconv<0] = 0

    return(dff, deconv, baseline)

def analyze_astrocyte_deconvolve_signal(array, standard):
    a = (array > standard)*1
    a_idx_start = np.array([])
    a_idx_end = np.array([])
    a_max = np.array([])
    a_max_idx = np.array([])
    a_duration = np.array([])
    tmp = [0,1]
    tmp_idx = np.array([])
    for i in range(len(a)-1):
        if np.sum(a[i:i+2] == tmp) == 2:
            tmp_idx = np.append(tmp_idx, i)
            tmp = np.flip(tmp)
        if len(tmp_idx) == 2:
            tmp_idx = tmp_idx.astype(int)
            a_idx_start = np.append(a_idx_start, tmp_idx[0])
            a_idx_end = np.append(a_idx_end, tmp_idx[1])
            a_max = np.append(a_max, np.max(array[tmp_idx[0]:tmp_idx[1]]))
            a_max_idx = np.append(a_max_idx, tmp_idx[0] + np.argmax(array[tmp_idx[0]:tmp_idx[1]]))
            a_duration = np.append(a_duration, tmp_idx[1]-tmp_idx[0])
            tmp_idx = np.array([])
    
    return(a_idx_start, a_idx_end, a_max, a_max_idx, a_duration)
