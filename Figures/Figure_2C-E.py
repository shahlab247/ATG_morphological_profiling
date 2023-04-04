# -*- coding: utf-8 -*-
"""
Code for generating figure 2C-D and Figure S2 and Fig 2E
"""

#importing packages
import os
path= r"enter the working directory\Figures"
os.chdir(path)

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800
from MWU_BH import mannu_p
from RGB_to_hex import RGB
from split_functions import split_time
import umap
import seaborn as sns
#%%
#importing processed data file (Table-2)
data_wort= pd.read_csv(r"enter the location of preprocessed feature /Table-S2.csv")
data_wort=data_wort.drop(columns=['Unnamed: 0'])

#renaming the conditions with proper names

data_wort=data_wort.set_index(['Cell_label','Treatment'])
data_wort=data_wort.dropna(axis=1)

#%%
#concating the dataframe into cell(rows) X features*time (columns)

time_points= data_wort['time_point'].unique()
feature_name= data_wort.columns
time_to_account=time_points[4:] #accounting timepoints at and after 30 mins of treatment

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

#%%
#identifying all the features that vary significantly at all time points


time_df_ready=time_df.reset_index(level='Treatment').dropna(axis=1)


condition_test=time_df_ready['Treatment'].unique()[:-1] #removing basal(-1)

all_cond=[]

for condition in condition_test:
    p_val_data=mannu_p(df=time_df_ready,treatment='Treatment',cond1='basal',
                                           cond2=condition)
    cond_med=time_df_ready[time_df_ready['Treatment']==condition].median()

    if all(p_val_data['Feature']==(cond_med.index)):
        p_val_data['median_value']= list(cond_med)
        p_val_data['Condition']=[condition]*len(cond_med)
        all_cond.append(p_val_data)
    else:
        print(condition +' index doesnt match')

data_p=pd.concat(all_cond).reset_index(drop=True)

#export the p-values for future processing (optional)
#data_p.to_csv(r"enter the location to save/data_with_p_values_wort.csv")

#%%
#selecting significantly variable features
feat_bio_thres= data_p[(data_p['adj-p-value']<0.05) & (abs(data_p['median_value'])>=0.50)]

#%%
#For figure figure 2C-D
n_condition= ['10-W','Rapa'] #enter the conditions to visualize 
colors=[RGB([179,0,134]) ,RGB([255,192,0])]

#For supplemental figure S2
# n_condition= ['1-W','1-WR','10-WR']
# colors= [RGB([125,125,125])]*len(n_condition) #change color if necessary

fig,ax=plt.subplots(1,len(n_condition),figsize=(5*len(n_condition),4))


#plotting 
for idx,cond in enumerate(n_condition):
    df=feat_bio_thres[(feat_bio_thres['Condition']==cond)]
    test_bio_kind=split_time(df,time_split=time_to_account,Feature_col='Feature')

    pos1=ax[idx]
    test_bio_kind.plot.area(ax=pos1,x='Time',color=colors[idx],legend=False)
    pos1.set_title(cond)
    pos1.set_ylabel('Total number of significantly variable features')
    x_axis = pos1.axes.get_xaxis()
    x_axis.set_label_text('Time (hours)')
    pos1.set_xticks([0.5, 3,6,9, 12,15], minor=False)

#%%
#Figure 2E
#enter the timepoints at which cellular landscape needs to be analyzed
time_to_plot=[0.0,0.5,3.0,6.0,12.0,15.0]

#selecting the significantly variable features at the specific timepoint and separating them into lists.  
save_keep=[]
for idx,time in enumerate(time_to_plot):
    select_condition=feat_bio_thres[feat_bio_thres['Condition'].isin([ '10-W','Rapa'])]
    sig_feature_time=set([s for s in select_condition['Feature'] if s.startswith(str(time))])    
    save_keep.append(sig_feature_time)

#umap at each time point
g=[]
colors=[RGB([179,0,134]) ,RGB([255,192,0]),RGB([125,125,125])]
neighbors= 250
mindist=0.90
for idx,time in enumerate(time_to_plot):
    
    if idx==0: #first data corresponds to 0 timepoint. At this timpoint there are no significantly variable features therefore the 0.5 hour features are used. 
        data=data_wort.reset_index(level='Treatment')
        data= data[(data['Treatment'].isin([ '10-W','Rapa','basal'])) & (data['time_point']==0.0)]
        save_keep[idx]=[n[4:] for n in list(save_keep[1])]
        df_UMAP_final=data[save_keep[idx]]
    else:
        data= time_df_ready[time_df_ready['Treatment'].isin([ '10-W','Rapa','basal'])]
        df_UMAP_final=data[save_keep[idx]]
    data=data.reset_index()    
    reducer = umap.UMAP(n_neighbors=neighbors,min_dist=mindist)
    embedding = reducer.fit_transform(df_UMAP_final)
    sns.set_palette(sns.color_palette(colors))
    figure=sns.jointplot(x=embedding[:, 0], y=embedding[:, 1], data=data.reset_index(), hue='Treatment',space=0)
    plt.title("Time: " + str(time)+" hours" +str(neighbors)+"/"+str(mindist))
    g.append(figure)
    del(data)