from genericpath import isdir
from PIL import Image
import cv2
import glob
import os
import numpy as np
import nibabel as nib
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
import models_small as M
import SimpleITK as sitk
from predict_generater import DataGenerator
from scipy.ndimage.morphology import binary_fill_holes,binary_erosion
from scipy.ndimage import zoom
import Reza_functions2 as rf
import matplotlib.pyplot as plt
import copy
import time
import open3d as o3
from probreg import cpd



def liver_detection(before_niigz_path,after_niigz_path):

    start=time.time()

    raw_niigz=[before_niigz_path,after_niigz_path]

    CONFIDENCE_THRESHOLD=0.4
    NMS_THRESHOLD=0.5
    net = cv2.dnn.readNet("backup/yolo-obj_best.weights", "yolo-obj.cfg")
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(size=(256, 256), scale=1/255, swapRB=True)

    dicom_list=[]
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
        dicom_list.append(dicom[min:max])

    prosses_time=time.time()-start
    print("detection_time=",prosses_time)

    return dicom_list


def get_FOV(vol_ims):#around_lung, lung

    vol_mask = np.where(vol_ims>0, 1, 0) # vol_im 儲存所有有值的部分(人體組織，也就是 不是肺的部分)

    # 對不是費的部分作侵蝕運算，得到中空部分(肺的區域)更廣泛的Mask
    shp = vol_mask.shape
    FOV = np.zeros((shp[0], shp[1], shp[2]), dtype=np.float32)
    for idx in range(shp[0]):
        FOV[idx, :, :] = binary_fill_holes(vol_mask[idx, :, :]).astype(vol_mask.dtype)
        FOV[idx, :, :] = binary_erosion(FOV[idx, :, :], structure=np.ones((30,30))).astype(FOV.dtype)
        #FOV[idx, :, :] = binary_dilation(FOV[idx, :, :], structure=np.ones((25,25))).astype(FOV.dtype)
    return FOV

def prepare_test(slice):

    lung=rf.hu_to_grayscale(slice,1500,-600)
    lung=np.array(lung)

    soft=rf.hu_to_grayscale(slice,400,50)
    soft=np.array(soft)

    bone=rf.hu_to_grayscale(slice,1800,400)
    bone=np.array(bone)

    return lung,soft,bone


def load_niigz(slice):
    
    slice_resize=[]
    for s in slice:
        test_Img = Image.fromarray((s).astype(np.uint8))
        test_small_Img = test_Img.resize((256,256), Image.ANTIALIAS)
        test_data = np.asarray(test_small_Img)
        slice_resize.append(test_data)
    
    slice_resize=np.asarray(slice_resize)
    return slice_resize

def segmentation(dicom_for_seg):
    start=time.time()
    params = {'dim': (256,256),
          'batch_size': 12,
          'n_classes': 1, # 這個好像要處理一下，有看到說可以用1，或4的倍數
          'n_channels': 3,
          'shuffle':False
          }

    
    weight="segmentation_weight"
    model = M.unet(input_size = (256,256,3))
    model.load_weights(weight) 



    done=0
    predict_mask=[]
    for dicom in dicom_for_seg:
        print(done,'/',len(dicom_for_seg)-1)
        done+=1

        dicom=load_niigz(dicom)#標準化
        # FOV=get_FOV(dicom)

        lung,soft,bone=prepare_test(dicom)

        predict_generator = DataGenerator(lung,soft,bone,**params)

        predictions = model.predict(predict_generator, verbose=1)
        
        predictions=np.squeeze(predictions)
        
        predictions_mask = np.where(predictions>0.5, 1, 0)
        predictions_mask = zoom(predictions_mask, (1,2,2))

        FOV=get_FOV(predictions_mask)

        Estimated_mask = np.where(FOV - predictions_mask>0, 1, 0)##

        Estimated_mask=np.int32(Estimated_mask)
        predict_mask.append(Estimated_mask)

    prosses_time=time.time()-start
    print("segmentation_time=",prosses_time)

    return predict_mask

def prn_obj(obj): 
    print ('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))
    
def registration(before_point,after_point):
    start=time.time()
    # load source and target point cloud
    source = o3.geometry.PointCloud()
    target = o3.geometry.PointCloud()
    source.points = o3.utility.Vector3dVector(before_point)
    target.points = o3.utility.Vector3dVector(after_point)
    print(source)
    print(target)

    # compute cpd registration
    tf_param, _, _ = cpd.registration_cpd(source, target)
    result = copy.deepcopy(source)
    result.points = tf_param.transform(result.points)

    prn_obj(tf_param)
    
    output_file="result/"
    if not os.path.isdir(output_file):
        os.mkdir(output_file)

    transform_matrix_rot=open(output_file+'transform_matrix_rot.txt','w')
    for rot in tf_param.rot:
        transform_matrix_rot.write(str(rot[0])+' '+str(rot[1])+' '+str(rot[2])+'\n')

    transform_matrix_t=open(output_file+'transform_matrix_t.txt','w')
    transform_matrix_t.write(str(tf_param.t[0])+' '+str(tf_param.t[1])+' '+str(tf_param.t[2])+'\n')

    scale_txt=open(output_file+'scale.txt','w')
    scale_txt.write(str(tf_param.scale))

    # draw result
    source.paint_uniform_color([1, 0, 0])
    target.paint_uniform_color([0, 1, 0])
    result.paint_uniform_color([0, 0, 1])
    
    #o3.visualization.draw_geometries([ source,target,result])#,tranform_mask

    prosses_time=time.time()-start
    print("registration_time=",prosses_time)

def mask_to_pointcloud(predict_mask):

    start=time.time()

    before_canny=[]
    for i in predict_mask[0]:
        canny=cv2.Canny(np.uint8(i),0.5,2)
        before_canny.append(canny)
    before_canny=np.array(before_canny)

    after_canny=[]
    for i in predict_mask[1]:
        canny=cv2.Canny(np.uint8(i),0.5,2)
        after_canny.append(canny)
    after_canny=np.array(after_canny)


    before_point=[]
    interval=50
    pointer=0
    print("making as before_mask.txt")
    for z in range(before_canny.shape[0]):
        for x in range(before_canny.shape[1]):
            for y in range(before_canny.shape[2]):
                if before_canny[z,x,y]>0:
                    if pointer%interval==0:
                        before_point.append([z,x,y])
                    pointer+=1
    print(pointer/interval)
    # pcd = o3.geometry.PointCloud()
    # pcd.points = o3.utility.Vector3dVector(point_list)
    # o3.visualization.draw_geometries([pcd])    

    after_point=[]
    interval=50
    pointer=0
    print("making as after_mask.txt")
    for z in range(after_canny.shape[0]):
        for x in range(after_canny.shape[1]):
            for y in range(after_canny.shape[2]):
                if after_canny[z,x,y]>0:
                    if pointer%interval==0:
                        after_point.append([z,x,y])
                    pointer+=1
    print(pointer/interval)
    # pcd = o3.geometry.PointCloud()
    # pcd.points = o3.utility.Vector3dVector(point_list)
    # o3.visualization.draw_geometries([pcd])

    prosses_time=time.time()-start
    print("make_point_cloud_time=",prosses_time) 

    return before_point,after_point
if __name__=='__main__':

    before_niigz_path='dicom/s11.nii.gz'
    after_niigz_path='dicom/s12.nii.gz'

    start=time.time()
    dicom_for_seg=liver_detection(before_niigz_path,after_niigz_path)
    predict_mask=segmentation(dicom_for_seg)
    before_point,after_point=mask_to_pointcloud(predict_mask)
    registration(before_point,after_point)
    prosses_time=time.time()-start
    print("time=",prosses_time)
    

