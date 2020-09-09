# -*- coding: utf-8 -*-

"""
性能分析模块
"""

__author__ = 'lijingang'

import time
import threading

from libs.log.logger import LoggerFactory


class Profile(object):
    __tokens = {}

    @staticmethod
    def __set_begintime():
        # thread_id = threading.currentThread().ident
        thread_id = threading.currentThread().name
        if thread_id not in Profile.__tokens.keys():
            Profile.__tokens[thread_id] = []
        Profile.__tokens[thread_id].append(time.time())

    @staticmethod
    def __get_duration():
        duration = 0
        
        # thread_id =  threading.currentThread().ident
        thread_id = threading.currentThread().name
        if thread_id not in Profile.__tokens.keys() or not Profile.__tokens[thread_id]:
            raise Exception('Profile begintime not found')
        else:
            duration = time.time() - Profile.__tokens[thread_id].pop()

        return duration

    @staticmethod
    def __get_logger():
        return LoggerFactory.get_logger(threading.currentThread().name)

    @staticmethod
    def begin(token):
        """
        标记用于分析的代码块的开始

        必须与对具有相同类别名称的[[end]]的调用相匹配。
        开始和结束调用也必须正确嵌套。例如,

        >>> Profile.begin('block1')
        >>> # some code to be profiled
        >>> Profile.begin('block2')
        >>> # some other code to be profiled
        >>> Profile.end('block2')
        >>> Profile.end('block1')
        """
        Profile.__set_begintime()
        Profile.__get_logger().info(token + '，' + time.strftime('%Y-%m-%d %H:%M:%S'))

    @staticmethod
    def end(token):
        """
        标记用于分析的代码块的结束

        必须与之前调用具有相同类别名称的[[begin]]相匹配
        """
        Profile.__get_logger().info(token + '，' + time.strftime('%Y-%m-%d %H:%M:%S') + '，耗时：' + str(Profile.__get_duration()))


if __name__ == '__main__':
    threading.currentThread().name = 'profile'
    logger = LoggerFactory.get_logger(threading.currentThread().name)
    logger.info("begin to run")

    Profile.begin('test1 -- begin -- ')

    try:
        time.sleep(1)
        print(1/0)
    except Exception as ex:
        logger.exception(ex)

    Profile.end('test1 -- end -- ')

