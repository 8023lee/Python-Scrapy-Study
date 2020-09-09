# -*- conding:utf-8 -*-

__author__ = 'lijingang'

import datetime
import threading

from libs.log.logger import LoggerFactory
from libs.proxy.ip_manager import IpManager
from dbs.model.proxy_ip import ProxyIp as ProxyIpModel


class TaskIpcheck(object):
    # IP信息
    __list_ips = []

    def __init__(self, list_ips):
        self.__list_ips = list_ips

    # 处理任务
    def do_process(self):
        # 日志组件
        self.logger = LoggerFactory.get_logger(threading.currentThread().name)

        try:
            for ip in self.__list_ips:
                self.logger.info('验证IP：%s ' % (ip.get('ip')))

                # check_resutl = IpManager.check_ip(ip.get('ip'), ip.get('port'))
                # 修改成，只验证是否支持https代理
                check_resutl = IpManager.check_https_ip(ip.get('ip'), ip.get('port'))

                ip['speed'] = check_resutl.get('speed')
                ip['last_checked_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ip['status'] = ProxyIpModel.STATUS_ENABLE if check_resutl.get('result') else ProxyIpModel.STATUS_UNENABLE
                if check_resutl.get('result'):
                    ip['status'] = ProxyIpModel.STATUS_ENABLE
                    ip['invalidNum'] = 0
                else:
                    ip['status'] = ProxyIpModel.STATUS_UNENABLE
                    ip['invalidNum'] = ip['invalidNum'] + 1

                # 去除updateTime，更新时，自动更新当前时间
                if 'updateTime' in ip.keys():
                    ip.pop('updateTime')

                proxyip_model = ProxyIpModel()
                affected_rows = proxyip_model.update(ip)

                print(affected_rows)

        except Exception as ex:
            self.logger.exception(ex)
        finally:
            pass


if __name__ == '__main__':
    threading.currentThread().name = 'task-ipcheck-logger-main'
    # 日志组件
    logger = LoggerFactory.get_logger(threading.currentThread().name)

    logger.info('==== ipcheck task running start ====')

    # 获取账号信息
    proxy_ip_model = ProxyIpModel()
    proxy_ips = proxy_ip_model.get_all_for_check()
    # proxy_ips = [{'id':1, 'ip': '183.156.242.236', 'port':4217}]

    task = TaskIpcheck(proxy_ips)
    task.do_process()

    logger.info('==== ipcheck task running end ====')

