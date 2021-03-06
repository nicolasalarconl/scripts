# %%
from matplotlib import pyplot as plt
from auxiliaryFunctions import AuxiliaryFunctions
from listEllipses import ListEllipses
from randomImage import RandomImage
from astropy.io import fits
import cupy as cp
#import numpy as cp
import numpy as np
import time


# %%
class DatasetImages:  
    def __init__(self,size_image,device,path_save = None,path_read = None): 
        self.size_image =size_image
        self.path_save = self.init_path_save(path_save)
        self.path_read = self.init_path_read(path_read)
        self.params = []       
        self.images = []
        self.times = []
        self.masks = []
        self.device = self.init_device(device)
  
    def init_device(self,device):
        cp.cuda.Device(device).use()
        return device

    def init_path_save(self,path_save):
        if (path_save == None):
            return'../../datasets/images_'+str(self.size_image)+'x'+str(self.size_image)+'/images'
        else:
            return path_save
    def init_path_read(self,path_read):
        if (path_read == None):
            return'../../datasets/images_'+str(self.size_image)+'x'+str(self.size_image)+'/images'
        else:
            return path_read

    def recursion_average(self):
        a = np.array(self.recursions)
        return cp.sum(a)/(self.len_images())

    def time_averange(self):
        a = np.array(self.times)
        return cp.sum(a)/(self.len_images())
    
    def len_images(self):
        return len(self.images)
    
    def save(self,size_image,params,stop,start = None,path = None):
        self.size_image  = size_image
        self.params = params
        if (start is None):
            start = 0
        if(path is not None):   
            self.path_save = path
        
        AuxiliaryFunctions.make_dir(self.path_save)        
        list_figure_random = ListEllipses(params,start,self.device)
        self.recursions = []
        self.times = []
        for index in cp.arange(int(start),int(stop),1):
            start_time = time.time()
            cleanImage  = RandomImage(list_figure_random,index,self.device)
            hdu_image =fits.PrimaryHDU(cp.asnumpy(cleanImage.image))     
            hdu_image.writeto(self.path_save+'/image_'+str(self.size_image)+'x'+str(self.size_image)+'_'+str(index)+'.fits',
                            overwrite=True)
            AuxiliaryFunctions.write_csv(
                     self.path_save+'/image_'+str(self.size_image)+'x'+str(self.size_image)+'_'+str(index)+'.csv',
                cleanImage.mask)
            stop_time = time.time()
            self.times.append(stop_time-start_time) 
            self.recursions.append(cleanImage.recursion)
        
    def create(self,size_image,params,stop,start = None):
        self.size_image  = size_image
        self.params = params
        if (start is None):
            start = 0
        list_figure_random = ListEllipses(params,start,self.device)
        self.recursions = []
        self.times = []
        images = []
        for index in cp.arange(int(start),int(stop),1):
            start_time = time.time()
            image = RandomImage(list_figure_random,index,self.device)
            images.append(image.image)
            stop_time = time.time()
            self.times.append(stop_time-start_time)
            self.recursions.append(image.recursion)
        self.images = images
    
    def read(self,size_image,start,stop,path = None):
        self.size_image  = size_image
        if(path != None):   
            self.path_read= path
        AuxiliaryFunctions.make_dir(self.path_read)
        self.images = []
        self.masks = []
        for index in cp.arange(int(start),int(stop)):
            path_file = self.path_read+'/image_'+str(self.size_image)+'x'+str(self.size_image)+'_'+str(index)
            path_image = path_file+'.fits'
            path_mask = path_file+'.csv'
            hdul=fits.open(path_image)
            data = hdul[0].data.astype(cp.float32)
            image = cp.reshape(data,[self.size_image,self.size_image])
            image  = cp.array(image)      
            mask =  AuxiliaryFunctions.read_csv(path_mask)
            self.images.append(image)
            self.masks.append(mask)
        


    def view(self,index = None):
        if  (index is None):
            index = 1
        if (self.len_images() <= index):
            print("index out of bounds, index max: "+str(self.len_images()-1))
        else:
            plt.imshow(cp.asnumpy(self.images[index]))


# %%
#from paramsEllipses import ParamsEllipses
#params = ParamsEllipses(128)
#dataset = DatasetImages(128) 
#dataset.save(size_image = 128,params = params,stop =10)
#x = dataset.read(size_image = 128,stop = 10)


# %%


# %%
