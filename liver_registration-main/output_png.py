import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.morphology import binary_fill_holes
from PIL import Image
import matplotlib
matplotlib.use('Agg')


def get_FOV(mask):  # around_lung, lung
    shp = mask.shape
    FOV = np.zeros((shp[0], shp[1], shp[2]), dtype=np.float32)
    for idx in range(shp[0]):
        FOV[idx, :, :] = binary_fill_holes(mask[idx, :, :]).astype(mask.dtype)

    return FOV


def load_niigz(path):
    slice_resize = []
    slice = nib.load(path).get_data()
    print(np.shape(slice))
    for s in slice:
        test_Img = Image.fromarray((s).astype(np.uint8))
        test_small_Img = test_Img.resize((256, 256), Image.ANTIALIAS)
        test_data = np.asarray(test_small_Img)
        slice_resize.append(test_data)

    slice_resize = np.asarray(slice_resize)

    return slice_resize


def save_as_plot(output_path, dicom=None, mask=None, predictions=None):
    if dicom is None and mask is None:
        for n in range(len(predictions)):
            plt.title(f'predictions: {n}')
            plt.imshow(predictions[n])
            plt.tight_layout()

            plt.savefig(output_path + "/" + str(n) + ".png")  #
            plt.close()
        return len(predictions)-1
    predictions = np.squeeze(predictions)  # 刪除長度為1的軸
    predictions_mask = np.where(predictions > 0.5, 1, 0)
    FOV = get_FOV(predictions)
    Estimated_mask = np.where((FOV - predictions_mask) > 0, 1, 0)  ##

    shp = predictions_mask.shape

    # 原圖上遮罩
    dicom_with_mask = np.zeros((shp[0], shp[1], shp[2]), dtype=np.float32)

    for i, per_dicom in enumerate(dicom):
        dicom_with_mask[i] = np.where(Estimated_mask[i] == 1, 255, per_dicom)  ##
    # 若輸入格式改了這個也要改

    print('save_plot')
    for n in range(dicom_with_mask.shape[0]):
        plt.subplot(221)
        plt.title("original_mask")
        plt.imshow(mask[n])
        plt.subplot(222)
        plt.title("Estimated_mask")
        plt.imshow(Estimated_mask[n])
        plt.subplot(223)
        plt.title("predict_with_dicom")
        plt.imshow(dicom_with_mask[n])
        plt.subplot(224)
        plt.title('dicom')
        plt.imshow(dicom[n])
        plt.tight_layout()

        plt.savefig(output_path + "/" + str(n) + ".png")  #
        plt.close()

    plt.close()
