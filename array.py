# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:05:33 2019

@author: jzhao1
"""
import math
import numpy as np

def bint1D(array, binsize, setint = False):
    # smooth 1D array
    remains = len(array) % binsize
    array1 = np.reshape(array[0:len(array)-remains], [-1, binsize])
    array2 = np.mean(array1, axis = 1)
    if remains > binsize/2:
        array2 = np.append(array2, np.mean(array[-remains:]))
    
    if setint:
        array2 = np.around(array2).astype(int)
    return(array2)

def smooth(x,window_len=15,window='hanning'):
    # https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
    
    """
    smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.
    """

    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[math.floor(window_len/2):-math.floor(window_len/2)]

