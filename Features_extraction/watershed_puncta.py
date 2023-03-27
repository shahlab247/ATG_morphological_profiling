# -*- coding: utf-8 -*-
"""
#this function segments objects using watershed approach
#inputs:
    #puncta_mask- 3D image contaning objects that need to be segmented. 
    #zplane- the plane in which the objects need to be watershed. Autophagosome are in 0 while autolysosome are in 2. 
#labeling blobs by watershed function.
"""
from skimage.measure import label
from skimage import segmentation, morphology
from scipy import ndimage as ndi
import matplotlib.pyplot as plt


def watershed_fun(puncta_mask,zplane): #input the filename of the puncta mask
    img_circ=label(plt.imread(puncta_mask)[:,:,zplane])
    distance= ndi.distance_transform_edt(img_circ)
    local_max=morphology.local_maxima(distance)
    markers=ndi.label(local_max)[0]
    pmask= segmentation.watershed(img_circ,markers,mask=img_circ)
    return pmask #output the watersheded puncta image with labels