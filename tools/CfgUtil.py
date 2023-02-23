# encoding: utf-8
import logging
import os
import time
import uuid
from datetime import datetime as dt
try:
    # Python3
    from configparser import ConfigParser
except ImportError:
    # Python2
    from ConfigParser import ConfigParser

__path = os.path.dirname(os.path.abspath(__file__))
__conf_file = __path + os.path.sep + ".." + os.path.sep + "conf.ini"
__cgf_section = "config"
__db_section = "db"
PROJECT_DIR=os.path.abspath(__conf_file)
conf = ConfigParser()
conf.read(__conf_file, encoding='utf-8')


def get_options(name):
    options = {}
    try:
        options = dict(conf.items(name))
    except Exception as e:
        logging.error(e)
    return options


def get_cfg(name):
    val = conf.get(__cgf_section, name)
    return val


def get_db(name):
    val = conf.get(__db_section, name)
    return val


def db_read_config(db_var, _db_section, _db_label):
    db_options = get_options(_db_section)
    for attr in dir(db_var):
        if "__" not in attr:
            k = "%s_%s" % (_db_label, attr)
            if k in db_options:
                v = db_options[k]
                setattr(db_var, attr, v)


def print_attr(db_var):
    for attr in dir(db_var):
        if "__" not in attr:
            logging.warning("%s:%s" % (attr, getattr(db_var, attr)))


# ;ERROR = 40,WARNING = 30,WARN = WARNING,INFO = 20,DEBUG = 10,NOTSET = 0
def get_logging_level():
    try:
        level = get_cfg("logging_level")
        if level == "INFO":
            return logging.INFO
        elif level == "DEBUG":
            return logging.DEBUG
        elif level == "WARNING":
            return logging.WARNING
        elif level == "ERROR":
            return logging.ERROR
    except Exception as e:
        logging.warning(e)
    return logging.DEBUG


def get_mac_address():
    try:
        return get_cfg("mac")
    except Exception as e:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return "".join([mac[e:e + 2] for e in range(0, 11, 2)]).upper()


def get_version():
    try:
        version = get_cfg("version")
        if version == "pro":
            return True
    except Exception as e:
        logging.warning(e)
    return False


def get_server_url(name):
    try:
        server_option = get_options("server")
        server_url = server_option.get("server_url")
        url = server_option.get(name)
        return "%s/%s" % ((server_url[:-1] if str(server_url).endswith("/") else server_url),
                          url)
    except Exception as e:
        logging.warning(e)
    return None


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DBS_DIR = BASE_DIR
LOG_DIR = os.path.join(BASE_DIR, "data/logs/")
ramdisk_dir = "data/ramdisk/"
RAMDISK_DIR = os.path.join(BASE_DIR, "data/ramdisk/")
for DIR in [LOG_DIR, RAMDISK_DIR]:
    if not os.path.exists(DIR):
        os.makedirs(DIR)
PROJECT_NAME = get_cfg("project")
VERSION = get_version()
MAC = get_mac_address()
LOGGING_LEVEL = get_logging_level()

F_TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_url(filepath):
    base_dir = BASE_DIR if BASE_DIR.endswith("/") else BASE_DIR + "/"
    url = filepath.replace(base_dir, "")
    return url

def get_url_time(filepath):
    base_dir = RAMDISK_DIR if RAMDISK_DIR.endswith("/") else RAMDISK_DIR + "/"
    timedirname = filepath.replace(base_dir, "")
    return dt.strptime(timedirname, "%Y/%m/%d/%H%M%S")

def get_ramdisk_dir(isRandom=False,dt = time.time()):
    timestr="%s000"%(time.strftime("%Y/%m/%d/%H%M", time.localtime(dt)))
    output_dir = os.path.join(RAMDISK_DIR,timestr)
    if isRandom:
        mills = str(int(time.time()*10000000))[8:]
        output_dir = os.path.join(output_dir,mills)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir
