# -*- coding: utf-8 -*-
"""

#the function takes dataframe, search col, the txt to search, the name to assign(treatment_name) and will assign a column with col_name 
at location loc. 
"""
import numpy as np

#adding label function
    
def addlabel_new(all_Cell_features,search_col,search_text,alt_text,treatment_name,col_name,loc=1,cond=1):
    #making sure the len(well_name)==len(treatment_name)
    if len(search_text)==len(treatment_name):
        conditions=[]
        choices=treatment_name
        if cond==1:
            for name in search_text:
                conditions.append(all_Cell_features[str(search_col)].str.contains(name)==True)
        else:
            for idx,name in enumerate(search_text):
                conditions.append((all_Cell_features[str(search_col)].str.contains(name)==True) | (all_Cell_features[str(search_col)].str.contains(alt_text[idx])==True))
        all_Cell_features.insert(loc,col_name,'')
        all_Cell_features[col_name]=np.select(conditions, choices, default='False')
    return all_Cell_features