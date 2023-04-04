# -*- coding: utf-8 -*-
"""
Code for generating Figure 3A-D
"""

#importing packages
import os
path= r"enter the working directory\Figures"
os.chdir(path)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800
from RGB_to_hex import RGB
import seaborn as sns
from remove_correlated import remove_correlated
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import cross_val_score
#%%
#importing processed data file (Table-S2) 
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
data_p= pd.read_csv(r"enter the location of p-values\Figures\data_with_p_values_wort.csv")


#selecting significantly variable features
thres=0.5
feat_bio_thres=sorted(list(set(data_p[(abs(data_p['median_value'])>=thres) & (data_p['adj-p-value']<0.05) & (data_p['Condition'].isin([ '10-W','Rapa']))]['Feature'])))

#removing uncorrelated features
to_remove_uncorrelated= time_df_ready[time_df_ready['Treatment'].isin([ '10-W','Rapa','basal'])].set_index('Treatment')
uncorrelated_features=sorted(remove_correlated(to_remove_uncorrelated[feat_bio_thres],correlation_thres=0.75))

#dataframe with only uncorrelated features
classify_data=to_remove_uncorrelated[uncorrelated_features].reset_index(level='Treatment')

#%%

X,y= classify_data.iloc[:, 1:], classify_data.iloc[:, 0]

forest = RandomForestClassifier(n_estimators = 1000,criterion='entropy',random_state = 42)
rfc_cv_score=cross_val_score(forest, X, y, scoring='f1_micro',n_jobs=-1)

print("Accuracy of the classifier: " +str(rfc_cv_score.mean()) +' +/-'+ str(rfc_cv_score.std()))

#%%
#Generating a representative confusion matrix
#Figure 3A
#splitting data
X_train, X_test, y_train, y_test = train_test_split(classify_data.iloc[:, 1:], classify_data.iloc[:, 0], test_size = 0.2, random_state=42)

forest = RandomForestClassifier(n_estimators = 1000,criterion='entropy',random_state = 42)
forest.fit(X_train, y_train.values.ravel())
y_pred=forest.predict(X_test)
f1=(f1_score(y_test,y_pred,average='micro'))
print(" Accuracy: " + str(f1_score(y_test,y_pred,average='micro')))

#plotting confusion matrix

matrix = confusion_matrix(y_test, y_pred)
matrix = matrix.astype('float') / matrix.sum(axis=1)[:, np.newaxis]

# Build the plot
plt.figure(figsize=(8,5))
sns.set(font_scale=1.4)
sns.heatmap(matrix, annot=True, annot_kws={'size':20}, cmap=plt.cm.Blues, linewidths=0.2)

# Add labels to the plot
class_names = ['Wortmannin','Rapamycin','Basal']
tick_marks = np.arange(len(class_names))+ 0.5
plt.xticks(tick_marks, class_names, rotation=0)
plt.yticks(tick_marks, class_names, rotation=0)
plt.xlabel('Predicted Treatment')
plt.ylabel('True Treatment')
plt.title('Representative confusion matrix')
plt.show()

#%%
import shap
# Explain the model's predictions using SHAP values
explainer = shap.TreeExplainer(forest)
shap_values = explainer.shap_values(X_test)

# Plot the feature importance values
colors=[RGB([179,0,134]) ,RGB([255,192,0]),RGB([125,125,125])]

#%%
"""
#calculating the mean |SHAP values| for each treatment based on all cells. 
#note- this same graph can be generated using 
    shap.summary_plot(shap_values, X_test,plot_type="bar",class_names=forest.classes_
                  ,max_display=10) 
    Refer to SHAP documentation (https://shap.readthedocs.io/en/latest/index.html)"""
df_shap_val=[]
for idx,arr in enumerate(shap_values):
    abs_val=np.abs(arr)
    df_shap_val.append(pd.DataFrame(abs_val, columns=X_test.columns).mean())
    
df_shap_val=pd.concat(df_shap_val,axis=1)
df_shap_val.columns=forest.classes_
df_shap_val['Total_sum']= df_shap_val.iloc[:,0:3].sum(axis=1)
df_shap_val['Contribution']= df_shap_val['Total_sum']/(df_shap_val['Total_sum'].sum())*100
df_shap_val= df_shap_val.sort_values(by='Total_sum',ascending=False)


#%%
#categorizing features based on biological category (Cell, AP, and AL) and morphological property (structure, intensity, and texture)

filtered_feat_all=df_shap_val.rename_axis('Feature').reset_index()

from addlabel_new import addlabel_new
#assinging the kind of biological category based on feature name
#funtion-  addlabel_new(all_Cell_features,search_col,search_text,alt_text,treatment_name,col_name,loc=1,cond=1):
bio_kind=['AP','AL']
alt_kind=['Autophagosome','Autolysosome']
feat_bio= addlabel_new(filtered_feat_all,'Feature',bio_kind,alt_kind,bio_kind,col_name='Bio_kind',cond=2)
#replacing the false with cell
feat_bio['Bio_kind'].mask(feat_bio['Bio_kind'] == 'False', 'Cell', inplace=True)

#assinging the kind of morphological property based on feature name
intensity=['intensity','standard_deviation','median']
texture=["angularsecondmoment_mean", "contrast_mean", "correlation_mean", "variance_mean","inversedifferentmoment_mean",
           "sumaverage_mean", "sumvariance_mean", "sumentropy_mean", "entropy_mean", "differencevariance_mean",
           "differenceentropy_mean", "correlation1_mean", "correlation2_mean", "maxcorrelationcoeff_mean",
           "angularsecondmoment_range", "contrast_range","correlation_range","variance_range", "inversedifferentmoment_range",
                      "sumaverage_mean", "sumvariance_mean", "sumentropy_mean", "entropy_mean", "differencevariance_mean",
                      "differenceentropy_range", "correlation1_range", "correlation2_range", "maxcorrelationcoeff_range"]
structure=['moment','area', 'bbox_area', 'convex_area', 'filled_area', 'major_axis_length', 'minor_axis_length',
              'eccentricity','euler_number', 'extent', 'feret_diameter_max','inertia_tensor', 'inertia_tensor_eigvals', 
              'orientation', 'perimeter', 'perimeter_crofton','solidity']
bio=['Autophagosome_number','Autolysosome_number']

feat_assign_all_time=[]
for feature in feat_bio['Feature']:
    if any(iname in feature for iname in intensity):
        feat_assign_all_time.append('Intensity')
    elif any(name in feature for name in texture):
        feat_assign_all_time.append('Texture')
    elif any(Sname in feature for Sname in structure):
        feat_assign_all_time.append('Structure')
    elif any(Bname in feature for Bname in bio):
        feat_assign_all_time.append('Bio')
    else:
        feat_assign_all_time.append('None')
if 'None' in feat_assign_all_time:
    print("Still has None values")
else:
    feat_bio['Feature_Kind']=feat_assign_all_time   

#%%
#splitting each treatment based on the condition, category, property and counting the number of features in each. 
#[Cell, AP, AL] and #[Intensity, Texture, Structure, Bio]

conditions= conditions=['10-W','Rapa']
bio_labs=feat_bio['Bio_kind'].unique()
feat_labs=feat_bio['Feature_Kind'].unique()
cond_save=[]
for cond in conditions:
    save=[]
    for bio in bio_labs:
        for feat in feat_labs:
            if feat=='Bio':
                average=feat_bio[ (feat_bio['Feature_Kind']==feat)][cond].mean()
                cumsum=feat_bio[(feat_bio['Feature_Kind']==feat)][cond].sum()
                number_feat=len(feat_bio[(feat_bio['Feature_Kind']=='Bio')][cond])
                name='Vesicle_numbers'
            else:
                average=feat_bio[(feat_bio['Bio_kind']==bio) & (feat_bio['Feature_Kind']==feat)][cond].mean()
                cumsum=feat_bio[(feat_bio['Bio_kind']==bio) & (feat_bio['Feature_Kind']==feat)][cond].sum()
                number_feat=len(feat_bio[(feat_bio['Bio_kind']==bio) & (feat_bio['Feature_Kind']==feat)][cond])
                name=bio+('/')+feat
            save.append([name, average,cumsum,number_feat])
    save_df=pd.DataFrame(save,columns=['Name','Average_Importance','Cumsum','Length']).drop_duplicates().fillna(0)
    save_df=save_df.sort_values(by='Cumsum')
    cond_save.append(save_df)

#%%
#plotting importance calculated using mean|SHAP values|
#Figure 3B-C
for idx,data in enumerate(cond_save): 
    fig, axs = plt.subplots(figsize=(8,5),  ncols=2, sharey=True)    
    axs[0].barh(data['Name'],data['Average_Importance'],align='center',color=colors[idx])
    axs[0].set_xlabel("Average Importance")
    bars=axs[1].barh(data['Name'],data['Cumsum'],align='center',color=colors[idx])
    axs[1].set_xlabel("Cumulative Importance")
    axs[1].set_xlim([0,0.35])
    # If you have positive numbers and want to invert the x-axis of the left plot
    axs[0].invert_xaxis() 
    axs[0].set(yticks=data['Name'], yticklabels=data['Name'])
    axs[0].yaxis.tick_left()
    axs[1].tick_params(axis='y', colors=colors[idx]) # tick color
    plt.subplots_adjust(wspace=0.0, top=0.85, bottom=0.1, left=0.18, right=0.95)
    plt.title(conditions[idx])
    plt.show()
#%%
#Figure 3D
# Plot the feature importance values for the first 15 features
fig, axs = plt.subplots(figsize=(8,6))  
colors=[RGB([179,0,134]) ,RGB([255,192,0]),RGB([125,125,125])]
df_shap_val.iloc[0:15,0:3].plot.barh(ax=axs,stacked=True,color=colors)
plt.gca().invert_yaxis()
plt.show()
