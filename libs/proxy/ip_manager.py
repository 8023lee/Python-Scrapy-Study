# -*- coding: utf-8 -*-
"""代理IP管理工具类"""

__author__ = 'lijingang'

import time
import datetime
import sys
import requests
import threading
import json
import random

from libs.log.logger import LoggerFactory
from dbs.model.proxy_ip import ProxyIp as ProxyIpModel

# 日志组件
logger = LoggerFactory.get_logger('IpManager')


class IpManager(object):
    # 代理IP获取服务URL
    server_url = {
        'one': 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=4&mr=2&regions='
    }

    # 存储全局代理IP信息
    dict = {}

    def __init__(self):
        pass

    @staticmethod
    def get_ip(key):
        return_ip = None

        for i in range(0, 10):
            try:
                if key not in IpManager.dict.keys() or len(IpManager.dict[key]) == 0:
                    # except_ips = '","'.join([val[0].get('id') for key, val in IpManager.dict.items()])
                    except_ip_ids = []
                    for key1, val1 in IpManager.dict.items():
                        if val1:
                            for v in val1:
                                except_ip_ids.append(v.get('id'))

                    except_ip_ids = ','.join([str(v) for v in except_ip_ids])
                    list_ips = ProxyIpModel().get_all_enable(1, except_ip_ids)
                    IpManager.dict[key] = list_ips

                if IpManager.dict[key]:
                    proxy_ip = IpManager.dict[key][0]

                    # 再次验证IP是否可用
                    if proxy_ip:
                        # chk_resule = IpManager.check_ip(proxy_ip.get('ip'), proxy_ip.get('port'))
                        # 修改成，只验证是否支持https代理
                        chk_resule = IpManager.check_https_ip(proxy_ip.get('ip'), proxy_ip.get('port'))

                        if chk_resule.get('result'):
                            # 更新IP刷新时间
                            proxy_ip['last_checked_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            proxy_ip['speed'] = chk_resule.get('speed')

                            # 去除updateTime，更新时，自动更新当前时间
                            if 'updateTime' in proxy_ip.keys():
                                proxy_ip.pop('updateTime')

                            proxyip_model = ProxyIpModel()
                            affected_rows = proxyip_model.update(proxy_ip)

                            return_ip = proxy_ip
                            break
                        else:
                            # 更新IP响应时间为30秒，降低优先级
                            proxy_ip['last_checked_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            proxy_ip['speed'] = 30
                            proxy_ip['invalidNum'] = proxy_ip['invalidNum'] + 1
                            proxy_ip['status'] = ProxyIpModel.STATUS_UNENABLE

                            # 去除updateTime，更新时，自动更新当前时间
                            if 'updateTime' in proxy_ip.keys():
                                proxy_ip.pop('updateTime')

                            proxyip_model = ProxyIpModel()
                            affected_rows = proxyip_model.update(proxy_ip)

                            IpManager.dict[key].pop(0)
            except Exception as ex:
                logger.exception(ex)

        return return_ip

    @staticmethod
    def clear_ip(key):
        try:
            if key in IpManager.dict.keys():
                proxy_ip = IpManager.dict[key][0]
                IpManager.dict[key].clear()

                if proxy_ip:
                    # 更新为不可用状态
                    proxy_ip['last_checked_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    proxy_ip['speed'] = 30
                    proxy_ip['invalidNum'] = proxy_ip['invalidNum'] + 1
                    proxy_ip['status'] = ProxyIpModel.STATUS_UNENABLE

                    # 去除updateTime，更新时，自动更新当前时间
                    if 'updateTime' in proxy_ip.keys():
                        proxy_ip.pop('updateTime')
                    proxyip_model = ProxyIpModel()
                    affected_rows = proxyip_model.update(proxy_ip)
        except Exception as ex:
            logger.exception(ex)

    @staticmethod
    def get_using_ip():
        dict_ips = {}
        for key, val in IpManager.dict.items():
            dict_ips[key] = ['%s-%s' % (v.get('ip'), v.get('web_site')) for v in val]

        return dict_ips

    @staticmethod
    def get_ip_old(key):
        proxy_ip =  None
        try:
            if key not in IpManager.dict.keys() or len(IpManager.dict[key]) == 0:
                # rep_text = requests.get(IpManager.server_url['one']).text
                rep = '{"code":0,"success":true,"msg":"0","data":[{"ip":"182.37.75.0","port":6856,"expire_time":"2019-01-29 19:04:54"},{"ip":"182.37.75.0","port":6856,"expire_time":"2019-01-29 19:04:54"}]}'

                rep = json.loads(rep)
                if rep['code'] == 0:
                    list_ips = rep['data']
                
                IpManager.dict[key] = list_ips
                IpManager.dict[key] = []
            proxy_ip = IpManager.dict[key].pop()
        except Exception as ex:
            logger.exception(ex)
            pass
        
        return proxy_ip

    @staticmethod
    def check_ip(ip, port):
        result = False
        speed = 0

        url = 'http://httpbin.org/get'
        headers = IpManager.get_headers()  # 定制请求头
        proxy = {
            'http': 'http://%s:%s' % (ip, port),
            'https': 'https://%s:%s' % (ip, port)
        }
        try:
            begin_time = time.time()
            response = requests.get(url, proxies=proxy, headers=headers, timeout=5)
            content = response.content.decode('utf-8')
            # print(content)
            content = json.loads(content)
            origin_ip = content.get('origin')
            origin_ip_list = origin_ip.split(',')
            if ip in origin_ip_list:
                result = True
                end_time = time.time()
                speed = round(end_time - begin_time, 4)
        except requests.exceptions.ConnectionError as ex:
            logger.info(str(ex))
        except requests.exceptions.ReadTimeout as ex:
            logger.info(str(ex))
        except Exception as ex:
            logger.info(str(ex))

        return {'result': result, 'speed': speed}

    @staticmethod
    def check_https_ip(ip, port):
        result = False
        speed = 0

        url="https://www.baidu.com"
        # url = 'https://www.taobao.com/tbhome/page/market-list'
        # url = https://img.alicdn.com/tps/i3/T1OjaVFl4dXXa.JOZB-114-114.png
        headers = IpManager.get_headers()  # 定制请求头
        proxy = {
            # 'http': 'http://%s:%s' % (ip, port),
            'https': 'https://%s:%s' % (ip, port)
        }
        try:
            begin_time = time.time()
            response = requests.get(url, proxies=proxy, headers=headers, timeout=5)
            if response.status_code == 200:
                # content = response.content.decode('utf-8')
                # print(content)
                # content = json.loads(content)
                # origin_ip = content.get('origin')
                # origin_ip_list = origin_ip.split(',')
                # if ip in origin_ip_list:
                result = True

            else:
                result = False

            end_time = time.time()
            speed = round(end_time - begin_time, 4)
        except requests.exceptions.ConnectionError as ex:
            logger.info(str(ex))
        except requests.exceptions.ReadTimeout as ex:
            logger.info(str(ex))
        except Exception as ex:
            logger.info(str(ex))

        return {'result': result, 'speed': speed}

    @staticmethod
    def get_headers():
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}
        return headers


if __name__ == '__main__':
    print(IpManager.dict)
    # IpManager.get_ip('1111')
    # IpManager.get_ip('2222')
    # IpManager.get_ip('3333')
    # IpManager.get_ip('4444')
    # sys.exit(0)
    #
    #
    # print(IpManager._server_url)
    #
    # ip = IpManager.get_ip('aaaaa')
    # print(ip)
    # ip = IpManager.get_ip('aaaaa')
    # print(ip)
