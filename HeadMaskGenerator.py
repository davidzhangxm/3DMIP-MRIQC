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

from HDR_filter import HDRFilter


#print("Enter image folder path: ")
#Ipath = input()
#print("Enter path where to save the results: ")
#Spath = input()

#Dicom location
# Ipath  = "./sample_mri_image(DICOM)/"
# Ipath = "../data/series_1_localizer_BH/"
# Spath  = "./OutputImg-Larry/"

def load_mask(Ipath, hdr, Opath=None):
    print("The dataset path is " + Ipath)
    print("Loading images .......... ")
    l = filelocation(Ipath)
    # delete extra mac system attribute file
    if l[0].split('/')[-1] == '.DS_Store':
        l.pop(0)
    [orgImge,nofimage,w,h, slice_distance, slice_thickness] =  LoadOrginalImage(l)

    if nofimage == 0:
        print("There is no image in this directory")
        exit(1)

    print("Done! no of images: " + str(nofimage))

    print("Apply pipeline for generate masks.....")

    mask   = np.zeros((w,h,nofimage))
    # fgnd   = np.zeros((512,512,nofimage))
    actImg = np.zeros((w,h,nofimage))
    selem  = disk(4)
    filter = HDRFilter(True)
    for i in tqdm(range(nofimage)):
        raw_img             = orgImge[:,:,i]
        # print(raw_img.dtype)
        imgInt = raw_img.astype(np.int64)
        diff            = anisodiff(imgInt,20,50,0.1)
        mu,sigma        = norm.fit(diff)
        htr             = apply_hysteresis_threshold(diff,mu,sigma).astype(int)
        pmask           = binary_fill_holes(htr)
        eroded          = erosion(pmask, selem)
        # [fg,bg]         = foregroundBackground(eroded,imgInt)
        mask[:,:,i]     = eroded
        # fgnd[:,:,i]     = fg
        # HDR filter
        if hdr:
            print("HDR")
            actImg[:,:,i]   = pmask * filter.process(raw_img)
        else:
            actImg[:,:,i] = imgInt
        sleep(0.1)
    
    if Opath is not None:
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

    return mask, actImg, slice_distance, slice_thickness


