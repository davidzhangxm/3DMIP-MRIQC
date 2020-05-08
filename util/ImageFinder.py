from skimage import data
import SimpleITK as sitk
import numpy as np
from time import sleep
from scipy import ndimage
from skimage import io
import os
from skimage.io import imread


# from wls_filter import wlsFilter
# from srs import SRS
# from virtual_ev import VIG
# from tonemap import *
# import cv2

# import each and every file
def filelocation(directory):
    DEBUG =False
    l = []
    for file in os.listdir(directory):
        img = directory + file
        if DEBUG : print (img)
        l.append(img)
    # the os.listdir function do not give the files in the right order 
    #so we need to sort them
    l=sorted(l)
    return l

def org_image(n,l1):
    '''
    : n: image path list index
    : l1: image path list
    '''
    img_T1 = sitk.ReadImage(l1[n])  
    img_T1_255 = sitk.Cast(sitk.RescaleIntensity(img_T1), sitk.sitkUInt8)
    org_nda = sitk.GetArrayFromImage(img_T1_255)
    org_nda=org_nda[0,:,:]
    return img_T1, org_nda


def LoadOrginalImage(l1):
    first = True
    rng        = len(l1)
    img        = []
    cnt        = 0
    w = h = 0
    slice_distance = 0
    slice_thickness = 0
    for i in range(len(l1)):
        item = int(i)
        try:
            # img_T1, org_nda, img_T1_255
            # y: uint8
            x, y = org_image(item,l1)
            if first:
                # slice thickness property of meta data 
                # '0018|0050'
                first = False
                w, h = y.shape
                img = np.zeros((w, h, rng)) .astype(np.uint8)              #  Read image
                if '0018|0088' in x.GetMetaDataKeys():
                    slice_distance = x.GetMetaData('0018|0088')
                if '0018|0050' in x.GetMetaDataKeys():
                    slice_thickness = x.GetMetaData('0018|0050')

            img[:,:,item] = y
            cnt+= 1
            sleep(0.01)
        except:
            pass
        
    # imgInt = np.zeros((w,h,rng)).astype(np.int64)
    # for i in range(cnt):
    #     imgInt[:,:,i] = img[:,:,i].astype(np.int64)
        
    # return (imgInt,cnt, w, h, slice_distance, slice_thickness)
    return (img, cnt, w, h, slice_distance, slice_thickness)


# Unit Test
if __name__ == "__main__":
    # "/Users/xinmingzhang/Course/VR research/data/test/2012-08-31-MRI/series_3_COR_Fiesta/50476DC5"
    img = "/Users/xinmingzhang/Course/VR research/data/test/2012-08-31-MRI/series_3_COR_Fiesta/50476DC5"
    img_T1 = sitk.ReadImage(img)  
    img_T1_255 = sitk.Cast(sitk.RescaleIntensity(img_T1), sitk.sitkUInt8)
    org_nda = sitk.GetArrayFromImage(img_T1_255)
    org_nda=org_nda[0,:,:]

    image = 1.0 * cv2.cvtColor(org_nda, cv2.COLOR_GRAY2BGR) / 255

    # add filter
    S = 1.0*org_nda / np.max(org_nda)
    filtered_nda = wlsFilter(S)

    L = 1.0 * S
    I = filtered_nda
    R = np.log(L+1e-22) - np.log(I+1e-22)
    R_ = SRS(R, L)
    I_K = VIG(L, 1.0 - L)
    result = tonereproduct(image, L, R_, I_K, True) * 255
    # remember to scale result from (0,1) to (0,255)
    # and then change the data type from float32 to uint8
    result = result.astype('uint8')
    r = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    cv2.imshow('1', r)
    cv2.waitKey(0)
    print(r.shape)
    # return img_T1, org_nda