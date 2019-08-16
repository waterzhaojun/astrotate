# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:05:33 2019

@author: jzhao1
"""

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