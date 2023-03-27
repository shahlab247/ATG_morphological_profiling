# -*- coding: utf-8 -*-
"""
Function takes a list of cell masks organized chronological to track individual cells over the entire timecourse 
using btrack algorithm
#inputs:
    seg_select= list of cell masks in a array format organized chronologically. 
    path- location to .JSON file which contains the parameters to use for btrak algorithm
    time_label= list of timepoints to assign the labels for the list of images. 
outputs:
    a dataframe containing the cells tracked at all timepoints and their respective label at each timepoint. 
"""
# temporary full btrack analysis change the code such that the config file can be easily accessed. 
import btrack
import numpy as np
import pandas as pd

#running bTrack and selecting the cells that have complete tracks and no loss of segmentation.  
def full_btrack(seg_select,path,time_label):
    #importing the seg_files as image
    seg_masks=np.zeros((len(seg_select),2048,2048))
    for idx, image in enumerate(seg_select):
        seg_masks[idx,:,:]= np.loadtxt(image)
        
    seg_masks=seg_masks.astype(int)  
    
    #running bTrack  
    # localising the objects. 
    obj_from_arr = btrack.utils.segmentation_to_objects(seg_masks,properties = ('area', 'major_axis_length','minor_axis_length','perimeter'),assign_class_ID=True)
    
    #running btrack with the objects. 
    # initialise a tracker session using a context manager
    #PATH= r'G:\My Drive\Research\singlecell-analysis\Nitin\celltrackers/output'
    
    with btrack.BayesianTracker() as tracker:
    
        # configure the tracker using a config file
        tracker.configure_from_file(path)
        tracker.max_search_radius = 100
    
        # append the objects to be tracked
        tracker.append(obj_from_arr)
    
        # set the volume
        tracker.volume=((0, 2048), (0, 2048), (-1e5, 1e5))
    
        # track them (in interactive mode)
        tracker.track_interactive(step_size=100)
    
        # generate hypotheses and run the global optimizer
        #tracker.optimize()
    
        #tracker.export(os.path.join(PATH, 'tracking200.h5'), obj_type='obj_type_1')
    
        # get the tracks in a format for napari visualization
        data, properties, graph = tracker.to_napari(ndim=2)
        
        tracks = tracker.tracks
    
    full_tracks=[]
    min_tracks= len(seg_masks)
    #extracting cells that have full tracks and havent lost any masking
    for cells in tracks:
        if len(cells)==min_tracks and np.isnan(cells.properties["class_id"]).any()==False:
            full_tracks.append(cells)
            
    #selecting the cells and puncta that only have full tracks. 
    save_labels=np.zeros(((len(seg_select)*len(full_tracks),3)))
    exp_labels=[]
    #print(len(full_tracks[0]))    
    min_tracks=len(full_tracks[0])
    for idx,cell in enumerate(full_tracks):
        save_labels[min_tracks*idx:min_tracks*(idx+1),0]=time_label
        save_labels[min_tracks*idx:min_tracks*(idx+1),1]=cell.ID
        save_labels[min_tracks*idx:min_tracks*(idx+1),2]=cell.properties["class_id"]   
        exp_labels[min_tracks*idx:min_tracks*(idx+1)]= seg_select
    
    #converting everything to pandas dataframe for ease of working. 
    cell_to_measure=pd.DataFrame(exp_labels, columns=['filename'])
    cell_to_measure['time_point']= save_labels[:,0].tolist()
    cell_to_measure['track_ID']= save_labels[:,1].tolist()
    cell_to_measure['mask_ID']= save_labels[:,2].tolist()
    cell_to_measure=cell_to_measure.sort_values(by=['time_point'])
    return cell_to_measure