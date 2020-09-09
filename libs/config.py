# -*- coding: utf-8 -*-
"""全局配置信息"""

__author__ = 'lijingang'

import os
import operator

from configparser import ConfigParser

class EnvOld(object):
    # 存储全局配置信息
    dict = {}

    def __init__(self):
        pass

    @staticmethod
    def set_value(key, value):
        """ 定义一个全局变量 """
        Env.dict[key] = value

    @staticmethod
    def get_value(key, def_value = None):
        """ 获得一个全局变量，不存在则返回默认值 """
        try:
            return Env.dict[key]
        except KeyError:
            return def_value

class Env(object):
    def __init__(self, *args, **kwargs):
        propertys = self.__dict__

        # 读取配置文件
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cp = ConfigParser()
        cp.read(root_dir + "/config.ini")

        # 程序目录
        propertys['ROOT_DIR'] = root_dir

        # 解析配置文件
        sections = cp.sections()
        for section in sections:
            for opt in cp.options(section):
                if operator.eq(opt.upper()[0:3], 'IS_'):
                    propertys[opt.upper()] = cp.getboolean(section, opt)
                else:
                    propertys[opt.upper()] = cp.get(section, opt)

        return super().__init__(*args, **kwargs)

# 解析配置文件
env = Env()

# 方案二
# # 读取配置文件
# root_dir = os.path.abspath('.')
# cp = ConfigParser()
# cp.read(root_dir + "/config.ini")

# # 程序目录
# ROOT_DIR = root_dir

# # 解析配置文件
# sections = cp.sections()
# for section in sections:
#     for opt in cp.options(section):
#         # print(opt)
#         if operator.eq(opt.upper()[0:3], 'IS_'):
#             exec("{} = {}".format(opt.upper(), cp.getboolean(section, opt)))
#         else:
#             exec("{} = '{}'".format(opt.upper(), cp.get(section, opt)))

# 方案一
# # 读取配置文件
# root_dir = os.path.abspath('.')
# cp = ConfigParser()
# cp.read(root_dir + "/config.ini")

# # 程序目录
# ROOT_DIR = 'ROOT_DIR'
# Env.set_value(ROOT_DIR, root_dir)

# # 默认打开调试
# IS_DEBUG = 'IS_DEBUG'
# Env.set_value(IS_DEBUG, cp.getboolean('env', "IS_DEBUG"))

# # 数据库配置
# DB_HOST = 'DB_HOST'
# DB_USER = 'DB_USER'
# DB_PASS = 'DB_PASS'
# DB_NAME = 'DB_NAME'
# DB_PORT = 'DB_PORT'
# Env.set_value(DB_HOST, cp.get('db', "DB_HOST"))
# Env.set_value(DB_USER, cp.get('db', "DB_USER"))
# Env.set_value(DB_PASS, cp.get('db', "DB_PASS"))
# Env.set_value(DB_NAME, cp.get('db', "DB_NAME"))
# Env.set_value(DB_PORT, cp.getint('db', "DB_PORT"))

# # 超级鹰配置
# CJY_USER = 'DB_PASS'
# CJY_PASS = 'DB_NAME'
# CJY_SOFTID = 'DB_PORT'
# Env.set_value(CJY_USER, cp.get('chaojiying', "CJY_USER"))
# Env.set_value(CJY_PASS, cp.get('chaojiying', "CJY_PASS"))
# Env.set_value(CJY_SOFTID, cp.get('chaojiying', "CJY_SOFTID"))

if __name__ == '__main__':
    root_dir = os.path.abspath('.')
    cp = ConfigParser()
    cp.read(root_dir + "/config.ini")

    #得到所有的section，以列表的形式返回
    section = cp.sections()
    print(section)

    #得到该section的所有option
    print(cp.options('db'))

    #得到该section的所有键值对
    print(cp.items('db'))

    #得到该section中的option的值，返回为string类型
    print(cp.get('db', "DB_HOST"))

    #得到该section中的option的值，返回为int类型
    print(cp.getint('db', "DB_PORT"))

    print(cp.getboolean('env', "IS_DEBUG"))