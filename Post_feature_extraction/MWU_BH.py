# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 17:58:33 2022

@author: bniti
"""


#this function performs Mann- Whitney U(MWU) statistical test to compute p-values for two  conditions. 
#following MWU test,Benhamini/Hochberg method is used to account for multiple hypothesis testing. #0.05 is the threshold. 
#mann-whitney u test
#inputs:
    #df- dataframe containing column of features with treatment as one of the column containing cond1 and cond2
    #alpha_input= threshold of statistical significance 
#returns a df with feature, p-value and adj-p-value. 

import pandas as pd
import numpy as np
import scipy.stats as stat
from statsmodels.stats.multitest import multipletests

def mannu_p(df,treatment,cond1,cond2,alpha_input=0.05):
    

    df1= df[df[str(treatment)]==(cond1)]
    df2=df[df[str(treatment)]==(cond2)]

    info_list=[]
    df1=df1.drop(columns=[treatment])
    df2=df2.drop(columns=[treatment])
    df1.dropna(inplace=True)
    df2.dropna(inplace=True)
    
    if (df1.isnull().values.any()== True) or (df2.isnull().values.any()== True):
        print('still has na values')
    else:
        for feature in df1.columns:
            data1=np.asarray(df1[feature])
            data2=np.asarray(df2[feature])

            #calculating p-value
            fval,pval=stat.mannwhitneyu(data1,data2)
            temp_list=[feature,pval]
            info_list.append(temp_list)
        
    #calculating the adjusted p-values using Benjamini/Hochberg (non-negative) method
    df_out=pd.DataFrame(info_list, columns=['Feature','p-values'])
    df_out.replace([-np.inf], np.nan, inplace=True)
    df_out.replace([np.inf], np.nan, inplace=True)
    df_out.dropna(inplace=True)
    p_values=np.asarray(df_out['p-values'])
    if (df_out['p-values']).isnull().values.any()== True:
        print('NA values are present')
    adj_p= multipletests(p_values,alpha=alpha_input,method='fdr_bh')[1]
    df_out['adj-p-value']=adj_p
    return df_out    