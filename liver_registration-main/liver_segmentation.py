import os
import keras.callbacks

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import models_small as M
import numpy as np
from predict_generater import DataGenerator
from scipy.ndimage import zoom, binary_fill_holes, binary_erosion
import Reza_functions2 as rf
import nibabel as nib
from PIL import Image
import matplotlib.pyplot as plt
import globals_val
import matplotlib
matplotlib.use('Agg')


class callbacks(keras.callbacks.Callback):
    def on_predict_batch_begin(self, batch, logs=None):
        globals_val.seg_percent = int((batch + 1) / self.params['steps'] * 100)

    def on_predict_begin(self, logs=None):
        globals_val.seg_percent = 0


def get_FOV(vol_ims):  # around_lung, lung

    vol_mask = np.where(vol_ims > 0, 1, 0)  # vol_im 儲存所有有值的部分(人體組織，也就是 不是肺的部分)

    # 對不是費的部分作侵蝕運算，得到中空部分(肺的區域)更廣泛的Mask
    shp = vol_mask.shape
    FOV = np.zeros((shp[0], shp[1], shp[2]), dtype=np.float32)
    for idx in range(shp[0]):
        FOV[idx, :, :] = binary_fill_holes(vol_mask[idx, :, :]).astype(vol_mask.dtype)
        FOV[idx, :, :] = binary_erosion(FOV[idx, :, :], structure=np.ones((30, 30))).astype(FOV.dtype)
        # FOV[idx, :, :] = binary_dilation(FOV[idx, :, :], structure=np.ones((25,25))).astype(FOV.dtype)
    return FOV


def prepare_test(path):
    slice = nib.load(path).get_data()

    lung = rf.hu_to_grayscale(slice, 1500, -600)
    lung = np.array(lung)

    soft = rf.hu_to_grayscale(slice, 400, 50)
    soft = np.array(soft)

    bone = rf.hu_to_grayscale(slice, 1800, 400)
    bone = np.array(bone)

    return lung, soft, bone


def load_niigz(path):
    slice_resize = []
    slice = nib.load(path).get_data()
    for s in slice:
        test_Img = Image.fromarray((s).astype(np.uint8))
        test_small_Img = test_Img.resize((256, 256), Image.ANTIALIAS)
        test_data = np.asarray(test_small_Img)
        slice_resize.append(test_data)

    slice_resize = np.asarray(slice_resize)

    return slice_resize


def save_as_plot(dicom, mask, predictions, output_path):
    output_path = output_path + '/'

    for n in range(dicom.shape[0]):
        plt.subplot(131)
        plt.title("dicom " + str(n))
        plt.imshow(dicom[n])
        plt.subplot(132)
        plt.title("ground_truth_mask " + str(n))
        plt.imshow(mask[n])
        plt.subplot(133)
        plt.title("prediction " + str(n))
        plt.imshow(predictions[n])
        plt.tight_layout()

        plt.savefig(output_path + "/" + str(n) + ".png")  #
        plt.close()

    return dicom.shape[0]-1


def liver_seg(data_name, mask_name):
    params = {'dim': (256, 256),
              'batch_size': 4,
              'n_classes': 1,  # 這個好像要處理一下，有看到說可以用1，或4的倍數
              'n_channels': 3,
              'shuffle': False
              }

    output_path = "predict_mask/"
    weight = "liver_model.hdf5"
    model = M.unet(input_size=(256, 256, 3))
    model.load_weights(weight)

    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    dicom_path = f'dicom_detection/{data_name}.nii.gz'
    dicom_p = nib.load(dicom_path)

    # FOV=get_FOV(dicom)

    lung, soft, bone = prepare_test(dicom_path)

    predict_generator = DataGenerator(lung, soft, bone, **params)

    predictions = model.predict(predict_generator, callbacks=[callbacks()])

    predictions = np.squeeze(predictions)

    predictions_mask = np.where(predictions > 0.5, 1, 0)
    predictions_mask = zoom(predictions_mask, (1, 2, 2))

    FOV = get_FOV(predictions_mask)

    Estimated_mask = np.where(FOV - predictions_mask > 0, 1, 0)  ##

    Estimated_mask = np.int32(Estimated_mask)

    mask_path = f'./mask_detection/{mask_name}.nii.gz'  # 這個你改成s11mask的位置
    mask = nib.load(mask_path).get_data()
    print('begin saving image')
    img_len = save_as_plot(dicom_p.get_data(), mask, Estimated_mask, './seg_png')
    print('saved image complete')
    out = nib.Nifti1Image(Estimated_mask, dicom_p.affine, dicom_p.header)
    nib.save(out, output_path + 'mask_' + dicom_path.split('/')[-1])
    return img_len


if __name__ == '__main__':
    liver_seg('s11', 's11')
