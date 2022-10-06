from PIL import Image
import cv2
import glob
import os
import numpy as np
import nibabel as nib
import logging

raw_niigz_path = 'dicom/'
raw_niigz = glob.glob(raw_niigz_path + '*')
raw_niigz = [i.replace('\\', '/') for i in raw_niigz]


dicom_out_path = 'dicom_detection/'
mask_out_path = 'mask_detection/'

if not os.path.isdir(dicom_out_path):
    os.mkdir(dicom_out_path)

CONFIDENCE_THRESHOLD = 0.4
NMS_THRESHOLD = 0.5
net = cv2.dnn.readNet("backup/yolo-obj_best.weights", "yolo-obj.cfg")
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(256, 256), scale=1 / 255, swapRB=True)
logger_format = '%(asctime)s server_msg:%(message)s'


def find_liver(data_loc):
    logger_path = f'logger/liver_detect.log'
    with open(logger_path, 'w'):
        pass
    logging.basicConfig(filename='logger/liver_detect.log', level=logging.INFO, format=logger_format)
    dicom_data_loc = ''
    if data_loc == 'detect':
        dicom_data_loc = f'upload_file/detect_dicom.nii.gz'
    else:
        dicom_data_loc = f'dicom/{data_loc}.nii.gz'
    logging.info(dicom_data_loc)
    dicom_n = nib.load(dicom_data_loc)
    dicom = dicom_n.get_data()

    mask_data_loc = ''
    if data_loc == 'detect':
        mask_data_loc = f'upload_file/detect_mask.nii.gz'
    else:
        mask_data_loc = f'mask/{data_loc}.nii.gz'
    print(f'dicom path:{dicom_data_loc}')
    print(f'mask path:{mask_data_loc}')

    mask_n = nib.load(mask_data_loc)
    mask = mask_n.get_data()

    min = 9999
    max = -1
    accumulation_out = -9999

    for i, img in enumerate(dicom):

        img = Image.fromarray((img * 255).astype(np.uint8)).convert('RGB')
        img = np.array(img)
        classes, scores, boxes = model.detect(img, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        logging.info(f'{i}, {classes}, {scores}, {boxes}')
        if not len(classes) == 0:  # 有東西
            if i < min: min = i
            if i > max: max = i
            accumulation_out = 0

        else:
            accumulation_out += 1
            if accumulation_out > 5: break
    logging.info(f"min= {min}")
    logging.info(f"max= {max}")
    if min > 5: min = min - 5
    if max < dicom.shape[0] - 6: max = max + 5
    out = nib.Nifti1Image(dicom[min:max], dicom_n.affine, dicom_n.header)
    nib.save(out, dicom_out_path + data_loc.split('/')[-1] + '.nii.gz')

    out = nib.Nifti1Image(mask[min:max], dicom_n.affine, dicom_n.header)
    nib.save(out, mask_out_path + data_loc.split('/')[-1] + '.nii.gz')


if __name__ == '__main__':
    find_liver('s11')
