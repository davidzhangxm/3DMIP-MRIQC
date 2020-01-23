# 3DMIP-MRIQC
## Description
This is one part of the project 3DMIP, the goal of this subpart is that given a set of slices of MRI image, 
and we will give quality assessment of this dataset so that the professional can select better quality MRI image dataset.

The current progress seperate image post processing quality score, number of slice and the thickness of the slice. 
The final goal is to combine those three parameters and give a comprehensive quality score.

The current solution combines the background foreground seperation, which is to filter the noise in the background and 
standadized quality metric system for MRI. 

## Brief introduction
![Alt text](https://github.com/davidzhangxm/3DMIP-MRIQC/blob/master/img/MRIqa%20(1).png)
![Alt text](https://github.com/davidzhangxm/3DMIP-MRIQC/blob/master/img/MRIqa%20(2).png)
![Alt text](https://github.com/davidzhangxm/3DMIP-MRIQC/blob/master/img/MRIqa%20(3).png)
![Alt text](https://github.com/davidzhangxm/3DMIP-MRIQC/blob/master/img/MRIqa%20(4).png)
![Alt text](https://github.com/davidzhangxm/3DMIP-MRIQC/blob/master/img/MRIqa%20(5).png)

## Usage
- install prerequisite
```
pip -r install requirements.txt
```
- run
input path is the directory containing all MRI slice, output path is the result segementation for foreground image
```
python mriqa.py -i <input path> -o <output path>
```

## Reference
[Background-Foreground-separation-of-MRI-images-using-Anisotropic-Diffusion-Filtering-Thresholding](https://github.com/erayon/Background-Foreground-separation-of-MRI-images-using-Anisotropic-Diffusion-Filtering-Thresholding)
[Standardized quality metric system for structural brain magnetic resonance images in multi-center neuroimaging study](https://www.ncbi.nlm.nih.gov/pubmed/30223797)
