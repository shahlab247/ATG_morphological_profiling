"""
Code for generating Figure S4A-D. 
"""
#importing packages
import os
path= r"enter the working directory\Figures"
os.chdir(path)

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800
import seaborn as sns
from sklearn.decomposition import PCA
import numpy as np

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

#selecting all significant features
filtered_feat_all= data_p[(data_p['adj-p-value']<0.05) & (abs(data_p['median_value'])>=0.5)]

selected_df=time_df[filtered_feat_all['Feature']]
#%%
#Generating figure S4A & S4C
#using all significantly variable features for identifying correlation and clustering

#performing PCA for removing redunancy and 
pca=PCA(0.90)
comp_PCA = pca.fit_transform(selected_df)
#plt.plot(np.cumsum(pca.explained_variance_ratio_)) (optional - plot variance explained vs PC components)

#hierarchical clustering
cluster_df=pd.DataFrame(data=comp_PCA).reset_index(drop=True)
cluster_df['Treatment']=list(time_df_ready['Treatment'])
median_profiles=cluster_df.groupby('Treatment').median()
sns.clustermap(median_profiles, vmin=-2, vmax=2, col_cluster=False, row_cluster=True,cmap="crest", figsize=(6,6))
plt.title("All Morphological features that varied significantly",loc='left')
plt.show()

#correlation between treatments
matrix = cluster_df.groupby('Treatment').median().T.corr(method='pearson').round(2)
f=sns.heatmap(matrix, annot=True,cmap="crest",mask=np.isnan(matrix))
plt.title("Correlation between treatments using morphological features")
plt.show()
#%%
#Generating figure S4B & S4D
#using just autophagosome and autolysome numbers for identifying correlation and clustering
ap_col=[col for col in time_df.columns if '_number' in col] #autophagosome and autolysosome have  "_number" str

#PCA
pca=PCA(0.90)
comp_PCA_ap = pca.fit_transform(time_df_ready[ap_col])
cluster_df_ap=pd.DataFrame(data=comp_PCA_ap).reset_index(drop=True)
cluster_df_ap['Treatment']=list(time_df_ready['Treatment'])
median_profiles_ap=cluster_df_ap.groupby('Treatment').median()
sns.clustermap(median_profiles_ap, vmin=-2, vmax=2, col_cluster=False, row_cluster=True,cmap="flare", figsize=(6,6))
plt.title("Autophagosome and autolysosome dynamics", loc='left')
plt.show()

#hierarchical clustering
matrix_ap = cluster_df_ap.groupby('Treatment').median().T.corr(method='pearson').round(2)
sns.heatmap(matrix_ap, annot=True,cmap="flare")
plt.title("Correlation between treatments using AP and AL dynamics")
plt.show()








