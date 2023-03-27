"""
An example code for generating cellmask from GRAYSCALE images using Cellpose algorithm
Custom trained model is used for generating the masks and can be replaced with any custom trained model. 
Note- make sure the custom trained model is saved in the models folder under .cellpose folder(usually in your c folder)
"""
# import Packages
import fnmatch
from cellpose import  io, models
from channel_extract import channel_extract
from savepmask_to_txt import savepmask_to_txt


#enter the location of the folder which has GFP and TRITC files. 
GFP_filesb, TRITC_files = channel_extract(r"G:example/path/", "*GFPNSB*.tif",)

#enter the wells to analyze.  
required_wells= ['*B04*','*D04*','*G04*','*C04*','*E04*','*F04*'] 
  
#selecting images contaning the keyword in required_wells:
GFP_fil_all=[]

for well in required_wells:    
    for filename in GFP_filesb:
        if fnmatch.fnmatch(filename, well):
           GFP_fil_all.append(filename)
#%%
#enter the folder path where the masks need to be saved. 
cpath= r"G:example/path"

# DEFINE CELLPOSE MODEL (From cellpose Github)
# model_type='cyto' or model_type='nuclei'
#model = models.Cellpose(gpu=False, model_type='cyto')
model = models.CellposeModel(gpu=True, model_type='A549-LC3_trained_model')

# define CHANNELS to run segementation on
# grayscale=0, R=1, G=2, B=3
# channels = [cytoplasm, nucleus]
# if NUCLEUS channel does not exist, set the second channel to 0
# channels = [0,0]
# IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
# channels = [0,0] # IF YOU HAVE GRAYSCALE
# channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
# channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

# or if you have different types of channels in each image
channels = [0,0]

diam_labels = model.diam_labels.copy()    
#if diameter is set to None, the size of the cells is estimated on a per image basis
# you can set the average cell `diameter` in pixels yourself (recommended) 
# diameter can be a list or a single number for all images


#generating cell masks and saving them as text files for further processing(optional)
for filename in GFP_fil_all:
    img = io.imread(filename)
    masks, flows, diams = model.eval(img, diameter = diam_labels, channels=channels)
    savepmask_to_txt(masks, filename, label='cell', path=cpath)

