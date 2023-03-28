# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 16:54:43 2022

@author: Nitin Beesabathuni
"""
# -*- coding: utf-8 -*-
"""
"""
import os
path= r"G:\My Drive\Research\singlecell-analysis\Nitin\final_GIT\Post_feature_extraction/"
os.chdir(path)

#Packages
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300
from robust_zscore import rzscore 

#importing all three replicates from Feature extraction\output files folder
df_042021= pd.read_csv(r'G:\My Drive\Research\singlecell-analysis\Nitin\final_GIT\Feature_Extraction\output_files\raw_features_042021.csv')
df_072021= pd.read_csv(r'G:\My Drive\Research\singlecell-analysis\Nitin\final_GIT\Feature_Extraction\output_files\raw_features_072021.csv')
df_082021= pd.read_csv(r'G:\My Drive\Research\singlecell-analysis\Nitin\final_GIT\Feature_Extraction\output_files\raw_features_082021.csv')
all_df_treat_final=[df_042021,df_072021,df_082021]


#%%
#assinging cells numbers based on each condition to avoid confusion
#combining all replciates and assinging cell labels
#spliting the combined into individual replciates for robust z score calculations
df_select=pd.concat(all_df_treat_final).reset_index(drop=True).drop(columns=['Unnamed: 0']) #important

timepoints= len(df_select['time_point'].unique())
labeled_list=np.zeros((len(df_select)))
for cond in df_select['Treatment'].unique():
    label_cells=[]
    n_cells= int(len(df_select[df_select['Treatment']==cond]['track_ID'])/timepoints) #estimate number of cells. 
    index_val=df_select[df_select['Treatment']==cond]['track_ID'].index
    for x in range(1,n_cells+1,1):
        min_range= index_val[(x-1)*(timepoints)]
        max_range=min_range+(timepoints)
        labeled_list[min_range:max_range]=[x]*timepoints
            
df_select.insert(loc=1,column='Cell_label',value= labeled_list)

df_select=df_select.sort_values(by=['Treatment','Cell_label','time_point']).reset_index(drop=True)

#spliting into replicates
ready_zscore=[]
replicate_keys=['04152021','07302021','08262021']
for keyword in replicate_keys:
    ready_zscore.append(df_select[df_select['filename'].str.contains(keyword)])

#making sure individudal replicates are separated well
for idx,rep in enumerate(ready_zscore):
    if len(rep)== len(all_df_treat_final[idx]):
        print('replicates divided and assigned - proceed to zscore')
    else:
        print('replicates have duplicate keywords or not divided properly')
#%%standardisation of the data using modified z score method. 
#each timepoint for each replicate is normalized seperately and finally aggregated. 
#exporting the csv file
all_norm_rz=[]
for df in ready_zscore:
    time=df['time_point'].unique()
    zscore=[]
    for t in time:
        df_time=df[df['time_point']==t]
        df_drop=df_time.drop(columns=['filename','condition','time_point','track_ID','Cell_label'])
        df_rz=rzscore(df_drop)
        df_rz.insert(0,'filename',df_time['filename'])
        df_rz.insert(1,'time_point',df_time['time_point'])
        df_rz.insert(2,'Treatment',df_time['Treatment'])
        df_rz.insert(3,'track_ID',df_time['track_ID'])
        df_rz.insert(4,'Cell_label',df_time['Cell_label'])
        zscore.append(df_rz)
    
    all_norm_rz.append(pd.concat(zscore).sort_values(by=['Treatment','track_ID','time_point']))


export_wort_zscore=pd.concat(all_norm_rz).sort_values(by=['Treatment','Cell_label','time_point']).reset_index(drop=True)
export_wort_zscore.to_csv("Processed_features.csv")      
