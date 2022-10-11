from flask import Flask, request, send_file
from flask_cors import CORS
from liver_detection import find_liver
from liver_segmentation import liver_seg
from mask_to_pointcloud import mask_to_pointcloud
from liver_registation import liver_registation
from output_png import save_as_plot, load_niigz
import os
import json
import logging
import base64
import globals_val

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True
busy = False
seg_percent = 0

with open('logger/error.log', 'w'):
    pass
error_log = logging.getLogger('error_log')
logger_format = logging.Formatter('[%(asctime)s] :%(message)s')
fh = logging.FileHandler('logger/error.log')
format_fh = logging.StreamHandler()
format_fh.setFormatter(logger_format)
error_log.addHandler(fh)
error_log.addHandler(format_fh)

ALLOWED_EXTENSIONS = {'nii.gz'}


@app.route('/busy', methods=['GET'])
def check_server_status():
    print(f'busy ip:{request.remote_addr}')
    res = {
        'busy': busy
    }
    return json.dumps(res)


@app.route('/detect', methods=['POST'])
def liver_detect():
    try:
        print(f'liver_detect from:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        data_name = request.json['data_name']
        find_liver(data_name)
        logging.info('liver_detect finish')
        logging.info('generating png file')
        predictions = load_niigz(f'dicom_detection/{data_name}.nii.gz')
        image_len = save_as_plot('./detect_png', None, None, predictions)
        logging.info('generating png file finish')
        res = {
            'success': True,
            'image_len': image_len
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print('liver_detect finish')


@app.route('/detect_png', methods=['GET'])
def liver_detect_png():
    try:
        print(f'liver_detect_png from:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        pos = request.args['pos']
        image_path = f'./detect_png/{pos}.png'
        print(f'liver_detect_png asking:{image_path}')
        if not os.path.exists(image_path):
            raise Exception('file not found')
        file = open(image_path, 'rb')
        encoded_img = f'data:image/png;base64,{base64.b64encode(file.read()).decode()}'
        res = {
            'success': True,
            'image': encoded_img
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print(f'liver_detect_png finish')


@app.route('/detect_log', methods=['POST'])
def liver_detect_log():
    file = open('logger/liver_detect.log', 'r')
    lines = file.read().splitlines()
    return {'data': lines}


@app.route('/segmentation', methods=['POST'])
def liver_segmentation():
    try:
        print(f'liver_segmentation from:{request.remote_addr}')
        globals_val.init_globals()
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        data_name = request.json['data_name']
        print(f'liver_seg file:{data_name}')
        img_len = liver_seg(data_name, data_name)
        print('liver_seg finish')
        res = {
            'img_len': img_len,
            'success': True
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print(f'liver_segmentation finish')


@app.route('/seg_png', methods=['GET'])
def liver_seg_png():
    try:
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        pos = request.args['pos']
        image_path = f'./seg_png/{pos}.png'
        if not os.path.exists(image_path):
            raise Exception('file not found')
        file = open(image_path, 'rb')
        encoded_img = f'data:image/png;base64,{base64.b64encode(file.read()).decode()}'
        res = {
            'success': True,
            'image': encoded_img
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)


@app.route('/segmentation_process', methods=['POST'])
def liver_segmentation_process():
    res = {
        'process': globals_val.seg_percent
    }
    return json.dumps(res)


@app.route('/segmentation_pic', methods=['GET'])
def liver_segmentation_pic():
    try:
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        pos = request.args['pos']
        image_path = f'./predict_mask/{pos}.png'
        if not os.path.exists(image_path):
            raise Exception('file not found')
        file = open(image_path, 'rb')
        encoded_img = f'data:image/png;base64,{base64.b64encode(file.read()).decode()}'
        res = {
            'success': True,
            'image': encoded_img
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)


@app.route('/position', methods=['POST'])
def liver_position():
    try:
        print(f'liver_position from:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        data_name1 = request.json['data_name1']
        data_name2 = request.json['data_name2']
        print(f'file:{data_name1}, {data_name2}')
        mask_to_pointcloud(data_name1, data_name2)
        liver_registation()
        res = {
            'success': True
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print(f'liver_position finish')


@app.route('/position_file', methods=['GET'])
def position_file():
    file_name = request.args['f']
    return send_file(f'3d_model/{file_name}.pcd', as_attachment=True)


@app.route('/file/detect_dicom', methods=['POST'])
def file_detect_dicom():
    try:
        print(f'file_detect_dicom from:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        if 'file' not in request.files:
            raise Exception('file not uploaded')
        file = request.files['file']
        if file.filename == '':
            raise Exception('file not selected')
        if file.filename.split('.', 1)[1] not in ALLOWED_EXTENSIONS:
            raise Exception('file format needs to be .nii.gz')
        file.save('./upload_file/detect_dicom.nii.gz')
        res = {
            'success': True
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print('file_detect finish')


@app.route('/file/detect_mask', methods=['POST'])
def file_detect_mask():
    try:
        print(f'file_detect_mask from:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        if 'file' not in request.files:
            raise Exception('file not uploaded')
        file = request.files['file']
        if file.filename == '':
            raise Exception('file not selected')
        if file.filename.split('.', 1)[1] not in ALLOWED_EXTENSIONS:
            raise Exception('file format needs to be .nii.gz')
        file.save('./upload_file/detect_mask.nii.gz')
        find_liver('detect')
        logging.info('liver_detect finish')
        logging.info('generating png file')
        predictions = load_niigz(f'dicom_detection/detect.nii.gz')
        image_len = save_as_plot('./detect_png', None, None, predictions)
        logging.info('generating png file finish')
        res = {
            'success': True,
            'image_len': image_len
        }
        return json.dumps(res)
    except Exception as e:
        if str(e) != 'server is busy':
            busy = False
        error_log.error(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print('file_detect finish')


@app.route('/file/position', methods=['POST'])
def file_position():
    try:
        print(f'postion file addr:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        file = request.files['file']
        if request.form['count'] == 1:
            file.save('./upload_file/postion_file_1.nii.gz')
            res = {
                'success': True
            }
            return json.dumps(res)
        elif request.form['count'] == 2:
            file.save('./upload_file/postion_file_2.nii.gz')
            res = {
                'success': True
            }
            return json.dumps(res)
        else:
            res = {
                'success': False,
                'msg': 'invalid arguments'
            }
            return json.dumps(res)

    except Exception as e:
        error_log.error(repr(e))
        res = {
            'msg': str(e),
            'success': False
        }
        return json.dumps(res)


@app.route('/download/detect', methods=['POST'])
def return_detect_file():
    try:
        print(f'detect file sending addr:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        return send_file('dicom_detection/detect.nii.gz', as_attachment=True)
    except Exception as e:
        error_log.error(repr(e))
        res = {
            'msg': str(e),
            'success': False
        }
        return json.dumps(res)


@app.route('/download/segmentation', methods=['POST'])
def return_segmentation_file():
    try:
        print(f'segmentation file sending addr:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        return send_file('predict_mask/mask_detect.nii.gz', as_attachment=True)
    except Exception as e:
        error_log.error(repr(e))
        res = {
            'msg': str(e),
            'success': False
        }
        return json.dumps(res)


def create_app():
    CORS(app)
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        use_reloader=False
    )
    return app


if __name__ == '__main__':
    create_app()
