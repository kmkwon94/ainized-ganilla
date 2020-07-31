# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os 
import random
import string
import uuid
import os
from options.test_options import TestOptions
from options.test_options import BaseOptions
from data import CreateDataLoader
from models import create_model
from util.visualizer import save_images
from util import html
from test import run

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

########################################################################
#preload Model
def loadModel(name):
    opt = TestOptions().parse()
    # hard-code some parameters for test
    opt.num_threads = 1   # test code only supports num_threads = 1
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # no shuffle
    opt.no_flip = True    # no flip
    opt.display_id = -1   # no visdom display
    opt.name = name
    #preload model
    model = create_model(opt)
    model.setup(opt)
    return [model, name]

AS_model = loadModel('AS_pretrained')
DM_model = loadModel('DM_pretrained')
KH_model = loadModel('KH_pretrained')
KP_model = loadModel('KP_pretrained')
MB_model = loadModel('MB_pretrained')
Miya_model = loadModel('Miyazaki_pretrained')
PP_model = loadModel('PP_pretrained')
RC_model = loadModel('RC_pretrained')
SC_model = loadModel('SC_pretrained')
SD_model =loadModel('SD_pretrained')
TR_model = loadModel('TR_pretrained')
########################################################################
# 업로드 HTML 렌더링
@app.route('/')
def render_file():
    return render_template('upload.html')

@app.route('/healthz', methods=['GET'])
def healthz():
    return "I am alive", 200
    
@app.route('/fileUpload', methods=['POST'])
def fileupload():
    check_value = request.form['check_model']

    if request.method == 'POST':
        f = request.files['file']
        # 저장할 경로 + 파일명
        # redirect할 것을 method명으로 처리함
        randomDirName = str(uuid.uuid4()) #사용자끼리의 업로드한 이미지가 겹치지 않게끔 uuid를 이용하여 사용자를 구분하는 디렉터리를 만든다.
        path = "/ganilla/upload/" + randomDirName
        target = {
            "as" : {
                "path" : path,
                "function": axel_scheffler
            }
        }    
        os.mkdir(target[check_value]["path"])
        f.save(target[check_value]["path"] + '/' + secure_filename(f.filename))
        return target[check_value]["function"](randomDirName)

#사용자의 입력을 받아서 각 원하는 결과물을 라우팅
def axel_scheffler(user_id):
    data_root = 'upload/' + user_id
    pretrain_model = 'AS_pretrained'
    result_dir = './results/' + user_id
    model = AS_model
    #cmd = "python3 test.py --dataroot upload/" + user_id + "--name AS_pretrained --results_dir " + user_id + " --model test"
    run(data_root, pretrain_model, result_dir, model)
    return render_template(result_dir + "/" + "index.html")

if __name__ == '__main__':
    #preload를 하기 위해서 모델 10개를 --name을 이용하여 모두 preloadModel 을 만들어줘야한다.
    """
            "dm" : {
                "path" : path,
                "function":
            },
            "kh" : {
                "path" : path,
                "function":
            },
            "kp" : {
                "path" : path,
                "function":
            },
            "mb" : {
                "path" : path,
                "function":
            },
            "pp" : {
                "path" : path,
                "function":
            },
            "rc" : {
                "path" : path,
                "function":
            },
            "sc" : {
                "path" : path,
                "function":
            },
            "sd" : {
                "path" : path,
                "function":
            },
            "tr" : {
                "path" : path,
                "function":
            },
            "mi" : {
                "path" : path,
                "function" :
            }
            """
    
    app.run(host='0.0.0.0', port=80, debug=True)