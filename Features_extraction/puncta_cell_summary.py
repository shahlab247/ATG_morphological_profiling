# -*- coding: utf-8 -*-
"""
#this function takes puncta information including the corresponding cell numbers and returns dataframe
#inputs:
    #puncta_info_df=dataframe of puncta information with cell labels
    #cell_props= dataframe containing cellular features with labels.
    #label_name= is the prefix that will be added to each features of the respetive puncta/object. 
#returns:
    #dataframe containing summary puncta features at a single cell level with cell label
"""
import pandas as pd

def puncta_cell_summary(puncta_info_df,cell_props_df,label_name):
    puncta_summary_all=[]
    image_summary=[]
    after_drop= puncta_info_df.drop(columns=[str('condition_'+str(label_name)),'label','bbox-0','bbox-1','bbox-2','bbox-3',
                                         'centroid-0','centroid-1'])
    
    if after_drop.isnull().values.any()== False: #making sure the dataframe has no nan values
        cell_data= cell_props_df.values.tolist()
        for cell in range(len(cell_data)): #for each cell
            puncta_summary=[]
            cell_number=float(cell_data[cell][1]) #index 1 has the cell label
            puncta_summary.append(cell_data[cell][0])
            puncta_summary.append(cell_number)
            df_subset=after_drop[after_drop.Cell_label==cell_number]
            if df_subset.empty!=True:
               summary_info= df_subset.describe()
               index_label=summary_info.index
               for stat in index_label:
                   if stat == 'count':
                       puncta_summary.append(summary_info.loc[stat][0])
                   elif stat=='std':
                       pass
                   else:
                       puncta_summary=puncta_summary+(summary_info.loc[stat].values.tolist()[:-1])
            image_summary.append(puncta_summary)
            puncta_summary_all=pd.DataFrame(image_summary)
        #extracting labels all the columns 
        label_summary=['Condition-Check','Cell_label-check',str(label_name)]
        #label for individual cell properties
        for stat in index_label:
            if stat == 'count' or stat=='std':
                pass
            else:
                for name in after_drop.columns[:-1]:
                    label_summary.append(stat+'_'+str(label_name)+'_'+name)

        #labeling all the columns
        puncta_summary_all.columns=label_summary
        #nan's generated due to no puncta inside a cell are given a value of zero
        if puncta_summary_all.isnull().values.any()== True:
            puncta_summary_all=puncta_summary_all.fillna(0)
    else:
        print('The provided puncta feature dataframe still has null values')
    return puncta_summary_all
