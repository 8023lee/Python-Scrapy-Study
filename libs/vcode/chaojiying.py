# coding:utf-8

import json
import requests
import threading
from hashlib import md5

import libs.config as conf
from libs.log.logger import LoggerFactory

class ChaojiyingClient(object):

    def __init__(self, username, password, soft_id):
        # 日志组件
        self.logger = LoggerFactory.get_logger(threading.currentThread().name)

        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        result = json.loads('{"err_no": -100, "err_str": "", "pic_id": ""}')
        try:
            params = {
                'codetype': codetype,
            }
            params.update(self.base_params)
            files = {'userfile': ('ccc.jpg', im)}
            resp = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
            if resp.status_code == 200:
                result = resp.json()
            else:
                raise Exception(resp.reason)
        except Exception as ex:
            result['err_str'] = str(ex)

        return result

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        result = json.loads('{"err_no": -100, "err_str": ""}')
        try:
            params = {
                'id': im_id,
            }
            params.update(self.base_params)
            resp = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
            if resp.status_code == 200:
                result = resp.json()
            else:
                raise Exception(resp.reason)
        except Exception as ex:
            result['err_str'] = str(ex)

        self.logger.info('超级鹰打码，ReportError -- 结果：%s' % result)
        return result

    def digital_check(self, im):
        """
        im: 图片二进制流
        return: 验证码
        """
        if conf.env.IS_CJY_DEBUG:
            result = json.loads('{"err_no": 0, "err_str": "OK", "pic_id": "8059411152153000019", "pic_str": "57rvv", "md5": "cd5bf2bbab7126b3d42ca6eb91452325"}')
        else:
            # im = open(img_path, 'rb').read()
            result = self.PostPic(im, 1902)
        
        if result['err_no'] != 0 and result['pic_id'] != '':
            self.ReportError(result['pic_id'])

        self.logger.info('超级鹰打码，digital_check -- 结果：%s' % result)
        return result

    def axes_check(self, im):
        """
        im: 图片二进制流
        return: 验证码
        """

        if conf.env.IS_CJY_DEBUG:
            result = json.loads('{"err_no": 0, "err_str": "OK", "pic_id": "8060115082153000075", "pic_str": "67,238|188,275|163,174|58,308", "md5": "4c5b8d0ec0936cb18f72c4875b727e8e"}')
        else:
            # im = open(img_path, 'rb').read()
            result = self.PostPic(im, 9004)

        if result['err_no'] != 0 and result['pic_id'] != '':
            self.ReportError(result['pic_id'])

        self.logger.info('超级鹰打码，axes_check -- 结果：%s' % result)
        return result

if __name__ == '__main__':
    username = conf.env.CJY_USER
    password = conf.env.CJY_PASS
    soft_id = conf.env.CJY_SOFTID

    chaojiying = ChaojiyingClient(username, password, soft_id)	#用户中心>>软件ID 生成一个替换 96001

    chaojiying.ReportError('6060214042153000078')

    # im = open(conf.env.ROOT_DIR + '/data/logs/sina-vcode.png', 'rb').read()   #本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
    # im = open(conf.env.ROOT_DIR + '/data/logs/jianshu-vcode.png', 'rb').read()
    # result = chaojiying.axes_check(im)  #1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
    # print(type(result))
    # print(result)