# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 12:59:26 2023

@author: bniti
"""
import pandas as pd
import numpy as np

#function for removing correlated features
#input-dataframe and correlation_thresh
#the function would remove all feature that have a correlation above correlation_thresh except the first one
#returns a list of features that a NOT highly correlated(below the correlation_thres)

#testing the function
#removing uncorrelated features
def remove_correlated(df,correlation_thres=0.9):
    uncorrealed_features=[]
    cor_matrix = df.corr().abs()
    upper_tri = cor_matrix.where(np.triu(np.ones(cor_matrix.shape),k=1).astype(np.bool))
    to_drop=[]
    for column in upper_tri.columns:
        if any(upper_tri[column] > correlation_thres):
            to_drop.append(column)
    uncorrealed_features=list(set(df.columns.tolist())-set(to_drop))
    return uncorrealed_features