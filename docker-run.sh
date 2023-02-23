#!/bin/bash
docker pull paddlepaddle/paddle:2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0
docker stop test
docker rm test
docker  run --runtime nvidia \
    -p 9292:9292 \
    -p 9991:9991 \
    --name test \
    -v /opt/applications/AI2APPs/PP/samples/pphuman:/home/pphuman \
    -dit paddlepaddle/paddle:2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0 /bin/bash