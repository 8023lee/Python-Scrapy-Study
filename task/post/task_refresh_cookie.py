# -*- conding:utf-8 -*-

"""刷新登录Cookie模块"""

__author__ = 'lijingang'

import importlib
import time
import threading
import json
from datetime import datetime
from dateutil import rrule
from optparse import OptionParser

from selenium import webdriver

import libs.config as conf
from libs.log.logger import LoggerFactory
from libs.proxy.ip_manager import IpManager
from libs.log.profile import Profile
from task.post.basetask import BaseTask
from dbs.model.account import Account as AccountModel


class TaskRefreshCookie(BaseTask):
    # 账号信息
    __list_accounts = []
    # 一个线程的账户数量
    __num_of_ip = 10

    def __init__(self, list_accouts, __num_of_ip):
        self.__list_accounts = list_accouts
        self.__num_of_ip = __num_of_ip

        super().__init__()

    # 登录(针对手动登录平台)
    def __do_login(self, acct_list, browser):
        pass

    def login_process(self):
        pass

    # 刷新Cookie
    def __do_refresh(self, acct, browser):
        login_cookie_info = None

        try:
            Profile.begin('%s，账户ID=%d，-- begin --' % (acct.get("platformName"), acct.get("id")))

            # 构建PostModel数据
            _acct = acct.copy()
            _acct['title'] = ''
            _acct['content'] = ''
            _acct['tags'] = ''
            _acct['selfCategory'] = ''
            _acct['loginCookie'] = json.loads(acct['loginCookie'])
            _acct['refUrl'] = ''
            _acct['imgUrl'] = ''
        
            # 获取SDK
            sdk = self.get_sdk(_acct, browser)
            if sdk:
                # 刷新Cookie
                login_cookie_info = sdk.refresh_login_cookie()
                # 更新数据库Cookie状态
                AccountModel().update_login_cookie(login_cookie_info['loginCookieEnable'], login_cookie_info['loginCookie'], acct.get('id'))
        except Exception as ex:
            self.logger.exception('%s，账户ID=%d，Cookie刷新，异常', acct.get("platformName"), acct.get("id"))
        finally:
            Profile.end('%s，账户ID=%d，-- end --' % (acct.get("platformName"), acct.get("id")))

        return login_cookie_info

    def refresh_process(self):
        while True:
            # 日志组件，每天都创建新的logger，保证每天一个日志文件
            self.logger = LoggerFactory.get_logger(threading.currentThread().name)

            Profile.begin('刷新账户登录状态 -- begin --')

            # 获取需要刷新登录状态的账户
            accounts = AccountModel().get_refresh_accounts()
            # 循环账户分组
            for key, accts in accounts.items():
                try:
                    # 浏览器对象
                    browser = None

                    # 带刷新账户集合
                    dict_accounts = []

                    # 循环分组里的账户，先过滤不需要刷新的账户，减少浪费代理IP
                    for acct in accts:
                        # 手动登录，Cookie失效时，不需要刷新
                        if acct.get('loginType') == AccountModel.LOGIN_TYPE_MANUAL and acct.get('loginCookieEnable') == 0:
                            self.logger.info('%s，账户ID=%d，Cookie失效，需要手动登录处理' % (acct.get("platformName"), acct.get("id")))
                            continue

                        # # 距上次刷新时间 小于15分钟的账户，不做刷新
                        prev_datetime = acct.get('loginCookieUpdateTime')
                        minutes = rrule.rrule(rrule.MINUTELY, prev_datetime, until=datetime.now())
                        if acct.get('loginCookieEnable') and minutes.count() < int(conf.env.COOKIE_REFRESH_INTERVAL):
                            self.logger.info('%s，账户ID=%d，Cookie刷新，时间小于%s分钟，不需要刷新' % (acct.get("platformName"), acct.get("id"), conf.env.COOKIE_REFRESH_INTERVAL))
                            continue

                        # 加入到待刷新账户集合
                        dict_accounts.append(acct)

                    if dict_accounts:
                        # 获取代理IP（暂时可以不用代理）
                        # proxy_ip = self.get_proxy_ip()
                        # if proxy_ip is None:
                        #     self.logger.error("获取代理IP失败")
                        #     return None

                        # 浏览器对象，一个线程任务共用一个
                        options = webdriver.ChromeOptions()
                        options.add_argument('--headless')
                        options.add_argument('--disable-gpu')
                        options.add_argument("--no-sandbox")
                        options.add_argument('User-Agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36"')
                        # options.add_argument('--proxy-server=http://%(host)s:%(port)s' % {"host" : proxy_ip['ip'], "port" : proxy_ip['port']})

                        browser = webdriver.Chrome(options = options)
                        browser.set_page_load_timeout(60)

                        # 循环待刷新账户，执行刷新操作
                        for acct in dict_accounts:
                            self.__do_refresh(acct, browser)
                            # TODO：如果账户很多，可以在这个循环里控制代理IP使用的时间，如果快过期了，就调出循环，重新执行（即重新获取代理IP）
                except Exception as ex:
                    self.logger.exception(str(ex))
                finally:
                    # 关闭浏览器
                    if browser:
                        browser.quit()

            Profile.end('刷新账户登录状态 -- end --')

            self.logger.info('刷新一轮完成后，休息 %s 分钟' % conf.env.COOKIE_REFRESH_INTERVAL)
            time.sleep(int(conf.env.COOKIE_REFRESH_INTERVAL) * 60)

            # 重新加载配置
            importlib.reload(conf)

    def refresh_nopost_process(self):
        while True:
            # 日志组件
            self.logger = LoggerFactory.get_logger(threading.currentThread().name)

            Profile.begin('刷新账户登录状态 -- begin --')

            # 获取需要刷新登录状态的账户
            _ids = ",".join([str(val.get('id')) for val in self.__list_accounts])
            accounts = AccountModel().get_all(where='isEnable=1 and id in (%s)' % _ids, order_by='id asc')

            # 账户分组
            acct_group = {}
            group_index = 1

            for acct in accounts:
                if group_index in acct_group.keys():
                    acct_group[group_index].append(acct)
                else:
                    acct_group[group_index] = [acct]

                if (accounts.index(acct) + 1) % self.__num_of_ip == 0:
                    group_index += 1

            # 循环账户分组
            for key, accts in acct_group.items():
                # 需要刷新的账户
                dict_accounts = []

                # 循环分组里的账户，先过滤不需要刷新的账户，减少浪费代理IP
                for acct in accts:
                    # 手动登录，Cookie失效时，不需要刷新
                    if acct.get('loginType') == AccountModel.LOGIN_TYPE_MANUAL and acct.get('loginCookieEnable') == 0:
                        self.logger.info('%s，账户ID=%d，Cookie失效，需要手动登录处理' % (acct.get("platformName"), acct.get("id")))
                        continue

                    # 距上次刷新时间 小于15分钟的账户，不做刷新
                    prev_datetime = acct.get('loginCookieUpdateTime')
                    minutes = rrule.rrule(rrule.MINUTELY, prev_datetime, until=datetime.now())
                    if acct.get('loginCookieEnable') and minutes.count() < int(conf.env.COOKIE_REFRESH_INTERVAL_NOPOST):
                        self.logger.info('%s，账户ID=%d，Cookie刷新，时间小于%s分钟，不需要刷新' % (acct.get("platformName"), acct.get("id"), conf.env.COOKIE_REFRESH_INTERVAL_NOPOST))
                        continue

                    # 加入到待刷新账户集合
                    dict_accounts.append(acct)

                if dict_accounts:
                    # 获取代理IP
                    proxy_ip = None

                    # # 循环待刷新账户，执行刷新操作
                    for acct in dict_accounts:
                        # 浏览器对象
                        browser = None

                        try:
                            if proxy_ip is None:
                                proxy_ip = IpManager.get_ip('%s-%s' % (threading.currentThread().name, key))
                                if proxy_ip is None:
                                    self.logger.info("获取代理IP失败，没有有效的代理IP")
                                    continue
                                else:
                                    self.logger.info('获取代理IP：%s' % proxy_ip['ip'])

                            # 浏览器对象，一个线程任务共用一个
                            chrome_options = webdriver.ChromeOptions()
                            chrome_options.add_argument('--headless')
                            chrome_options.add_argument('--disable-gpu')
                            chrome_options.add_argument("--no-sandbox")
                            chrome_options.add_argument("--user-agent=%s" % IpManager.get_headers().get('User-Agent'))
                            if proxy_ip:
                                chrome_options.add_argument('--proxy-server=http://%(host)s:%(port)d' % {"host": proxy_ip['ip'], "port": proxy_ip['port']})
                                # chrome_options.add_argument('--proxy-server=http://%(host)s:%(port)s' % {"host": '66.70.167.116', "port": '3129'})

                            browser = webdriver.Chrome(options=chrome_options)
                            browser.set_page_load_timeout(30)

                            login_cookie_info = self.__do_refresh(acct, browser)

                            # 登录超时，更新代理IP无效
                            if login_cookie_info and login_cookie_info.get('loginTimeout'):
                                # 剔除代理IP
                                IpManager.clear_ip('%s-%s' % (threading.currentThread().name, key))
                                proxy_ip = None

                        except Exception as ex:
                            self.logger.exception(str(ex))

                        # 关闭浏览器
                        if browser:
                            browser.quit()

            Profile.end('刷新账户登录状态 -- end --')

            # 输出使用中的IP
            self.logger.info(IpManager.get_using_ip())

            self.logger.info('刷新一轮完成后，休息 %s 分钟' % conf.env.COOKIE_REFRESH_INTERVAL_NOPOST)
            time.sleep(int(conf.env.COOKIE_REFRESH_INTERVAL_NOPOST) * 60)

            # 重新加载配置
            importlib.reload(conf)


class TaskThread(threading.Thread):
    task = None

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        if self.task:
            self.task.refresh_nopost_process()
        else:
            logger_newsmth.error('task is None！')


# 日志组件
logger_newsmth = LoggerFactory.get_logger('task-refresh-cookie-logger-main')


def refresh_nopost_run(num_of_thread, num_of_ip):
    threads = []

    # 获取需要刷新登录状态的账户
    accounts = AccountModel().get_refresh_accounts(is_post=0)

    # 账户分组
    acct_group = {}
    group_index = 1

    for acct in accounts:
        if group_index in acct_group.keys():
            acct_group[group_index].append(acct)
        else:
            acct_group[group_index] = [acct]

        if (accounts.index(acct) + 1) % num_of_thread == 0:
            group_index += 1

    for key, val in acct_group.items():
        # print(key, val)
        task = TaskRefreshCookie(val, num_of_ip)
        t = TaskThread(task)
        t.name = 'task-refresh-cookie-logger-newsmth-trhead-%d' % key
        t.start()

        logger_newsmth.info('start thread: %s' % t.name)

        threads.append(t)

        # 间隔 5 秒，启动下一个线程
        time.sleep(int(conf.env.COOKIE_REFRESH_INTERVAL_THREAD))

    for thread in threads:
        thread.join()

    logger_newsmth.info('All thread done!!!!!')

    return "0"


def do_execute(do_type, num_of_thread, num_of_ip):
    if do_type.lower() == 'refresh':
        TaskRefreshCookie(None, num_of_ip).refresh_process()
    elif do_type.lower() == 'login':
        TaskRefreshCookie().login_process()
    elif do_type.lower() == 'refresh_nopost':
        refresh_nopost_run(num_of_thread, num_of_ip)


if __name__ == '__main__':
    threading.currentThread().name = 'task-refresh-cookie-logger-main'
    # 设置帮助参数
    usage = """Example: 'python %prog -t auto -g 5'"""
    parser = OptionParser(usage = usage)
    parser.add_option("-t", "--type", action="store", type="string", default='refresh', dest="doType", metavar="[refresh/login/refresh_nopost]", help="Refresh or Login")
    parser.add_option("-g", "--num_of_ip", action="store", type="int", default=5, dest="numOfIp", metavar="", help="number of per ip")
    parser.add_option("-r", "--num_of_thread", action="store", type="int", default=10, dest="numOfThread", metavar="", help="number of per thread")
    (options, args) = parser.parse_args()

    if options.doType.lower() not in ['refresh', 'login', 'refresh_nopost']:
        parser.error("options -t is must [refresh/login/refresh_nopost]")

    do_execute(options.doType, options.numOfThread, options.numOfIp)
    # do_execute('refresh_nopost', 3, 2)
    # do_execute('refresh', 5)
