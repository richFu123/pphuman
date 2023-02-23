#!/bin/bash

set -e
BASE_PATH=$(cd `dirname $0`/../..; pwd)
HOME_BIN=${BASE_PATH}
EXEC_NAME1="${HOME_BIN}/runserver.sh"
EXEC_NAME11="${HOME_BIN}/main.py"

function log_check() {
    fileDir=`dirname $1`
    if [ -d $fileDir ];then
        touch $1 > /dev/null 2>&1
        if [ $? -ne 0 ];then
            echo "Permission denied : $1"
            exit 1
        fi
    else
        mkdir -p $fileDir
        if [ $? -ne 0 ];then
            echo "Permission denied : $1"
            exit 1
        fi
    fi
}

function check() {
    PID=$(ps aux | grep $1 | grep -v grep | awk '{print $2}')
    if [[ "${PID[@]}" != "" ]];then
        echo "Process already exist"
        exit 1
        
    fi
}

function check_start() {
    PID=$(ps aux | grep $1 | grep -v grep | awk '{print $2}')
    if [[ "${PID[@]}" != "" ]];then
        echo "Service start successfully: $1"
    fi
}

function kill_process() {
    PID=$(ps aux | grep $1 | grep -v grep | awk '{print $2}')
    if [[ "${PID[@]}" != "" ]];then
        ps -ef | grep $1 | grep -v grep | cut -c 9-15 | xargs kill -9
        test $? -eq 0 && echo "Process has been killed: $1"
    else
        echo "Process is not running: $1"
    fi
}

function start_service() {
    check $EXEC_NAME1
    check $EXEC_NAME11
    nohup $EXEC_NAME1  >/dev/null 2>&1 &
    check_start $EXEC_NAME1
    check_start $EXEC_NAME11

}

function stop_service() {
    kill_process $EXEC_NAME1
    kill_process $EXEC_NAME11
}

if [ -d $HOME_BIN ];then
    # Make sure the program is executed in the root directory.
    cd $HOME_BIN
else
    echo "No such directory: $HOME_BIN"
    exit 1
fi

case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 1
        start_service
        ;;
    *)
        echo "Usage: /etc/init.d/`basename $0` start|stop|restart"
        ;;
esac
exit 0