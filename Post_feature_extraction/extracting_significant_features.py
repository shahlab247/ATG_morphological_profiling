#Packages
import os
path= "directory location"
os.chdir(path)
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800
from MWU_BH import mannu_p


#importing processed z scored file Post_feature_extraction\output information
data_wort= pd.read_csv(r"input the folder location\Processed_features")
data_wort=data_wort.drop(columns=['Unnamed: 0','filename','track_ID'])

#renaming the conditions with proper names

data_wort=data_wort.set_index(['Cell_label','Treatment'])
data_wort=data_wort.dropna(axis=1)
#%%
#feature space
#concating the dataframe into cell X features*time =  cells X (features*time)

time_points= data_wort['time_point'].unique()
feature_name= data_wort.columns
time_to_account=time_points[5:] #accounting timepoints at and after 30 mins of treatment

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
#extracting features that are significant


time_df_ready=time_df.reset_index(level='Treatment').dropna(axis=1)


condition_test=time_df_ready['Treatment'].unique()[:-1]

all_cond=[]

for condition in condition_test:
    p_val_data=mannu_p(df=time_df_ready,treatment='Treatment',cond1='basal',
                                           cond2=condition)
    cond_med=time_df_ready[time_df_ready['Treatment']==condition].median()
    basal_med=time_df_ready[time_df_ready['Treatment']=='basal'].median()
    if cond_med.index.equals(basal_med.index):    
        median_diff=cond_med- basal_med
    else:
        print("Index for basal and " + str(condition)+" doesnt match")
    if all(p_val_data['Feature']==(median_diff.index)):
        p_val_data['median_value']= list(median_diff)
        p_val_data['Condition']=[condition]*len(median_diff)
        all_cond.append(p_val_data)
    else:
        print(condition +' index doesnt match')

data_p=pd.concat(all_cond)

# location where the features with p-values need to be saved. 
data_p.to_csv(r"export_folder_location\data_with_p_values_wort.csv")












