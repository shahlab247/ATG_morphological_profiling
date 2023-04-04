# -*- coding: utf-8 -*-
"""
Code for generating figure 3E-F
"""

#importing packages
import os
path= r"enter the working directory\Figures"
os.chdir(path)

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800
from RGB_to_hex import RGB
import umap
import seaborn as sns
#%%
#importing processed data file (Table-2)
data_wort= pd.read_csv(r"enter the location of processed feature /Table-S2.csv")
data_wort=data_wort.drop(columns=['Unnamed: 0'])

#renaming the conditions with proper names

data_wort=data_wort.set_index(['Cell_label','Treatment'])
data_wort=data_wort.dropna(axis=1)

#%%
#concating the dataframe into cell(rows) X features*time (columns)

time_points= data_wort['time_point'].unique()
feature_name= data_wort.columns
time_to_account=time_points[4:] #accounting timepoints at and after 0 mins of treatment

for time in time_to_account:
    df=data_wort[data_wort['time_point']==time]
   
    if time == time_to_account[0]:
        time_df=df.drop(columns=['time_point'])
    else:
        if all(df.index==time_df.index)==True:
            time_df=pd.concat((time_df,df[feature_name[1:]]),axis=1)
        else:
            print('cell or conditions dont match')
            
#column_name
column_names=[]
for time in time_points:
    if time in time_to_account:
        for feat in feature_name[1:]:
            column_names.append(str(str(time)+'_'+feat))
        
time_df.columns=column_names
time_df=time_df.dropna(axis=1)
time_df_ready=time_df.reset_index(level='Treatment')
#%%
#importing all the features that vary significantly at all time points
#refer to figure 2C-E code 
data_p= pd.read_csv(r"enter the location of p-valuesFigures\data_with_p_values_wort.csv")

#%%
#selecting significantly variable features
feat_bio_thres= data_p[(data_p['adj-p-value']<0.05) & (abs(data_p['median_value'])>=0.50)]


#UMAP accounting for all timepoints 
colors=[RGB([179,0,134]) ,RGB([255,192,0]),RGB([125,125,125])]
neighbors= 250
mindist=0.90
data_UMAP=time_df_ready[time_df_ready['Treatment'].isin(['10-W','Rapa','basal'])]
df_UMAP_final=data_UMAP[set(feat_bio_thres['Feature'])]
#UMAP
reducer = umap.UMAP(n_neighbors=neighbors,min_dist=0.9)
embedding = reducer.fit_transform(df_UMAP_final)
#plot UMAP
sns.set_palette(sns.color_palette(colors))
data_UMAP['embedding_0']= embedding[:, 0]
data_UMAP['embedding_1']= embedding[:, 1]
data_UMAP= data_UMAP.reset_index()

sns.set_palette(sns.color_palette(colors))
figure=sns.jointplot(x=embedding[:, 0], y=embedding[:, 1], data=data_UMAP.reset_index(), hue='Treatment',space=0)
plt.title("All_time_points")
plt.show()

#%%
#visualizing individual features
feat_plots=['mean_intensity','Autophagosome_number','min_AP_contrast_mean','max_AP_area'] 
time_plot=[0.0,0.5,3.0,6.0,12.0,15.0]

fig, axs= plt.subplots(len(feat_plots),len(time_plot), figsize=(6*len(time_plot),5*len(feat_plots)))
for idx,feat in enumerate(feat_plots):
    for t,time in enumerate(time_plot):
        pos=axs[idx,t]
        name=str(str(time)+'_'+feat)
        color_index=data_UMAP[name].to_numpy()
        for n,con in enumerate(data_UMAP['Treatment'].unique()):
            if con=='basal':
                zorder= -1
            else:
                zorder=2
            df_plot=data_UMAP[data_UMAP['Treatment']==con]
            color_index=df_plot[name].to_numpy()
            sc=pos.scatter(x=df_plot['embedding_0'],y=df_plot['embedding_1'],zorder=zorder,label=con,
                           c=color_index,cmap='bwr',vmin=-2, vmax=2,edgecolors='k',linewidths=0.15)
            pos.get_yaxis().set_visible(False)
            pos.get_xaxis().set_visible(False)
plt.show()