# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 12:04:11 2023

@author: bniti
"""
import pandas as pd
import numpy as np

#splitting the kind/feature groups as a function of time

#function splits and count different conditions as a function of time. 
#input:df= input dataframe contaning the feature name starting with the timepoint and the col name(name_columns) used for spliting
#output: dataframe containing columns as the name_columns provided    
def split_kind(df,time_split,feat_name,col_name,name_columns,division_factor):
    split_condition=[]
    for time in time_split:
        first_cond= len([s for s in df[df[col_name]==name_columns[1]][feat_name] if s.startswith(str(time))])/division_factor[str(name_columns[1])]
        second_cond= len([k for k in df[df[col_name]==name_columns[2]][feat_name] if k.startswith(str(time))])/division_factor[str(name_columns[2])]
        third_cond= len([l for l in df[df[col_name]==name_columns[3]][feat_name] if l.startswith(str(time))])/division_factor[str(name_columns[3])]
        save=[time,first_cond,second_cond,third_cond]
        split_condition.append(save)
    
    split_condition=pd.DataFrame(np.vstack((split_condition)),columns=name_columns)    
    return split_condition

#reducing the redudancy in the features by eliminating features with more than 0.9 correlation. 

#function splits and count different conditions as a function of time. 
#input:df= input dataframe contaning the feature name starting with the timepoint and the col name(name_columns) used for spliting
#output: dataframe containing columns as the name_columns provided    
#all_time_df is the dataframe that contains the information of all timepoints of that specific condition
def split_uncorrelated_kind(all_time_df,df,time_split,feat_name,col_name,name_columns,division_factor):
    split_condition=[]
    for time in time_split:
        #selecting the specific time point
        df1=df[df['Feature'].str.startswith(str(time))]        
        #segregating by feature group
        uncorrealed_features=[]
        for kind in name_columns[1:]:
            feature_names= df1[df1[col_name]==kind]['Feature']
            df1_time= all_time_df[feature_names]
            cor_matrix = df1_time.corr().abs()
            upper_tri = cor_matrix.where(np.triu(np.ones(cor_matrix.shape),k=1).astype(np.bool))
            to_drop=[]
            for column in upper_tri.columns:
                if any(upper_tri[column] > 0.9):
                    to_drop.append(column)
            uncorrealed_features.append(set(df1_time.columns.tolist())-set(to_drop))
        first_cond=len(uncorrealed_features[0])/division_factor[str(name_columns[1])]
        second_cond=len(uncorrealed_features[1])/division_factor[str(name_columns[2])]
        third_cond=len(uncorrealed_features[2])/division_factor[str(name_columns[3])]
        save=[time,first_cond,second_cond,third_cond]
        split_condition.append(save)

    split_condition=pd.DataFrame(np.vstack((split_condition)),columns=name_columns)    
    return split_condition

#divinding based on time_only
def split_time(df,time_split,Feature_col):
    split_condition=[]
    for time in time_split:
        first_cond= len([s for s in df[Feature_col] if s.startswith(str(time))])
        save=[time,first_cond]
        split_condition.append(save)
    
    split_condition=pd.DataFrame(np.vstack((split_condition)),columns=['Time','Number of varibale features'])    
    return split_condition