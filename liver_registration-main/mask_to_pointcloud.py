import open3d as o3d
import numpy as np
import nibabel as nib
import cv2


def mask_to_pointcloud():
    before_path = 'predict_mask/mask_s11.nii.gz'
    after_path = 'predict_mask/mask_s12.nii.gz'
    test = nib.load(before_path).get_data()
    test2 = nib.load(after_path).get_data()
    # test2=test
    slice_thickness_before = nib.load(before_path).header["pixdim"][3]
    slice_thickness_after = nib.load(after_path).header["pixdim"][3]

    before_mask = open('before_mask.txt', 'w')
    after_mask = open('after_mask.txt', 'w')

    before_canny = []
    for i in test:
        canny = cv2.Canny(np.uint8(i), 0.5, 2)
        before_canny.append(canny)
    before_canny = np.array(before_canny)

    after_canny = []
    for i in test2:
        canny = cv2.Canny(np.uint8(i), 0.5, 2)
        after_canny.append(canny)
    after_canny = np.array(after_canny)

    interval = 50
    before_point = []
    pointer = 0
    print("making as before_mask.txt")
    for z in range(before_canny.shape[0]):
        if z % (5 // slice_thickness_before) == 0:
            for x in range(before_canny.shape[1]):
                for y in range(before_canny.shape[2]):
                    if before_canny[z, x, y] > 0:
                        if pointer % interval == 0:
                            before_mask.write(str(z) + ' ' + str(x) + ' ' + str(y) + '\n')
                            before_point.append([z, x, y])
                        pointer += 1
    print(pointer / interval)
    print('saving as ply / show')
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(before_point)
    # o3d.visualization.draw_geometries([pcd])

    after_point = []
    pointer = 0
    print("making as after_mask.txt")
    for z in range(after_canny.shape[0]):
        if z % (5 // slice_thickness_after) == 0:
            for x in range(after_canny.shape[1]):
                for y in range(after_canny.shape[2]):
                    if after_canny[z, x, y] > 0:
                        if pointer % interval == 0:
                            after_mask.write(str(z) + ' ' + str(x) + ' ' + str(y) + '\n')
                            after_point.append([z, x, y])
                        pointer += 1
    print(pointer / interval)
    print('saving as ply / show')
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(after_point)
    # o3d.visualization.draw_geometries([pcd])
