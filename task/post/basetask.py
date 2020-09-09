# -*- conding:utf-8 -*-

"""任务模块基类"""

__author__ = 'lijingang'

import datetime
import threading

from libs.proxy.ip_manager import IpManager
import libs.postsdk.sinasdk as SinaSDK
import libs.postsdk.hexunsdk as HeXunSDK
import libs.postsdk.csdnsdk as CsdnSDK
import libs.postsdk.newsmthsdk as NewsmthSDK
import libs.postsdk.jianshusdk as JianshuSDK

class BaseTask(object):
    def __init__(self):
        pass

    def get_proxy_ip(self, key):
        """获取代理IP"""
        proxy_ip = None
        num = 0
        while True:
            proxy_ip = IpManager.get_ip(threading.currentThread().ident)
            now = datetime.datetime.now() + datetime.timedelta(minutes = 1)
            if proxy_ip is None or proxy_ip['expire_time'] < now.strftime('%Y-%m-%d %H:%M:%S'):
                num += 1
                if num > 5:
                    proxy_ip = None
                    break
                else:
                    continue
            else:
                break
        return proxy_ip
   
    def get_sdk(self, dict_article, browser):
        """发布SDK"""
        sdk = None

        paltformsn = dict_article.get('platformSn')

        if paltformsn == "jianshu":
            model = JianshuSDK.PostModel(dict_article)
            if not model.has_error:
                sdk = JianshuSDK.JianshuSDK(model, browser)
        elif paltformsn == "sinablog":
            model = SinaSDK.PostModel(dict_article)
            if not model.has_error:
                sdk = SinaSDK.SinaSDK(model, browser)
        elif paltformsn == "hexunblog":
            model = HeXunSDK.PostModel(dict_article)
            if not model.has_error:
                sdk = HeXunSDK.HexunSDK(model, browser)
        elif paltformsn == "csdn":
            model = CsdnSDK.PostModel(dict_article)
            if not model.has_error:
                sdk = CsdnSDK.CsdnSDK(model, browser)
        elif paltformsn == "newsmth":
            model = NewsmthSDK.PostModel(dict_article)
            if not model.has_error:
                sdk = NewsmthSDK.NewsmthSDK(model, browser)
        else:
            pass
        
        return sdk