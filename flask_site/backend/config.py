# -*- coding: utf-8 -*-

"""
"""

from libs.config import env


class Config:
    """base config"""
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

    # 设置mysql+pymysql的连接
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(env.DB_USER,env.DB_PASS,env.DB_HOST,env.DB_PORT,env.DB_NAME)
    # 关闭数据追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 开启提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 打印SQL语句
    SQLALCHEMY_ECHO = False


class ProdConfig(Config):
    """运行环境配置"""
    ENV = 'production'


class DevConfig(Config):
    """开发环境配置"""
    ENV = 'development'
    DEBUG = True
    # 打印SQL语句
    SQLALCHEMY_ECHO = True


config = {
    'dev': DevConfig,
    'prod': ProdConfig
}