import cv2
import os
import numpy as np
from scipy.ndimage import maximum_filter, minimum_filter
import argparse
import time

from HeadMaskGenerator import load_mask

'''
calculate all MRI image score in the dataset
return individual score for each image

input => masks_img, foreground_img
output => average score of current dataset
'''
def mriqa(masks, imgs):
    _, _, n = masks.shape
    scores = []
    for i in range(n):
        img = imgs[:,:,i]
        mask = masks[:,:,i]

        # normalize img
        norm_img = cv2.normalize(img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

        gray = norm_img
        # contrast feature img
        window = (13, 13)
        maximg = maximum_filter(gray, size = window)
        minimg = minimum_filter(gray, size = window)
        contrast_img = maximg - minimg
        # image moment
        grayscale_moment = cv2.moments(gray)['nu20']
        contrast_moment = cv2.moments(contrast_img)['nu20']
        # binary image
        fgmg = (gray > grayscale_moment).astype(np.int)
        fcmg = (gray > contrast_moment).astype(np.int)
        fcmc = (contrast_img > contrast_moment).astype(np.int)
        fgmc = (contrast_img > grayscale_moment).astype(np.int)

        # luminance contrast quality score
        q11 = fcmg & fgmg
        q1 = np.sum(q11) / max(np.sum(fcmg), np.sum(fgmg))

        # texture score
        q22 = fgmc & fcmc
        q2 = np.sum(q22) / max(np.sum(fgmc), np.sum(fgmg))

        # texture contrast quality score
        q33 = fgmc & fcmc
        q3 = np.sum(q33) / np.sum(mask)

        # lightness quality score
        q44 = fcmg & fgmg
        q4 = np.sum(q44) / np.sum(mask)

        # weight
        w1 = w2 = w4 = 0.1
        w3 = 0.7
        Q = w1 * q1 + w2 * q2 + w3 * q3 + w4 * q4

        scores.append(Q)
    return scores

# load mask img and dicom img file name
def fileImgLoad(Opath):
    dcms_path = []
    masks_path = []
    for file in os.listdir(Opath):
        exten = file.split('.')[1]
        if exten == "dcm":
            dcms_path.append(Opath + file)
        elif exten == "dcmactImg":
            masks_path.append(Opath + file)
    
    return masks_path, dcms_path

# read image
def ImgLoader(masks_path, dcms_path):
    masks = []
    fgs = []
    first = True
    for i,mask in enumerate(masks_path):
        mask_img = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
        # norm_image = cv2.normalize(mask_img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        if first:
            first = False
            w, h = mask_img.shape
            masks = np.zeros((w, h, len(masks_path)))
        masks[:,:,i] = mask_img
    
    first = True
    for i,fg in enumerate(dcms_path):
        fg_img = cv2.imread(fg, cv2.IMREAD_GRAYSCALE)
        # norm_image = cv2.normalize(fg_img, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        if first:
            first = False
            w, h = fg_img.shape
            fgs = np.zeros((w, h, len(dcms_path)))
        fgs[:,:,i] = fg_img
    
    return masks, fgs


# load generated mask image and dicomimg
def load_existing_mask(Opath):
    masks_path, dcms_path = fileImgLoad(Opath)
    # read 
    masks, imgs = ImgLoader(masks_path, dcms_path)
    return masks, imgs

# slice property
# from f(x) = e^(-pi*(x-1)^2)
def slice_score(slice_thickness, slice_spacing):
    p = slice_thickness / slice_spacing
    return np.exp(-np.pi * (p - 1)**2)

# weight control for final score
def final_score(img_score, slice_score):
    return img_score * 0.7 + slice_score * 0.3

def directory_score(directory):
    """
    :param directory: Input directory containg MRI images
    :return: metric (img_quality_score, img_slice_score, num_slices, total_score, time_consuming)
    """
    print(f"Starting process directory {directory}")
    masks  = []
    imgs = []
    thickness = 0

    masks, imgs, distance, thickness = load_mask(directory)

    scores = mriqa(masks, imgs)
    img_score = sum(scores) / len(scores)
    s_score = slice_score(float(thickness), float(distance))
    score = final_score(img_score, s_score)

    print(f"Processed the directory {directory}")
    return (img_score, s_score, len(scores), score)



if __name__ == "__main__":
    # parsing command line arguments 
    # Input paht of MRI image dataset
    # Output result of foreground image 
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()
    
    if args.input is None or args.output is None:
        print("Please python mriqa.py -i <input path> -o <output path> for calculate dataset quality score")

    Ipath = args.input
    Opath = args.output
    # Ipath = "../data/series_216_SGE_fs_ax_113_2.55_256x256/"
    # Ipath = "../pydicom-playground/data/"
    # Opath = "../bfg/OutputImg-Larry-8/"
    # Opath = "./OutputImg-sample"



    masks  = []
    imgs = []
    thickness = 0

    if not os.path.exists(Opath):
        os.makedirs(Opath)

    masks, imgs, distance, thickness = load_mask(Ipath, Opath)

    scores = mriqa(masks, imgs)
    img_score = sum(scores) / len(scores)
    s_score = slice_score(float(thickness), float(distance))
    score = final_score(img_score, s_score)

    print(f"The dataset quality is {score}")
    print(f"The number of slice is {len(scores)}")

    # check difference between new generated img and existing img

    # masks_e, imgs_e = load_existing_mask(Opath)
    # masks_n, imgs_n = load_mask(Ipath, Opath)
    # _,_,n = masks_e.shape
    # for i in range(n):
    #     m_e = masks_e[:,:,i]
    #     m_e = cv2.normalize(m_e, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    #     m_n = masks_n[:,:,i]
    #     m_d = m_e - m_n

    #     i_e = imgs_e[:,:,i]
    #     i_n = imgs_n[:,:,i]
    #     i_d = i_e - i_n