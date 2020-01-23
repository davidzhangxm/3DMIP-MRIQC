# # import Dependencies
import sys
import os
from os import path

import matplotlib.pyplot as plt
import numpy as np
import warnings

sys.path.append(path.abspath('./util'))

from AnDiffusion import *
from MaskGenAlgo import *
from tqdm import tqdm
from hysteresisThresholding import apply_hysteresis_threshold
from time import sleep
from skimage.morphology import erosion, dilation, opening, closing, white_tophat
from skimage.morphology import disk
from ImageFinder import *
from scipy.stats import norm
from scipy.ndimage.morphology import binary_fill_holes


#print("Enter image folder path: ")
#Ipath = input()
#print("Enter path where to save the results: ")
#Spath = input()

#Dicom location
# Ipath  = "./sample_mri_image(DICOM)/"
# Ipath = "../data/series_1_localizer_BH/"
# Spath  = "./OutputImg-Larry/"

def load_mask(Ipath, Opath):
    print("The dataset path is " + Ipath)
    print("Loading images .......... ")
    l = filelocation(Ipath)
    [orgImge,nofimage,w,h, slice_thickness] =  LoadOrginalImage(l)
    if nofimage == 0:
        print("There is no image in this directory")
        exit(1)

    print("Done! no of images: " + str(nofimage))

    print("Apply pipeline for generate masks.....")

    mask   = np.zeros((w,h,nofimage))
    # fgnd   = np.zeros((512,512,nofimage))
    actImg = np.zeros((w,h,nofimage))
    selem  = disk(4)
    for i in tqdm(range(nofimage)):
        img             = orgImge[:,:,i]
        diff            = anisodiff(img,20,50,0.1)
        mu,sigma        = norm.fit(diff)
        htr             = apply_hysteresis_threshold(diff,mu,sigma).astype(int)
        pmask           = binary_fill_holes(htr)
        eroded          = erosion(pmask, selem)
        [fg,bg]         = foregroundBackground(eroded,img)
        mask[:,:,i]     = eroded
        # fgnd[:,:,i]     = fg
        actImg[:,:,i]   = img
        sleep(0.1)
    
    dictr = Opath
    for i in tqdm(range(nofimage)):
        x=l[i].split("/")
        loc1=dictr+x[-1]+'.png'
        # loc2=dictr+x[-1]+'fg'+'.png'
        loc3=dictr+x[-1]+'actImg'+'.png'
        plt.imsave(loc1,mask[:,:,i],cmap = plt.cm.gray) # save psudo mask
        # plt.imsave(loc2,fgnd[:,:,i],cmap = plt.cm.gray)
        plt.imsave(loc3,actImg[:,:,i],cmap = plt.cm.gray)


    print("Done! ")

    return mask, actImg, slice_thickness


