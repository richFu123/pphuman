#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import RotatingFileHandler
class Logger:

    @classmethod
    def get_logger(cls, filename, level=logging.DEBUG, log_dirs=os.path.abspath(".")):
        """
        :param name: name of logger
        :param threshold_level: minimum level to be log
        :return: logging.Logger object
        """
        name = os.path.basename(filename).split(".")[0]
        if not os.path.exists(log_dirs):
            try:
                os.makedirs(log_dirs)
            except Exception as e:
                print("%s already is exists" % os.path.basename(log_dirs))
        # 设置日志的记录等级
        logging.basicConfig(level=level)  # 调试debug级
        # 创建日志记录的格式                  时间          日志等级      输入日志信息的文件名 行数    日志信息
        if level == logging.INFO:
            formatter_msg = '{\"timestamp\":\"%(asctime)s\",\"file\":\"%(filename)s\",\"level\":\"%(levelname)s\",\"line\":\"%(lineno)d\",\"message\":\"%(message)s\"}'
        else:
            formatter_msg = '[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d %(message)s'
        formatter = logging.Formatter(formatter_msg)

        logpath = os.path.join(log_dirs, "%s.log" % name)

        # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
        # file_log_handler = RotatingFileHandler(logpath, maxBytes=1024 * 1024 * 100, backupCount=2)
        file_log_handler = logging.handlers.TimedRotatingFileHandler(filename=logpath, when='D', interval=1, \
                                                                     backupCount=3)
        # 为刚创建的日志记录器设置日志记录格式
        file_log_handler.setFormatter(formatter)
        # 为全局的日志工具对象添加日记录器
        logger = logging.getLogger()
        logger.addHandler(file_log_handler)
        logger.setLevel = level
        logging.info("start %s process" % str(name))
        return logger