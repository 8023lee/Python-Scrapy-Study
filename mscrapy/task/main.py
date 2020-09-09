# -*- conding:utf-8 -*-

import time
import threading
import importlib

from optparse import OptionParser

import libs.config as conf

from libs.log.logger import LoggerFactory
from dbs.model.proxy_ip import ProxyIp as ProxyIpModel
from mscrapy.task.task_ipcheck import TaskIpcheck
from mscrapy.task.task_ipspider import TaskIpspider

# 日志组件
logger = LoggerFactory.get_logger('ipcheck-logger')


def run_check(num_per_time=50):
    threading.currentThread().name = 'ipcheck-logger'
    while True:
        logger.info('代理IP验证开始 %s' % time.strftime('%Y-%m-%d %H:%M:%S'))

        threads = []

        # 获取账号信息
        proxy_ip_model = ProxyIpModel()
        proxy_ips = proxy_ip_model.get_all_for_check()

        # 计算分组，每组一个线程
        ip_count = len(proxy_ips) // num_per_time
        if len(proxy_ips) % num_per_time:
            ip_count += 1

        for i in range(1, ip_count + 1):
            tmp_list = proxy_ips[(i-1)*num_per_time:i*num_per_time]
            # print(tmp_list)

            task = TaskIpcheck(tmp_list)
            t = TaskThread(task)
            t.name = 'ipcheck-logger'
            t.start()

            logger.info('start ipcheck thread %s' % i)

            threads.append(t)

            # 间隔 1 秒，启动下一个线程
            time.sleep(1)

        for thread in threads:
            thread.join()

        logger.info('All ipcheck thread done!!!!!')

        logger.info('代理IP验证结束 %s，休息 %s 分钟' % (time.strftime('%Y-%m-%d %H:%M:%S'), conf.env.PROXYIP_REFRESH_INTERVAL))
        time.sleep(int(conf.env.PROXYIP_REFRESH_INTERVAL) * 60)

        # 重新加载配置
        importlib.reload(conf)


def run_crawl():
    threading.currentThread().name = 'ipcrawl-logger'
    while True:
        logger_crawl = LoggerFactory.get_logger(threading.currentThread().name)
        logger_crawl.info('代理IP爬取开始 %s' % time.strftime('%Y-%m-%d %H:%M:%S'))

        spider_names = [
            # 'dink_spider',
            # 'kuaidaili_spider',
            # 'data5u_spider',
            'txt_spider',
            # 'xicidaili_spider',
            # 'ip3366_spider',
            # 'feiyiproxy_spider',
            # 'cnproxy_spider',
            'nimadaili_spider'
        ]

        for spider_name in spider_names:
            task = TaskIpspider(spider_name)
            task.do_process()

        logger_crawl.info('代理IP爬取结束 %s，休息 %s 分钟' % (time.strftime('%Y-%m-%d %H:%M:%S'), conf.env.PROXYIP_CRAWL_INTERVAL))
        time.sleep(int(conf.env.PROXYIP_CRAWL_INTERVAL) * 60)

        # 重新加载配置
        importlib.reload(conf)


class TaskThread(threading.Thread):
    task = None

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        if self.task:
            self.task.do_process()
        else:
            logger.error('task is None！')


def run(do_type):
    if do_type.lower() == 'crawl':
        run_crawl()
    elif do_type.lower() == 'check':
        run_check()


if __name__ == '__main__':
    # 设置帮助参数
    usage = """Example: 'python %prog -t auto'"""
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--type", action="store", type="string", dest="doType",
                      metavar="[crawl/check]", help="Crawl or Check")
    (options, args) = parser.parse_args()

    if not options.doType:
        options.doType = 'crawl'
    elif options.doType.lower() not in ['crawl', 'check']:
        parser.error("options -t is must [crawl/check]")

    run(options.doType)
