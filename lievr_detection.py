from PIL import Image
import cv2
import glob
import os
import numpy as np
import nibabel as nib
raw_niigz_path='dicom/'
raw_niigz=glob.glob(raw_niigz_path+'*')
raw_niigz=[i.replace('\\','/') for i in raw_niigz]

dicom_out_path='dicom_for_liver_seg/'
if not os.path.isdir(dicom_out_path):
        os.mkdir(dicom_out_path)

CONFIDENCE_THRESHOLD=0.4
NMS_THRESHOLD=0.5
net = cv2.dnn.readNet("backup/yolo-obj_best.weights", "yolo-obj.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(256, 256), scale=1/255, swapRB=True)

def find_liver():

    for dicom_p in raw_niigz:

        print(dicom_p)
        dicom_n=nib.load(dicom_p)
        dicom=dicom_n.get_data()
        min=9999
        max=-1
        accumulation_out=-9999

        for i,img in enumerate(dicom):

            img=Image.fromarray((img*255).astype(np.uint8)).convert('RGB')
            img=np.array(img)
            classes, scores, boxes = model.detect(img, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
            print(i,classes,scores,boxes)
            if not len(classes)==0:#有東西
                if i<min:min=i
                if i>max:max=i
                accumulation_out=0

            else:
                accumulation_out+=1
                if accumulation_out>5: break
        print("min=",min)
        print("max=",max)
        if min>5:min=min-5
        if max<dicom.shape[0]-6:max=max+5
        out = nib.Nifti1Image(dicom[min:max],dicom_n.affine,dicom_n.header)
        nib.save(out,dicom_out_path + dicom_p.split('/')[-1])


            

if __name__=='__main__':
    
    find_liver()

