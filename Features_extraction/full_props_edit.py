# -*- coding: utf-8 -*-

"""
Function extracts features for a series of chronological images and outputs two dataframes corresponding to all cells 
and the cells with full tracks. 
inputs:
    raw_img_GFP: GRAYSCALE image of GFP channel
    raw_img_TRITC: GRAYSCALE image of TRITC channel
    seg_mask: mask for each cell- this will be used as reference for extracting features for whole cell and identifying
              the corresponding cell for each puncta. 
    GFP_puncta_mask: puncta mask for autophagosomes. 
    AL_puncta_mask: puncta mask for autolysosomes. 
    cell_to_measure: list of cells that are full tracked for the entire timecourse of the experiments. 
                    Track and mask labels are necessary. (the output from full_btrack algorithm)
outputs:
    final_cell_features: Features of all cells in the image
    fulltrack_cell_features: features of all cell with full tracks ( this is just a subset of final_cell_features data)
"""

from features_extract import feature_extract
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from watershed_puncta import watershed_fun
from assign_puncta_to_cell import assign_puncta_to_cell
from puncta_cell_summary import puncta_cell_summary

def full_props(raw_img_GFP, raw_img_TRITC, seg_mask, GFP_puncta_mask,AL_puncta_mask,cell_to_measure):

    #making sure the same images and segmentation files are loaded. 
    raw_label_pos_GFP=raw_img_GFP.rfind('_')-5
    raw_label_GFP=raw_img_GFP[raw_label_pos_GFP:-4] #removing the extension
    
    raw_label_pos_TRITC=raw_img_TRITC.rfind('_')-5
    raw_label_TRITC=raw_img_TRITC[raw_label_pos_TRITC:-4] #removing the extension
    
    mask_label_pos= seg_mask.rfind('_')-5
    mask_label=seg_mask[mask_label_pos:-4] #comparing the well and postion and time point
    
    pmask_label_pos_AP=GFP_puncta_mask.rfind('_')-5
    pmask_label_AP=GFP_puncta_mask[pmask_label_pos_AP:-4] #puncta has a prefix GFP_
    
    pmask_label_pos_AL=AL_puncta_mask.rfind('_')-5
    pmask_label_AL=AL_puncta_mask[pmask_label_pos_AL:-4] #puncta has a prefix GFP_
    
    if raw_label_GFP== mask_label and mask_label==pmask_label_AP and pmask_label_AL==pmask_label_AP and  pmask_label_AL==raw_label_TRITC:
        print('match found: '+ raw_label_GFP)
        #loading all images 
        cmask=np.loadtxt(seg_mask)
        
       
        pmask_AP= watershed_fun(GFP_puncta_mask,zplane=0)
        pmask_AL= watershed_fun(AL_puncta_mask,zplane=2)
        raw_GFP=plt.imread(raw_img_GFP)
        raw_TRITC= plt.imread(raw_img_TRITC)
        
        #cell features/props
        cname=seg_mask[mask_label_pos:-4]
        cond_name=[cname]*int(np.max(cmask))
        cond_name=pd.DataFrame(cond_name,columns=["condition"])
        temp_features= feature_extract(cmask,raw_GFP) #extracting all cellular features. 
        ctemp_df= pd.concat([cond_name, temp_features], axis=1)
               
        #Autophagosome props
        cpname_AP=GFP_puncta_mask[pmask_label_pos_AP:-4]
        cond_name_AP=pd.DataFrame([cpname_AP]*int(np.max(pmask_AP)),columns=["condition_AP"])
        ptemp_features_AP= feature_extract(pmask_AP,raw_GFP) #extracting all AP features. 
        ptemp_AP_df= pd.concat([cond_name_AP, ptemp_features_AP], axis=1)
        
        #Autolysosome props
        cpname_AL=AL_puncta_mask[pmask_label_pos_AL:-4]
        cond_name_AL=pd.DataFrame([cpname_AL]*int(np.max(pmask_AL)),columns=["condition_AL"])
        ptemp_features= feature_extract(pmask_AL,raw_TRITC) #extracting all AL features. 
        ptemp_AL_df= pd.concat([cond_name_AL, ptemp_features], axis=1)
        

        #assigning cell number for AP and AL
        assigned_info=[]
        label_order=['AP','AL']   
        for idx,item in enumerate([ptemp_AP_df,ptemp_AL_df]):
            info=assign_puncta_to_cell(item,cell_mask=cmask)
            assigned_info.append(puncta_cell_summary(puncta_info_df=info,cell_props_df=ctemp_df,label_name=label_order[idx]))
         
        #combinign cellular level info with puncta_summary info
        if assigned_info[0].isnull().values.any()== False and assigned_info[1].isnull().values.any()== False:
            final_cell_features=[]
            cell_data= ctemp_df.reset_index().drop(columns=['index'])
            puncta_data_AP=assigned_info[0].reset_index().drop(columns=['index'])
            puncta_data_AL=assigned_info[1].reset_index().drop(columns=['index'])
            if (cell_data['condition'].loc[0]==puncta_data_AP['Condition-Check'].loc[0]) and (cell_data['condition'].loc[0]==puncta_data_AL['Condition-Check'].loc[0]): #checking if the same cell is combined
                final_cell_features=pd.concat([cell_data,puncta_data_AP,puncta_data_AL],axis=1)
            else:
                print('Images dont match for:'+str(cell_data['condition']))
        else:
            print('NA values are not removed after puncta summary for each cell')
        
            
        #selecting only full track cells. 
        image_label=final_cell_features['condition'].loc[0]+'.txt'
        subset=cell_to_measure[cell_to_measure['filename'].str.contains(image_label)].sort_values(by=['mask_ID'])
        subset_data=final_cell_features.loc[final_cell_features['label'].isin(subset['mask_ID'])].sort_values(by=['label'])
        fulltrack_cell_features=pd.concat([subset.reset_index().drop(columns=['index']),subset_data.reset_index().drop(columns=['index'])],axis=1)

    else:
        print('cell Segmentation mask and raw images are not same')
    return final_cell_features, fulltrack_cell_features 