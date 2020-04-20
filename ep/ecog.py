from . import ep
from .. import analysis, array as ay
import numpy as np
import copy

# ===========================================================================================
# ====== analysis part ======================================================================
# ===========================================================================================


# ===========================================================================================
# ====== plot part ======================================================================
# ===========================================================================================
def timecourse(array, ax, **kwargs):
    ax.plot(array, color = 'gray')
    if kwargs.get('showpeak', False):
        peaks = ay.findpeak(array, need_above_zero=True)
        peakcolor = kwargs.get('peakcolor', 'red')
        ax.scatter(np.argwhere(peaks).flatten(), array[peaks], color = peakcolor)
    if kwargs.get('showtrough', False):
        trough = ay.findtrough(array, need_below_zero=True)
        troughcolor = kwargs.get('troughcolor', 'blue')
        ax.scatter(np.argwhere(trough).flatten(), array[trough], color = troughcolor)

# ===========================================================================================
# ====== treatment part ======================================================================
# ===========================================================================================
def timecourse_treatment(array, bintsize, method = 'abs_average'):
    tmp = copy.deepcopy(array)
    if method == 'abs_average':
        # This method is used in paper:
        # https://www.ncbi.nlm.nih.gov/pubmed/29538620
        # You can check Fig 4 description.
        tmp = ay.bint1D(np.absolute(tmp), bintsize)
        
    elif method == 'positive_average':
        mask = np.argwhere(tmp<=0).flatten()
        np.put(tmp, mask, np.nan)
        tmp = ay.bint1Dnan(tmp, bintsize)
        
    elif method == 'negative_average':
        mask = np.argwhere(tmp>=0).flatten()
        np.put(tmp, mask, np.nan)
        tmp = ay.bint1Dnan(tmp, bintsize) * -1
        
    elif method == 'positive_peak':
        mask = ay.findpeak(tmp, need_above_zero = True)
        mask = np.argwhere(mask == False)
        np.put(tmp, mask, np.nan)
        tmp = ay.bint1Dnan(tmp, bintsize)
        
    elif method == 'negative_peak':
        mask = ay.findtrough(tmp, need_below_zero = True)
        mask = np.argwhere(mask == False)
        np.put(tmp, mask, np.nan)
        tmp = ay.bint1Dnan(tmp, bintsize) * -1

    elif method == 'avg_std':
        tmp = np.absolute(tmp)
        remain = len(tmp)%bintsize
        if remain > 0:
            tmp = tmp[:-remain]
        tmp = np.reshape(tmp, [bintsize, -1], order = 'F')
        tmp = np.std(tmp, axis = 0)

    elif method == 'avg_conf':
        tmp = np.absolute(tmp)
        remain = len(tmp)%bintsize
        if remain > 0:
            tmp = tmp[:-remain]
        tmp = np.reshape(tmp, [bintsize, -1], order = 'F')
        tmp = np.apply_along_axis(ay.conf,0, tmp)[1,:]
        
    elif method == 'spike_length':
        pass # So far no idea to identify each spike and calculate top to bottom height
    
    return(tmp)

# ===========================================================================================
# ====== class part ======================================================================
# ===========================================================================================
class Ecog(ep.Result):
    # the whole part of this class is not ready yet.
    def __init__(self, querydf):
        """
        df for Multiunit should be three columns df including: date, group, data.
        The data of each row should be an array.
        character is a dict 
        """
        super().__init__('ecog', querydf)
        # self.character = character
        # self.result=self.create_result()
        
    