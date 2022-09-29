import copy
import numpy as np
import open3d as o3
from probreg import cpd
import time


def prn_obj(obj):
    print('\n'.join(['%s:%s' % item for item in obj.__dict__.items()]))


def liver_registation():
    # load source and target point cloud
    source = o3.geometry.PointCloud()
    target = o3.geometry.PointCloud()
    source.points = o3.utility.Vector3dVector(np.loadtxt('before_mask.txt'))
    target.points = o3.utility.Vector3dVector(np.loadtxt('after_mask.txt'))
    print(source)
    print(target)

    # compute cpd registration
    start = time.time()
    tf_param, _, _ = cpd.registration_cpd(source, target)
    result = copy.deepcopy(source)
    result.points = tf_param.transform(result.points)

    prn_obj(tf_param)

    transform_matrix_rot = open('transform_matrix_rot.txt', 'w')
    for rot in tf_param.rot:
        transform_matrix_rot.write(str(rot[0]) + ' ' + str(rot[1]) + ' ' + str(rot[2]) + '\n')

    transform_matrix_t = open('transform_matrix_t.txt', 'w')
    transform_matrix_t.write(str(tf_param.t[0]) + ' ' + str(tf_param.t[1]) + ' ' + str(tf_param.t[2]) + '\n')

    scale_txt = open('scale.txt', 'w')
    scale_txt.write(str(tf_param.scale))

    # draw result
    source.paint_uniform_color([1, 0, 0])
    target.paint_uniform_color([0, 1, 0])
    result.paint_uniform_color([0, 0, 1])
    # o3.visualization.draw_geometries([ target, result])
    #############################################################
    before_txt = np.loadtxt('before_mask.txt')
    after_txt = np.loadtxt('after_mask.txt')
    tranform_matrix = tf_param.rot
    tranform_matrix2 = tf_param.t
    scale = tf_param.scale

    tranform_mask_txt = before_txt  # +target.get_center()-source.get_center()
    tranform_mask = o3.geometry.PointCloud()
    tranform_mask.points = o3.utility.Vector3dVector(tranform_mask_txt)
    tranform_mask.paint_uniform_color([0.706, 0, 0])
    tranform_mask = tranform_mask.translate(target.get_center(), relative=False)
    tranform_mask = tranform_mask.scale(scale, source.get_center())
    tranform_mask = tranform_mask.rotate(tranform_matrix)  # ,center=after_mask.get_center()

    # merge three point to cloud in to ones
    # source red
    # target green
    # result blue

    # o3.visualization.draw_geometries([source])  # ,tranform_mask
    o3.io.write_point_cloud('3d_model/source.pcd', source, write_ascii=True)
    o3.io.write_point_cloud('3d_model/target.pcd', target, write_ascii=True)
    o3.io.write_point_cloud('3d_model/result.pcd', result, write_ascii=True)
    # 給befoe_mask中的點來映射到after_mask上
    print("before", before_txt)
    before = before_txt
    after = (np.dot(before, tranform_matrix.T) + tranform_matrix2) * scale
    after = [[round(i[0]), round(i[1]), round(i[2])] for i in after]
    after = np.array(after)
    print("after", after)
    elapsed = time.time() - start
    print("time: ", elapsed)


if __name__ == '__main__':
    liver_registation()

