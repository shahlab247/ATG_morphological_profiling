from IPython import get_ipython
def __reset__(): get_ipython().magic('reset -sf')
__reset__()
import os
cd=r"\Feature_Extraction/" #enter the location of working directory containing all the functions
os.chdir(cd)

import numpy as np
import matplotlib as mpl
#%matplotlib inline
mpl.rcParams['figure.dpi'] = 300
import pandas as pd
from channel_extract import channel_extract
from selecting_wells import selected_wells
from full_btrack import full_btrack
from full_props_edit import full_props

#%%
#04152022 data
all_cell_info=[] # to save all information possible about every cell
all_well_info=[] #to save info about just the cells with full tracks.  

well_name=  ['B02'] #enter the list of well name to analyze
pos_in_well=['1'] #enter the list of positions inside each well to analyze
outliers=[] #enter the outlier For ex:B02-3
for well in well_name:
    for pos in pos_in_well:
        required_wells=well+'-'+pos
        if required_wells in outliers:
            pass
        else:
            #enter the keywords that help identify the order of the experiment
            order_raw=["*pretreatment_*","*minus20_*","*posttreatment_*"] #enter the 
            order_puncta=order_raw
            order_cell=order_raw
            #provide the folder paths to raw data, cell mask data and puncta mask data
            
            #raw files
            #keywords for selecting individual channels. 
            search_raw_GFP="*GFP_RG_"+str(required_wells)+"*.tif"
            search_raw_TRITC="*TRITC1_RG_"+str(required_wells)+"*.tif"
            GFP_files, TRITC_files = channel_extract(r"G:\.shortcut-targets-by-id\1m1bQR-tnQCfKRd3zgPEENJc3VpOD4fdg\Shared-raw_dataand_experimental_setup\ULK Drugs Data\\10152022-ULK-101\Experimental(New)\tiffiles/", search_raw_GFP,search_raw_TRITC)
            
            #segmented cell masks
            cell_mask_path=r"G:\.shortcut-targets-by-id\1m1bQR-tnQCfKRd3zgPEENJc3VpOD4fdg\Shared-raw_dataand_experimental_setup\ULK Drugs Data\\10152022-ULK-101\Experimental(New)\savemasks/"
            seg_masks_fname=channel_extract(cell_mask_path,str('*'+required_wells+'*'))[0]
            
            #puncta masks
            GFP_mask_puncta="*_GROWING (GFP_SP)_"+str(required_wells)+"*.tif"
            AL_mask_puncta="*_GROWING (Autolysosome)_"+str(required_wells)+"*.tif"
            GFP_pmasks_fname,AL_pmasks_fname=channel_extract(r"G:\.shortcut-targets-by-id\1m1bQR-tnQCfKRd3zgPEENJc3VpOD4fdg\Shared-raw_dataand_experimental_setup\ULK Drugs Data\\10152022-ULK-101\Experimental(New)\tiffiles-binarymasks/", GFP_mask_puncta,AL_mask_puncta)
            
            #organize the images in the order of time.
            raw_select_GFP=selected_wells(order_raw, sorted(GFP_files),pre_min=3,max_post=31,postname=order_raw[-1])
            raw_select_TRITC=selected_wells(order_raw, sorted(TRITC_files),pre_min=3,max_post=31,postname=order_raw[-1])
            seg_select=selected_wells(order_cell, seg_masks_fname,pre_min=3,max_post=31,postname=order_cell[-1])
            puncta_select_GFP=selected_wells(order_puncta, sorted(GFP_pmasks_fname),pre_min=3,max_post=31,postname=order_puncta[-1])
            puncta_select_AL=selected_wells(order_puncta, sorted(AL_pmasks_fname),pre_min=3,max_post=31,postname=order_puncta[-1])
            #%% 
            #running bTrack and selecting the cells that have complete tracks and no loss of segmentation.
            config_path=r'G:\.shortcut-targets-by-id\1dnE4QtTSMUOYzZ30lhKgQ04v0npPlpRR\singlecell-analysis\Nitin\final_GIT\Feature_Extraction\bTrack_model/cell_config -test-3.json'  #enter the location where bTrack_model is saved.  
            #make sure the time label is same as the organized files from line 61-66
            time_label=list([-1.33,-1,-0.67,-0.33])+list(np.arange(0,15.5,0.5))
            cell_to_measure=full_btrack(seg_select,config_path, time_label=time_label)
                                    
            #%%
            #running all images in a well+pos. Ex- all timepoints for B02-2
            #reference for the fullprops entry
                #full_props(raw_img_GFP, raw_img_TRITC, seg_mask, GFP_puncta_mask,AL_puncta_mask,cell_to_measure)
            all_cells=[]
            all_times_select=[]
            for image in range(len(raw_select_GFP)):
                all_image_sum, cells_tracked=full_props(raw_select_GFP[image],raw_select_TRITC[image],seg_select[image],puncta_select_GFP[image],puncta_select_AL[image],cell_to_measure)
                all_times_select.append(cells_tracked)
                all_cells.append(all_image_sum)
            sum_all_times=pd.concat(all_times_select).sort_values(by=['track_ID','time_point'])
            all_cell_times=pd.concat(all_cells)
            print(str(required_wells)+' is completed')
            all_well_info.append(sum_all_times)
            all_cell_info.append(all_cell_times)

#%%exporting data
saving_location=r'#enter the location you want to save' #output_files
os.chdir(saving_location)

pd.concat(all_well_info).to_csv("cells_with_full_tracks.csv")
pd.concat(all_cell_info).to_csv("all_Cells_props.csv")
