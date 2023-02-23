# -*- encoding: utf-8 -*-
# @Author: fy
# @Contact: yu.fu@deepcam.com
import os
import base64
import json
import time
import logging
from wsgiref.simple_server import make_server

import cv2
import numpy as np
from flask import Flask, render_template, request


from tools import CfgUtil as cfg
from tools.Logger import Logger
from PPHuman import init_pphuman,exec_pphuman,result_pphuman
Logger.get_logger(cfg.PROJECT_NAME, level=cfg.LOGGING_LEVEL, log_dirs=cfg.LOG_DIR)
app = Flask(__name__)
# 调整接收文本大小
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/human', methods=['POST'])
def human():
    if request.method == 'POST':
        url_get = request.get_json()
        img_str = str(url_get).split(',')[1]

        image = base64.b64decode(img_str + '=' * (-len(img_str) % 4))
        nparr = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        
        
        dir_path = cfg.get_ramdisk_dir()
        in_dir = os.path.join(dir_path,"in")
        out_dir = os.path.join(dir_path,"out")
        if not os.path.exists(in_dir):
            os.makedirs(in_dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        filename = f"{int(time.time()*1000000)}.jpg"
        image_path = os.path.join(in_dir,filename)
        cv2.imwrite(image_path,image)
        t1 = time.time()
        res_dict = exec_pphuman(pipeline=pphuman,input=[image_path],output=out_dir)
        elapse = time.time() - t1
        logging.warning(res_dict)
        logging.warning(f'total_elapse: {elapse:.4f}')
        out_path = os.path.join(out_dir,filename)
        out_dict = result_pphuman(out_path,res_dict,isprit=True)
        img = out_dict["image"]
        dets = out_dict["dets"]
        

        return json.dumps({'image': img,
                           'total_elapse': f'{elapse:.4f}',
                           'elapse_part': "",
                           'rec_res': json.dumps(dets)
                           
                           })
        
@app.route('/api/v1/human/detect', methods=['POST'])
def ocr_idcard():
    if request.method == 'POST':
        try:
            #接收检测图片
            json_obj = request.get_json()
            logging.warning(json_obj)
            img_str = json_obj["image"]

            image = base64.b64decode(img_str + '=' * (-len(img_str) % 4))
            nparr = np.frombuffer(image, np.uint8)
        except Exception as e:
            logging.error(e)
            return json.dumps({"code": -1001,"msg": u"Incomplete parameters","data": {}})
        try:
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            
            
            dir_path = cfg.get_ramdisk_dir()
            #临时数据存目录
            in_dir = os.path.join(dir_path,"in")
            #临时数据保存目录
            out_dir = os.path.join(dir_path,"out")
            if not os.path.exists(in_dir):
                os.makedirs(in_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            filename = f"{int(time.time()*1000000)}.jpg"
            image_path = os.path.join(in_dir,filename)
            #保存图片数据
            cv2.imwrite(image_path,image)
            
        except Exception as e:
            logging.error(e)
            return json.dumps({"code": -1101,"msg": u"Detection failed","data": {}})
        image = None
        out_dict = {}
        try:
            t1 = time.time()
            # 3.执行检测识别
            res_dict = exec_pphuman(pipeline=pphuman,input=[image_path],output=out_dir)
            elapse = time.time() - t1
            logging.warning(res_dict)
            logging.warning(f'total_elapse: {elapse:.4f}')
            out_path = os.path.join(out_dir,filename)
            # 4.检测结果解析,格式化输出结果
            out_dict = result_pphuman(out_path,res_dict)
        except Exception as e:
            logging.error(e)
            return json.dumps({"code": -1102,"msg": u"Parsing failed","data": {}})
        logging.warning(f'out_dict:{out_dict}')
        return json.dumps({"code": 1000,"msg": "success","data": out_dict})
if __name__ == '__main__':
    # 1.初始化模型，创建人类属性识别对象
    pphuman = init_pphuman()
    # 2.对象第一次执行，可能存在第一次耗时较长的问题
    exec_pphuman(pipeline=pphuman)
    ip = '0.0.0.0'
    ip_port = 9991
    logging.warning(f"http://{ip}:{ip_port}")
    server = make_server(ip, ip_port, app)
    server.serve_forever()
