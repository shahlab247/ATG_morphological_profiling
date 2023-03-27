# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 20:11:33 2022

@author: bniti
"""
import fnmatch

#function selects images for pre and post treatment
#order= order of images 
#files_list= name of files containing all timpoints
#pre_min corresponds to the lowest timpoint for pretreatment before -20 mins timepoint. 3 is the default so it would select -40, -60 and -80
#max_post=max timepoint you want to analyze after treatment. Selects all treatments below this time point. Default is 31. 
#output is a list of   
def selected_wells(order, files_list,pre_min=3,max_post=31,postname='posttreatment'): 
    
    files_list=sorted(files_list)
    select_files=[]
   
    count=0  #to keep count of pretreatment files
    point=0  #to keep count of min timepoint 
    #figuring out the first time point for post treatment. 
    timepoints=[]
    temp_select=[]
    for idx, cond in enumerate(order):
        if (cond in postname)==False:
            for filename in files_list:
                if fnmatch.fnmatch(filename, cond):
                   temp_select.append(filename)
        elif (cond in postname)==True:
            count= len(temp_select) #track no of pretreatment files
            for filename in files_list:
                if fnmatch.fnmatch(filename, cond):
                    
                    try:
                        t_min=int(filename[-6:-4])
                        timepoints.append(t_min)
                    except ValueError:
                        t_min=(filename[-6:-4])
                        t_min=int(t_min[-1])
                    if t_min<=max_post:
                        temp_select.append(filename)

                   
    select_files=temp_select[count-pre_min-1:] #just getting 4 images from pretreatment
                
    return select_files

