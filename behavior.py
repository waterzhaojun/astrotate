from scipy.io import loadmat
from astrotate import array as ay
import numpy as np

def running_array(matpath, binsize):
    # This function is to read the array data from mat file by giving the path.
    
    array = loadmat(matpath)['speed_array'][0].astype(np.float)
    array = array[1:] - array[0:-1]
    
    # remove shake. =======================
    # shake happens when animal almost don't move but the bar edge up and down on the IR probe.
    # So the number can't be more than 2. 
    # Our stragety is to seperate the whole array to pieces by 2 as threshold.
    def __removeshake__(array):
        array_shake = (abs(array) == 1) * array
        shake_idx = np.where(array_shake != 0)[0]
        
        if len(shake_idx) > 1:
            for i in range(len(shake_idx)-1):
                array_shake[shake_idx[i]] = array_shake[shake_idx[i]] - array_shake[shake_idx[i+1]]
            array_shake[shake_idx[-1]] = array_shake[shake_idx[-1]] - array_shake[shake_idx[-2]]
            array = array* (array_shake == 0)
        return(array)
    
    pieceidx = np.where(abs(array) > 1)[0]
    pieceidx = np.concatenate(([0], pieceidx, [len(array)]))
    for i in range(len(pieceidx)-1):
        if len(array[pieceidx[i]:pieceidx[i+1]]) > 2:
            tmppiece = array[pieceidx[i]:pieceidx[i+1]]
            array[pieceidx[i]:pieceidx[i+1]] = __removeshake__(tmppiece)
    
    # bint the array
    array = abs(array)
    array2 = ay.bint1D(array, binsize)
    
    return(array2)

def running_analysis(array):
    # This function is to analyse one trial's running data and output a dict
    # Each point in the array suppose represent 1 sec.

    # define the analysis parameters
    bout_gap = 3 # If the animal stop running for 3 sec. we call it the end of this bout.
    
    result = {}
