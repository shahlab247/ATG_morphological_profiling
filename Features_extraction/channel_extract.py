# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 12:51:07 2022

@author: Nitin Beesabathuni

#definining a function to extract individual channels and sort them according to the filename. Can extract upto 2 channels at the same time. 
#the input are 1) folder_location= enter the path to the folder that contains all files. 
#GFP_name= enter the keyword of the GFP files in the format of *GFPname*.tif(file extension is needed), similarly TRITC. 
#important = if you  dont want one of the channels please mention the argument as none. For example, for extracting tritc but not GFP
#the syntax would be = channel_extract("folder_location", "None", TRITC_files)
#the other way of doing it is mentioned the argument name and then providing the input. For example, 
#the syntax would like = channel_extract("folder_location", TRITC_name="TRITC_NSB")

#outputs
    #returns a two lists of GFP and TRITC filenames
"""
#Packages
import os
import fnmatch

def channel_extract(folder_location, GFP_name='None', TRITC_name='None'):
    files = []
    #folder_location= "r"+folder_location.str
    #GFP_name=GFP_name.str
    #TRITC_name= TRITC_name.str
    #enter the folder path which contains the tif files. 
    if GFP_name =='None' and TRITC_name =='None':
        print("No argument for channel extraction was provide. Null list are generated")
    if GFP_name =='None' or TRITC_name == 'None':
        if GFP_name=='None':
            print("No arguments for GFP channel was provided")
        else:
            print("No arguments for TRITC channel was provided")
    input_dir = os.path.dirname(folder_location)
    for f in os.listdir(input_dir):
        filename = os.path.join(input_dir, f)
        files.append(filename)
    
    #Extracting GFP files
    GFP_files=[]
    for file in files:
        if fnmatch.fnmatch(file, GFP_name):
            GFP_files.append(file)
    GFP_files= sorted(GFP_files)
    
    #Extracting TritC files
    TRITC_files=[]
    for file in files:
        if fnmatch.fnmatch(file, TRITC_name):
            TRITC_files.append(file)
    TRITC_files= sorted(TRITC_files)

    return GFP_files, TRITC_files