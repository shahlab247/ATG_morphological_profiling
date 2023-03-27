# -*- coding: utf-8 -*-
"""
#this function assigns the cell number for each puncta based on the centriod coordinates of the puncta 
#and the corresponding cell number for that specific coordinate in the cell mask.
#inputs:
    #ptemp_df- dataframe containing puncta mask information. Each row should be a puncta/object the corresponding props.
    #cell_mask- is the cell mask image in the form a 2D-array
    #x, y are the poisition/column numbers of the centriod coordinates of each puncta. Default is 6 and 7 """

import pandas as pd

def assign_puncta_to_cell(ptemp_df,cell_mask,x=6,y=7): #6 and 7 are puncta centriod coordinates for each puncta 
    #assigning puncta to cell
    search_list=ptemp_df.values.tolist()
    for puncta in range(len(search_list)):
        coords=[int(search_list[puncta][x]),int(search_list[puncta][y])] 
        cell_number=cell_mask[coords[0],coords[1]]
        search_list[puncta].append(cell_number)
    
    column_name=ptemp_df.columns.tolist()
    column_name.append('Cell_label')
    GFP_puncta_info_df=pd.DataFrame(search_list,columns=column_name)
    
    #removing all puncta with no assigned cell label and droping na values. 
    GFP_puncta_info_df=GFP_puncta_info_df[GFP_puncta_info_df.Cell_label!=0].sort_values(by=['Cell_label'])
    GFP_puncta_info_df=GFP_puncta_info_df.dropna(axis=1,how='all')
    GFP_puncta_info_df=GFP_puncta_info_df.dropna()
    return GFP_puncta_info_df
        