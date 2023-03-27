# -*- coding: utf-8 -*-
"""
#function take a labeled imaged and raw image and extracts properties for individual objects in the labelled image. 
output:
    dataframe containing features for individual objects in the labeled image. 
"""
import numpy as np
import pandas as pd
from skimage.measure import regionprops_table
from additional_features import haralick_summary, zernike_moments

def feature_extract(label_img, int_img):
    label_img=label_img.astype(int)
    int_img=int_img.astype(int)
    props = ['label','bbox','centroid','area', 'bbox_area', 'convex_area', 'filled_area', 'major_axis_length', 'minor_axis_length',
                  'eccentricity','euler_number', 'extent', 'feret_diameter_max','inertia_tensor', 'inertia_tensor_eigvals', 'max_intensity', 'mean_intensity', 'min_intensity',
                  'orientation', 'perimeter', 'perimeter_crofton','solidity']
        
    df= regionprops_table(label_img,int_img,properties=props)
    reg_props=pd.DataFrame(df) #for exporting
    rg_props=pd.DataFrame(df).to_numpy()
    
    
       
    puncta_properties_dictionaries = []
    for cell in range(np.max(label_img)):
        cell_label=int(rg_props[cell][0])
        minr,minc,maxr,maxc=int(rg_props[cell][1]), int(rg_props[cell][2]),int(rg_props[cell][3]),int(rg_props[cell][4])
        cropped_mask= label_img[minr:maxr,minc:maxc] 
        cropped_img= int_img[minr:maxr,minc:maxc]
        if int(np.max(cropped_mask))==cell_label and int(np.min(cropped_mask))==0 and len(set(cropped_mask.ravel().tolist()))==2:
            #print("cell label"+ str(cell_label)+' correct')
            segmented_cell= np.multiply(cropped_mask,cropped_img)/cell_label
        else:
            cropped_mask[cropped_mask!=cell_label]=0
            segmented_cell= np.multiply(cropped_mask,cropped_img)/cell_label
              
        #using the cropped image of each cell to extract haralick features. 
        props = regionprops_table(cropped_mask.astype(int),segmented_cell.astype(int))
        props.update(haralick_summary(segmented_cell))
        
        #zernike moments
        radius_value=rg_props[cell][11]/2 # 0.5 times major axis length, 11 is the major axis length
        props.update(zernike_moments(cropped_mask, segmented_cell,radius_value))
        puncta_properties_dictionaries.append(props)

    extra_df = (pd.DataFrame(puncta_properties_dictionaries))
    extra_df= extra_df.drop(columns=['label','bbox-0','bbox-1','bbox-2','bbox-3'])
    final_df= pd.concat([reg_props, extra_df], axis=1)
    
    #for converting any arrays into floats. 
    for column_name in final_df.columns:
        if column_name=='condition':
            pass
        else:
            if str(final_df[column_name].dtype)=='object':
                #print(column_name)
                try:
                    final_df[column_name]=final_df[column_name].astype(float)
                except ValueError:
                    #new_list=[]
                    for j in range(len(final_df[column_name])):
                        if len(final_df[column_name][j])==0:
                            final_df[column_name][j]=np.nan
                            #print(final_df[column_name][j].dtype)
                            #new_list.append(final_df[column_name][j])
                        else:
                            final_df[column_name][j]=final_df[column_name][j][0]#.astype(float)
                            #print(final_df[column_name][j].dtype)
                            #new_list.append(final_df[column_name][j][0])
                    #final_df[column_name][j]=pd.Series(new_list)
                
    return final_df   