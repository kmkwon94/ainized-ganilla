# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
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
import numpy as np
import shutil
import PIL
from PIL import Image, ImageOps
import base64
import io
import sys
from threading import Thread

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)
threads = []

#multi-threads with return value
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, timeout=3):
        Thread.join(self, timeout=3)
        return self._return

class thread_with_trace(ThreadWithReturnValue):
    def __init__(self, *args, **keywords):
        ThreadWithReturnValue.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        ThreadWithReturnValue.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True
########################################################################
#preload Model
#preload를 하기 위해서 모델 10개를 --name을 이용하여 모두 preloadModel 을 만들어줘야한다. 
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
Miya_model = loadModel('Miyazaki_pretrained')
PP_model = loadModel('PP_pretrained')
RC_model = loadModel('RC_pretrained')
SC_model = loadModel('SC_pretrained')
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
        global threads
        print(len(threads),"fileUpload")
        if len(threads) > 3:
            return Response("error : Too many requests", status=429)
        try:
            f = request.files['file']
            #사용자끼리의 업로드한 이미지가 겹치지 않게끔 uuid를 이용하여 사용자를 구분하는 디렉터리를 만든다.
            randomDirName = str(uuid.uuid4()) 
            path = "/ganilla/upload/" + randomDirName
            target = {
                "as" : {
                    "path" : path,
                    "run" : runModel,
                    "args":{
                        "pretrain_model" : "AS_pretrained",
                        "model" : AS_model,
                        "user_id" : randomDirName
                    }
                },
                "dm" : {
                    "path" : path,
                    "run" : runModel,
                    "args" : {
                        "pretrain_model" : "DM_pretrained",
                        "model" : DM_model,
                        "user_id" : randomDirName
                    }
                },
                "kh" : {
                    "path" : path,
                    "run" : runModel,
                    "args" : {
                        "pretrain_model" : "KH_pretrained",
                        "model" : KH_model,
                        "user_id" : randomDirName
                    }
                },
                "kp" : {
                    "path" : path,
                    "run": runModel,
                    "args" : {
                        "pretrain_model" : "KP_pretrained",
                        "model" : KP_model,
                        "user_id" : randomDirName
                    }
                },
                "pp" : {
                    "path" : path,
                    "run" : runModel,
                    "args" :{
                        "pretrain_model" : "PP_pretrained",
                        "model" : PP_model,
                        "user_id" : randomDirName
                    }
                },
                "rc" : {
                    "path" : path,
                    "run" : runModel,
                    "args" : {
                        "pretrain_model" : "RC_pretrained",
                        "model" : RC_model,
                        "user_id" : randomDirName
                    }
                },
                "sc" : {
                    "path" : path,
                    "run" : runModel,
                    "args" : {
                        "pretrain_model" : "SC_pretrained",
                        "model" : SC_model,
                        "user_id" : randomDirName
                    }
                },
                "tr" : {
                    "path" : path,
                    "run" : runModel,
                    "args" : {
                        "pretrain_model" : "TR_pretrained",
                        "model" : TR_model,
                        "user_id" : randomDirName
                    }
                },
                "mi" : {
                    "path" : path,
                    "run": runModel,
                    "args" : {
                        "pretrain_model" : "Miyazaki_pretrained",
                        "model" : Miya_model,
                        "user_id" : randomDirName
                    }
                }
            }    
            os.mkdir(target[check_value]["path"])
            f.save(target[check_value]["path"] + '/' + secure_filename(f.filename))
            arg = list(target[check_value]["args"].values())

            return target[check_value]["run"](arg[0],arg[1],arg[2])
        except Exception as e:
            print(e)
            return Response("error! you have to choose your illustrator please try again!", status=400)
#사용자의 입력을 받아서 각 원하는 결과물을 라우팅
def runModel(pretrain_model, model, user_id):
    data_root = 'upload/' + user_id
    result_dir = './static/img/' + user_id
    try:
        #multi-threading
        t1 = thread_with_trace(target=run, args=(data_root,pretrain_model,result_dir,model))
        t1.user_id = user_id
        threads.append(t1)
        while threads[0].user_id!=user_id:
            print(str(user_id)+": ", threads[0].user_id)
            if threads[0].is_alive():
                threads[0].join()
        threads[0].start()

        img_list = threads[0].join(timeout=3)
        if threads[0].is_alive():
            threads[0].kill()
            threads.pop(0)
            raise Exception("error model does not work! please try again 30 seconds later")
        threads.pop(0)
        
        #img_list = run(data_root, pretrain_model, result_dir, model)
        result_list = image_dump_to_memory(img_list, user_id)
        remove(user_id)
        return render_template('showImage.html', rawimg=result_list)
    except Exception as e:
        print(e)
        return Response("error! please try again", status=400)

def image_dump_to_memory(img_list, user_id):
    path = '/ganilla/static/img/' + user_id + '/images/'
    img_list[0] = path + img_list[0]
    img_list[1] = path + img_list[1]
    byte_image_list = [] #byte_image를 담기위한 list
    tmp_list = [] #byte_image를 담기전에 decode 하기 위한 list
    #imgFIle은 np.array형태여야 fromarray에 담길수 있음
    #img_io는 각 파일마다 byte 객체를 적용해줘야하므로 for문 안에서 같이 반복을 돌아야 함
    #b64encode로 encode 해준다.
    try:
        for image in img_list:
            imgFile = PIL.Image.fromarray(np.array(PIL.Image.open(image).convert("RGB")))
            img_io = io.BytesIO()
            imgFile.save(img_io, 'jpeg', quality = 100)
            img_io.seek(0)
            img = base64.b64encode(img_io.getvalue())
            tmp_list.append(img)

        #decode 작업은 여기서 해준다.
        for i in tmp_list:
            byte_image_list.append(i.decode('ascii'))

        return byte_image_list
    except Exception as e:
        print(e)
        return Response("Cannot load img_list please try again", status=400)

def remove(user_key):
    #input_dir = '/ganilla/upload/<user_id>
    #output_dir = '/ganilla/static/img/<user_id>
    remove_input_dir = '/ganilla/upload/' + user_key 
    remove_output_dir = '/ganilla/static/img/' +user_key
    print("Now start to remove file")
    print("user key is " + user_key)
    print("Input path " + remove_input_dir)
    print("Output path " + remove_output_dir)

    #output path를 삭제하는 try 문
    try:
        if os.path.isdir(remove_output_dir):
            shutil.rmtree(remove_output_dir)
            print("Delete " + remove_output_dir + " is completed")
    except Exception as e:
        print(e)
        print("Delete" + remove_output_dir + " is failed")
    #input path를 삭제하는 try 문
    try:
        if os.path.isdir(remove_input_dir):
            shutil.rmtree(remove_input_dir)
            print("Delete" + remove_input_dir + " is completed")
    except Exception as e:
        print("Delete" + remove_input_dir + " is failed")
    
    return print("All of delete process is completed!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)