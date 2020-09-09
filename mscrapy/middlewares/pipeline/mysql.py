# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

import logging

from dbs.db import DB


class MysqlPipeline(object):
    name = None

    def __init__(self, name=None):
        if name is not None:
            self.name = name
        # DB组件
        self.DB = DB()

    def open_spider(self, spider):
        self.DB.connect()

    def close_spider(self, spider):
        self.DB.close()

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {'pipeline': self})

