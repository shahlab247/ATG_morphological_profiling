# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 10:34:52 2022
#saving puncta mask as text file. 
The inputs: 
    pmask= masks as an array. 
    fname- name you want to save as masks as(often its the same as filename of pmasks)
    label- prefix of the fnanme
    path- folder to store the masks in the format of text files 
output:
    text files with label_fname 


"""
import numpy as np

def savepmask_to_txt(pmask,fname,label,path):
    char="\\"
    position=fname.rfind(char)-len(fname)+1
    fname=fname[position:-4]
    fname=label+'_'+fname
    floc=path+fname+".txt"
    np.savetxt(floc, pmask,fmt='%d')