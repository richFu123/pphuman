#!/bin/bash
BASE_PATH=$(cd `dirname $0`; pwd)
while true
do
    python ${BASE_PATH}/main.py
    sleep 1
done