# -*- conding:utf-8 -*-

__author__ = 'lijingang'

import os
import threading

from libs.log.logger import LoggerFactory


class TaskIpspider(object):
    # IP信息
    spider_name = ''

    def __init__(self, spider_name):
        self.spider_name = spider_name

    # 处理任务
    def do_process(self):
        # 日志组件
        logger = LoggerFactory.get_logger(threading.currentThread().name)

        try:
            os.chdir(os.path.dirname(os.path.dirname(__file__)))
            os.system('scrapy crawl %s' % self.spider_name)
        except Exception as ex:
            logger.exception(ex)
        finally:
            pass


if __name__ == '__main__':
    task = TaskIpspider('txt_spider')
    task.do_process()

    task = TaskIpspider('nimadaili_spider')
    task.do_process()

    # task = TaskIpspider('data5u_spider')
    # task.do_process()
    # task = TaskIpspider('xicidaili_spider')
    # task.do_process()
    #
    # task = TaskIpspider('ip3366_spider')
    # task.do_process()
    # task = TaskIpspider('feiyiproxy_spider')
    # task.do_process()
    # task = TaskIpspider('cnproxy_spider')
    # task.do_process()


