# -*- coding: utf-8 -*-

__author__ = 'lijingang'

import threading

from dbs.db import DB
from libs.log.logger import LoggerFactory


class BaseModel(object):
    def __init__(self):
        # DB组件
        self.DB = DB()
        # 日志组件
        self.logger = LoggerFactory.get_logger(threading.currentThread().name)
