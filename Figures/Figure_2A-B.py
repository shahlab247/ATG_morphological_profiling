'''
#code for regenerating Figure 2A-B( 0.5 hours) and supplemental figures S1B-D (0 and 6 hours)
'''

#enter the working directory
import os
path= r"enter the working directory location"
os.chdir(path)

#importing packages
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800
from RGB_to_hex import RGB

#%%
#importing processed data file (Table-2)
data_wort= pd.read_csv(r"enter the location for preprocessed data/Table-S2.csv")
data_wort=data_wort.drop(columns=['Unnamed: 0'])

#renaming the conditions with proper names
data_wort=data_wort.set_index(['Cell_label'])
data_wort=data_wort.dropna(axis=1)

#%%
#timepoints for volcano plots
time_plot= [0.0,0.5, 6.0]
sorted_df_rz=[]
for time in time_plot:
    sorted_df_rz.append(data_wort[data_wort['time_point']==time].set_index('time_point'))

#%%
#assinging phenotypes for each feature. 
from MWU_BH import mannu_p
#list of feature that our significant
data_volcano=[]

condition_test=['10-W','Rapa']
for before_pert in sorted_df_rz:
    all_cond=[]
    for cond in condition_test:
        p_val_data=mannu_p(df=before_pert,treatment='Treatment',cond1='basal',
                                               cond2=cond)
        cond_med=before_pert[before_pert['Treatment']==cond].median()   
       
        if all(p_val_data['Feature']==(cond_med.index)):
            p_val_data['median_value']= list(cond_med)
            p_val_data['Condition']=[cond]*len(cond_med)
            all_cond.append(p_val_data)
        else:
            print(cond +' index doesnt match')
    data_volcano.append(pd.concat(all_cond))

#%%
##adding a hue to check if the feature is downregulated or upregulated
thres= 0.5 #threshold for determining significant features
for p_val in data_volcano:
    
    conditions=[((p_val['adj-p-value']<0.05) & (p_val['median_value']<=-thres)),
                ((p_val['adj-p-value']<0.05) & (p_val['median_value']>=thres)),
                ((p_val['adj-p-value']<0.05) & (abs(p_val['median_value'])<thres)),
                (p_val['adj-p-value']>=0.05)]
    values=['Decrease','Increase','Insignificant','Insignificant']
    p_val['Phenotype']=np.select(conditions, values, default='False')
    p_val['-log_p_val']=-np.log10(p_val['adj-p-value'])
#%%
#volcano plots for each timepoint
#setting max value for logp
logp_max= 10
to_annote=['mean_intensity'] #enter the features that needs to be annoted on the volcano plot. 
colors=[RGB([0,0,255]) ,RGB([125,125,125]),RGB([255,0,0])]
y_dotted_lines= [0,2,4,6,8,10]

sns.set_palette(sns.color_palette(colors))
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

for time, df in enumerate(data_volcano):
      
      df['-log_p_val'].mask(df['-log_p_val']>logp_max,logp_max, inplace=True)
      cond=df['Condition'].unique()
      fig,axs=plt.subplots(1,len(cond),figsize=(10,4))
      for idx,con in enumerate(cond):
          df_con=df[df['Condition']==con]
          hue_order = ['Decrease', 'Insignificant', 'Increase']
          pos1=axs[idx]
          sns.scatterplot(ax=pos1,x=df_con['median_value'], y=df_con['-log_p_val'], data=df_con,hue_order=hue_order, hue='Phenotype',s=20)
          pos1.set( xlabel = "Median of modified Z-score", ylabel = "-log10FDR".translate(SUB))
          
          
          pos1.plot([0]*6,y_dotted_lines,color='k',ls='--')
          pos1.plot([0.5]*6,y_dotted_lines,color='k',ls='--')
          pos1.plot([-0.5]*6,y_dotted_lines,color='k',ls='--')
          min_neg_x=df_con['median_value'].min()
          max_pos_x=df_con['median_value'].max()
          rng= (max_pos_x-min_neg_x)/6
          pos1.plot([min_neg_x, max_pos_x],[1.30]*2,color='k',ls='--')
          
          if len(to_annote)>0: 
              for i in range(len(df_con)):
                   if df_con['Feature'].iloc[i] in to_annote: 
                       gitter=0.1
                       pos1.scatter(x=df_con['median_value'].iloc[i],y=df_con['-log_p_val'].iloc[i], s=20, facecolors='none', edgecolors='k')
                       pos1.text(x=df_con['median_value'].iloc[i],y=df_con['-log_p_val'].iloc[i],s=df_con['Feature'].iloc[i])
              pos1.set_title(str(con) +" at "+ str(time_plot[time])+ ' hours')
              
      #plt.savefig(r'enter the location to save.pdf') 
      plt.show()













