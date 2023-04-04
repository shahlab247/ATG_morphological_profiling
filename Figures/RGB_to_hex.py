# -*- coding: utf-8 -*-
import numpy as np

#function for converting RGB values to hex values
def RGB(RGB_val):
    hex_val=np.divide(RGB_val,255)
    return hex_val
