import base64
import json
import logging
import os
import sys
import time

import paddle
import numpy as np
#运行环境切换到调用工程目录
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
PRO_PATH = os.path.join(ROOT_DIR,"PaddleDetection")
ENV_PATH = os.path.join(PRO_PATH,"deploy/pipeline")
WEIGHTS_PATH = os.path.join(ROOT_DIR,"weights/paddle/infer_weights")
sys.path.append(ENV_PATH)
from PaddleDetection.deploy.pipeline.pipeline import argsparser,merge_cfg,print_arguments,Pipeline

#obj Numpy => json数据转换
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

# rtsp://admin:admin@172.22.7.6:8554/live0.264
rtsp = ["rtsp://172.22.7.17:554/av0_0","rtsp://admin:admin@172.22.7.6:8554/live0.264"]
video_dir = os.path.join(PRO_PATH,'demo/rtsp_videos')
def init_pphuman():
    """初始化人类属性识别

    Returns:
        _type_: 人类属性识别对象
    """
    paddle.enable_static()

    # parse params from command
    parser = argsparser()
    # python deploy/pipeline/pipeline.py --config deploy/pipeline/config/infer_cfg_pphuman.yml --image_file=./deploy/pipeline/docs/images/pphumanplate.jpg --device=gpu
    # python deploy/pipeline/pipeline.py --config deploy/pipeline/config/infer_cfg_pphuman.yml -o MOT.enable=True REID.enable=True --video_dir=demo/rtsp_videos --device=gpu --run_mode paddle


    # python deploy/pipeline/pipeline.py --config deploy/pipeline/config/infer_cfg_pphuman.yml --video_dir=demo/rtsp_videos --device=gpu
    # 输入初始化参数
    FLAGS = parser.parse_args([
                            #测试结果输出到指定目录
                            '--output_dir','./out',
                            # 检测属性
                            "-o",f"MOT.enable=True",f"REID.enable=True",f"ATTR.enable=True",
                            #配置文件路径
                            '--config',os.path.join(PRO_PATH,'deploy/pipeline/config/infer_cfg_pphuman.yml'),
                            # 测试图片/视频路径
                            # '--video_dir',video_dir,
                            # '--rtsp',rtsp,
                            "--image_file","PaddleDetection/demo/hrnet_demo.jpg",
                            # #default:CPU,Choose the device you want to run, it can be: CPU/GPU/XPU, default is CPU.
                            '--device',"GPU"
                            # #default:paddle,mode of running(paddle/trt_fp32/trt_fp16/trt_int8)
                            '--run_mode',"paddle"
                            ])
    FLAGS.device = FLAGS.device.upper()
    cfg = merge_cfg(FLAGS)  # use command params to update config
    print_arguments(cfg)
    pipeline = Pipeline(FLAGS, cfg)
    return pipeline
def create_multi_threads(pipeline):
    import threading
    threads = []
    #基于多线程的方式对多路视频或视频文件并行处理
    for idx, (predictor,input) in enumerate(zip(pipeline.predictor, pipeline.input)):
        thread = threading.Thread(
                name=str(idx).zfill(3),
                target=predictor.run,
                args=(input, idx))
        threads.append(thread)

    for thread in threads:
        thread.start()
    return threads
def get_multi_res(pipeline):
    # 获取视频跟踪reid特征
    multi_res = []
    for predictor in pipeline.predictor:
        #获取视频跟踪的reid特征数据
        collector_data = predictor.get_result()
        multi_res.append(collector_data)
    return multi_res


def exec_pphuman(pipeline,input = None,output = None):
    """人类属性识别

    Args:
        pipeline (_type_): 人类属性识别对象
        input (_type_, optional): 输入路径. Defaults to None.
        output (_type_, optional): 输出目录. Defaults to None.

    Returns:
        _type_: _description_
    """
    if input:
        #输入路径['']
        pipeline.input = input
    if output:
        #修改测试结果输出目录
        pipeline.predictor.output_dir = output
    # 执行人类检测识别
    pipeline.run()
    #返回结果
    return pipeline.predictor.pipeline_res.res_dict


def result_pphuman(out_path,res_dict,isprit=False):
    """人类属性识别返回结果解析

    Args:
        out_path (_type_): 输出图片路径
        res_dict (_type_): 识别结果，返回结构化结果
        isprit (bool, optional): 特殊格式. Defaults to False.

    Returns:
        _type_: _description_
    """
    out_dict = {}
    logging.warning(out_path)
    img = None
    if os.path.exists(out_path):
        with open(out_path,"rb") as f:
            img = str(base64.b64encode(f.read()),'utf-8')
    boxes = res_dict["det"]["boxes"]
    human_attrs = res_dict["attr"]["output"]
    
    rec_res = []
    num = 0
    for box,attrs in zip(boxes,human_attrs):
        score = box[1]
        x1,y1,x2,y2 = box[2:]
        if isprit:
            rec_res.append([num,",".join(attrs),float(f'{score:.3f}')])
        else:
            atrr_dict = dict(attr.split(":") for attr in attrs)
            atrr_dict["score"] = float(f'{score:.3f}')
            atrr_dict["box"]={
                "x1":float(f'{x1:.3f}'),
                "y1":float(f'{y1:.3f}'),
                "x2":float(f'{x2:.3f}'),
                "y2":float(f'{y2:.3f}'),
                }
            rec_res.append(atrr_dict)
        num = num + 1
    out_dict["dets"] = rec_res
    logging.warning(out_dict)
    out_dict["image"] = img
    return out_dict

def main():
    pphuman = init_pphuman()
    t1 = time.time()
    res_dict = exec_pphuman(pipeline=pphuman,output="123")
    elapse = time.time() - t1
    logging.warning(res_dict)
    logging.warning(f'total_elapse: {elapse:.4f}')


if __name__ == '__main__':
    main()