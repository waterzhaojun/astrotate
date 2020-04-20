from . import ep
from .. import analysis, array as ay
import numpy as np


# ===========================================================================================
# ====== analysis part ======================================================================
# ===========================================================================================
def csd_period_analysis(array, character_dict, do_smooth = True):
    """
    To analyse multiunit response in CSD
    array is the raw data containing baseline and response period
    This analysis will refer to the position of CSD wave peak, and output different arrays
    based on the pre peak and post peak duration.
    
    character_dict is the dict containing informations including:
    -- baseline length
    -- estimated impossible duration after CSD. When measure the peak, this period will be ignored in case some super active noise happened.
    -- analyse duration after peak. Define how long after peak will be analysed.
    -- estimated CSD end timepoint after pinprick. The max timepoint of which CSD peak will be sure past the view, like 300 sec after pinprick.
    
    post_peak_response is from peak point to the duration of we want to analysis
    whole_timecourse is the whole duration from we wanted prepeak length to the after peak analysis length.
    """
    result = {}
    
    bint = character_dict.get('bint', 1)

    # This part output some basic points
    tmpstart = character_dict['baseline_length'] + character_dict['estimated_impossible_duration']
    tmpend = character_dict['baseline_length'] + character_dict['estimated_csd_end_timepoint']
    peakpoint = np.argmax(array[tmpstart:tmpend]) + tmpstart
    result['peakpoint'] = peakpoint
    
    # this array just output after peak array
    after_peak_array = array[peakpoint+1:]
    if do_smooth:
        after_peak_array = ay.smooth(after_peak_array)
    after_peak_array = ay.bint1D(after_peak_array, bint)#, window_length = 5, polyorder = 3)
    result['post_peak_response'] = after_peak_array
    
    # This array output a specific period define by analysis_period, refer to the peak. 
    # minus num means before peak. 
    # Be sure this period is not too short if you want to smooth it. Otherwise there will be error.
    if character_dict.get('analysis_period', False):
        timecourse_start = peakpoint + character_dict['analysis_period'][0]
        timecourse_end = peakpoint + character_dict['analysis_period'][1]
        whole_array = array[timecourse_start: timecourse_end]
        if do_smooth:
            whole_array = ay.smooth(whole_array)
        result['analysis_period'] = ay.bint1D(whole_array, bint)
    return(result)

# ===========================================================================================
# ====== polt part ==========================================================================
# ===========================================================================================
def timecourse(array, ax, **kwargs):
        
    mean_array = np.mean(array, axis = 0)  
    error_array = np.std(array, axis = 0)/np.shape(array)[0]
    
    marker = kwargs.get('marker', '.')
    alpha = kwargs.get('alpha', 0.5)
    color = kwargs.get('color', 'gray')
    timecourse_xlabels = kwargs.get('xticks', np.arange(np.shape(array)[1]))

    ax.errorbar(
        timecourse_xlabels, mean_array, yerr=error_array, alpha = alpha, color = color,
        marker = marker, ms=1
    )#, fmt='|')
    

class Multiunit(ep.Result):
    # the whole part of this class is not ready yet.
    def __init__(self, querydf):
        """
        df for Multiunit should be three columns df including: date, group, data.
        The data of each row should be an array.
        character is a dict 
        """
        super().__init__('multiunit', querydf)
        # self.character = character
        # self.result=self.create_result()
        
    def create_result(self):
        # This function is not ready yet
        result = {}
        peak_arrive_duration_array = np.array([])
        
        for i in range(len(self.df)):
            tmp = self.csd_period_analysis(self.df.loc[i, 'data'], self.character)
            # no need to calculate baseline, it's already normed
            peak_arrive_duration_array = np.append(peak_arrive_duration_array, tmp['peakpoint'])
            
        result['peak_arrive_duration'] = build_ttest_character(peak_arrive_duration_array)
        return(result)
        
    