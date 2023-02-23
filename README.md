# PP-Human人类属性的识别服务

  ## 一.功能说明

- 实现web服务，在页面上导入图片，输出人类属性
- 绘制在图片上，并显示
- 支持API接口
- 基于视频输入的属性识别，任务类型包含多目标跟踪和属性识别，具体如下：

```shell
#人形跟踪
- reid
- person

#人类属性
- pedestrian:pedestrian tracking.
- scores:
- gender:Male/Female
- age:['AgeLess18', 'Age18-60', 'AgeOver60']
- direction:['Front', 'Side', 'Back']
- glasses:Glasses
- hat:Hat
- hold obj:HoldObjects/HoldObjectsInFornt
- bag:['HandBag', 'ShoulderBag', 'Backpack']/No bag
- Upper:LongSleeve/ShortSleeve ['UpperStride', 'UpperLogo', 'UpperPlaid', 'UpperSplice']
- lower:['LowerStripe', 'LowerPattern', 'LongCoat', 'Trousers', 'Shorts','Skirt&Dress']
- shoe:No Boots/Boots
```

## 二.开发环境搭建

### 1.**运行环境搭建**

#### 下载docker

然后pull镜像文件。cuda版本向下兼容

```SQL
docker pull paddlepaddle/paddle:2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0
```

#### 创建docker

然后根据下载的镜像文件创建docker容器。

```SQL
docker  run --runtime nvidia \
    -p 9292:9292 \
    -p 9292:9292 \
    --name test \
    -shm-size=252G \
    --network=host \
    -v $PWD:/home/pphuman \
    -dit paddlepaddle/paddle:2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0 /bin/bash
```

-v $PWD:/home/pphuman:挂载工程目录

#### 验证docker

然后用docker ps看一下当前运行的docker容器

```SQL
docker ps     #查看当前运行的docker容器。
docker ps -a  #查看所有存在的docker容器。
```

结果如下：

```SQL
CONTAINER ID   IMAGE                                           COMMAND       CREATED             STATUS             PORTS     NAMES
489e9f56374b        paddlepaddle/paddle:2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0                     "/bin/bash"              41 hours ago        Up 41 hours                 22/tcp, 0.0.0.0:9292->9292/tcp      test
```

#### 进入docker

然后进入docker环境：

```SQL
docker exec -it test /bin/bash
```

### 2.安装python依赖module

#### 依赖module列表

```shell
cat >> requestsments.txt << EOF

numpy==1.21.6

tqdm
typeguard
visualdl>=2.2.0
opencv-python <= 4.6.0
PyYAML
shapely
scipy
terminaltables
Cython
pycocotools
setuptools

# for vehicleplate
pyclipper

# for mot
lap
motmetrics
sklearn==0.0
filterpy

# flask
Flask>=2.1.0

paddlepaddle==2.4.1

EOF
```

####  执行安装命令

```shell
pip install --upgrade pip -i https://pypi.douban.com/simple
pip install -r requirements.txt -i https://pypi.douban.com/simple
```
## 三.运行测试code

### 1.下载工程
```shell
cd pphuman
git clone https://github.com/PaddlePaddle/PaddleDetection.git
git checkout -b release/2.5
```
### 2.测试demo

```shell
cd PaddleDetection
# 预测单张图片文件
python deploy/pipeline/pipeline.py  --config deploy/pipeline/config/infer_cfg_pphuman.yml -o MOT.enable=True REID.enable=True ATTR.enable=True --image_file "demo/hrnet_demo.jpg" --device=gpu --run_mode paddle
```

image_file:指定测试文件


### 3.运行后台服务

```shell
cd pphuman
./etc/init.d/run.sh restart
```
服务器url:http://172.22.8.244:9991    (运行服务ip)

接口调用:http://172.22.8.244:9991/api/v1/human/detect

设置docker自启动






## 四.web支持,前后端测试
在浏览器测试 http://172.22.8.244:9991/  (运行服务ip) 网页测试

![](images\20230223071310.png)