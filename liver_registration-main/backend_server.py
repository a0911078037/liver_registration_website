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
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print('liver_detect finish')
        busy = False


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
        print(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print(f'liver_detect_png finish')
        busy = False


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
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print(f'liver_segmentation finish')
        busy = False


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
        print(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        busy = False


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
        print(repr(e))
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        busy = False


@app.route('/position', methods=['POST'])
def liver_position():
    try:
        print(f'liver_position from:{request.remote_addr}')
        global busy
        if busy:
            raise Exception('server is busy')
        busy = True
        mask_to_pointcloud()
        liver_registation()
        res = {
            'success': True
        }
        return json.dumps(res)
    except Exception as e:
        res = {
            'success': False,
            'msg': str(e)
        }
        return json.dumps(res)
    finally:
        print(f'liver_position finish')
        busy = False


@app.route('/position_file', methods=['GET'])
def position_file():
    file_name = request.args['f']
    return send_file(f'3d_model/{file_name}.pcd', as_attachment=True)


def create_app():
    CORS(app)
    app.run(
        host='192.168.0.105',
        port=8000,
        debug=True,
        use_reloader=True
    )


if __name__ == '__main__':
    create_app()
