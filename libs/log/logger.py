# -*- coding: utf-8 -*-

"""日志模块，管理全局logger

    示例
    ------------
    >>> from libs.log.logger import LoggerFactory
    >>> logger = LoggerFactory.get_logger('sinalog')
    >>> logger.info("logger inof output")
"""

__author__ = 'lijingang'

import datetime
import os
import logging
import logging.handlers

import libs.config as conf

class LoggerFactory(object):
    # 存储所有logger
    __loggers = {}

    def __init__(self):
        pass

    @staticmethod
    def loggers():
        return LoggerFactory.__loggers

    # 配置logger
    @staticmethod
    def __logger_config(logger_name):
        logger = LoggerFactory.__loggers[logger_name]

        # create logger with "spam_application"        
        logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        filehandler = logging.handlers.TimedRotatingFileHandler(os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data/logs/" + logger_name + ".log", "D")
        filehandler.suffix = "%Y-%m-%d"
        filehandler.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter_01 = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        filehandler.setFormatter(formatter_01)

        # add the handlers to the logger
        logger.addHandler(filehandler)

        if conf.env.IS_DEBUG == True:
            # create console handler with a higher log level
            consoleHandler = logging.StreamHandler()
            consoleHandler.setLevel(logging.DEBUG)
            # create formatter and add it to the handlers
            formatter_02 = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            consoleHandler.setFormatter(formatter_02)

            # add the handlers to the logger
            logger.addHandler(consoleHandler)
    
    @staticmethod
    def get_logger(logger_name = None):
        """
        通过 logger_name 获取日志组件，如果没有就新创建一个

        同一 logname 只创建一个logger实例，通过 __loggers 全局存储所有logger，实现单例模式
        如果 logger_name 没有指定，返回 root logger
        """
        
        if not logger_name:
            logger_name = 'posttask-logger'
        
        logger_name = str(logger_name)

        logger_name_today = '%s-%s' % (logger_name, datetime.date.today().strftime("%Y%m%d"))
        if not logger_name_today in LoggerFactory.__loggers.keys():
            LoggerFactory.__loggers[logger_name_today] = logging.getLogger(logger_name_today)
            LoggerFactory.__logger_config(logger_name_today)

            # 删除前一天日志对象
            logger_name_prev = '%s-%s' % (logger_name, (datetime.date.today() + datetime.timedelta(days = -1)).strftime("%Y%m%d"))
            if logger_name_prev in LoggerFactory.__loggers.keys():
                LoggerFactory.__loggers.pop(logger_name_prev)
        
        return LoggerFactory.__loggers[logger_name_today]

    
if __name__ == '__main__':
    logger = LoggerFactory.get_logger()
    logger.info("begin to run")

    try:
        print(1/0)
    except Exception as ex:
        logger.exception(ex)
    

