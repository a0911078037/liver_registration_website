import open3d as o3d
import numpy as np
import glob
import nibabel as nib
import cv2
import matplotlib.pyplot as plt
from scipy.ndimage import rotate
input_path='D:\\Rai_Thran\\liver_seg_full\\predict_nii.gz\\'
mask_path=glob.glob(input_path+'*')
test=nib.load(mask_path[2]).get_data()
test2=nib.load(mask_path[4]).get_data()
# test2=test


before_mask=open('before_mask.txt','w')
after_mask=open('after_mask.txt','w')

test_canny=[]
for i in test:
    canny=cv2.Canny(np.uint8(i),0.5,2)
    test_canny.append(canny)
test_canny=np.array(test_canny)

test2_canny=[]
for i in test2:
    canny=cv2.Canny(np.uint8(i),0.5,2)
    test2_canny.append(canny)
test2_canny=np.array(test2_canny)
test2_canny=rotate(test2_canny,60,(1,2))

point_list=[]
interval=50
pointer=0
print("making as before_mask.txt")
for z in range(test_canny.shape[0]):
    for x in range(test_canny.shape[1]):
        for y in range(test_canny.shape[2]):
            if test_canny[z,x,y]>0:
                if pointer%interval==0:
                    before_mask.write(str(z)+' '+str(x)+' '+str(y)+'\n')
                    point_list.append([z,x,y])
                pointer+=1
print(pointer/interval)
print('saving as ply / show')
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(point_list)
# o3d.io.write_point_cloud("before_mask.pcd", pcd)
o3d.visualization.draw_geometries([pcd])    

point_list=[]
interval=200
pointer=0
print("making as after_mask.txt")
for z in range(test2_canny.shape[0]):
    for x in range(test2_canny.shape[1]):
        for y in range(test2_canny.shape[2]):
            if test2_canny[z,x,y]>0:
                if pointer%interval==0:
                    after_mask.write(str(z)+' '+str(x)+' '+str(y)+'\n')
                    point_list.append([z,x,y])
                pointer+=1
print(pointer/interval)
print('saving as ply / show')
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(point_list)
# o3d.io.write_point_cloud("after_mask.pcd", pcd)
o3d.visualization.draw_geometries([pcd])
