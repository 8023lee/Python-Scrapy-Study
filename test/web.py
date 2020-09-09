# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'


# from flask import Flask # 导入包
#
# app = Flask(__name__) # 创建一个Web应用
#
#
# @app.route('/') # 定义路由(Views)，可以理解为定义页面的URL
# def index():
#     return "这是用Python + Flask 搞出来的。" # 渲染页面
#
#
# if __name__ == "__main__":
#     app.run(host='127.0.0.1',port=8080) # 运行，指定监听地址为 127.0.0.1:8080
#

from sqlalchemy import create_engine

from libs.config import env

HOST = env.DB_HOST
USERNAME = env.DB_USER
PASSWORD = env.DB_PASS
DATABASE = env.DB_NAME
PORT = env.DB_PORT
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USERNAME,PASSWORD,HOST,PORT,DATABASE)


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])

    engine = create_engine(DB_URI)

    with engine.connect() as db:
        data = db.execute('select * from m_platform_account where 1=1  and platformSn="newsmth"')

        print(data)
    return [b'<h1>Hello, web!</h1>']


from wsgiref.simple_server import make_server

httpd = make_server('', 8000, application)
print("Serving HTTP on port 8000...")
httpd.serve_forever()