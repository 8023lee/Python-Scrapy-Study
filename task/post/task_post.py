# -*- conding:utf-8 -*-

__author__ = 'lijingang'

import time
import threading
import importlib
import json

from selenium import webdriver

import libs.config as conf
from libs.log.logger import LoggerFactory
from task.post.basetask import BaseTask
from dbs.model.posttask_platform import PostTaskPlatform as PostTaskPlatformModel


class TaskPost(BaseTask):
    # 账号信息
    __dict_accounts = {}

    def __init__(self, dict_accounts):
        self.__dict_accounts = dict_accounts

    def get_posttask_platform(self, account_id):
        """获取需要处理的任务"""

        porttask_platform_model = PostTaskPlatformModel()
        posttask_platform = porttask_platform_model.get_posttask_platform(account_id)
        return posttask_platform

    def update_posttask_platform(self, posttask_platform_id, articleUrl):
        """更新 post_task_platform 状态"""

        porttask_platform_model = PostTaskPlatformModel()
        affected_rows = porttask_platform_model.update_posttask_platform(posttask_platform_id, articleUrl)
        return affected_rows

    # 处理任务
    def do_process(self):
        while True:
            # 日志组件
            self.logger = LoggerFactory.get_logger(threading.currentThread().ident)

            try:
                # 浏览器对象
                browser = None
                
                # 待发布任务集合
                dict_posttasks = []

                # 先取任务，减少没有任务时，浪费代理IP
                for account in self.__dict_accounts:
                    posttask_platform = self.get_posttask_platform(account.get('id'))
                    if posttask_platform:
                        posttask_platform['loginname'] = account.get('loginname')
                        posttask_platform['loginpass'] = account.get('loginpass')
                        posttask_platform['postUrl'] = account.get('postUrl')
                        posttask_platform['loginCookie'] = json.loads(account.get('loginCookie'))
                        posttask_platform['loginCookieEnable'] = account.get('loginCookieEnable')
                        posttask_platform['loginCookieUpdateTime'] = account.get('loginCookieUpdateTime')
                        
                        # 加入到待发布任务集合
                        dict_posttasks.append(posttask_platform)

                if dict_posttasks:
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
                    browser.set_page_load_timeout(30)

                    # 循环待发布任务，执行发布操作
                    for posttask in dict_posttasks:
                        self.logger.info('发布任务，platformSn：%s - taskId：%d - title：%s' % (posttask.get('platformSn'), posttask.get('id'), posttask.get('title')))
                        
                        sdk = self.get_sdk(posttask, browser)
                        if sdk:
                            # 发布文章
                            articleUrl = sdk.do_post()
                            # 更新 post_task_platform 状态
                            self.update_posttask_platform(posttask['id'], articleUrl)
                            # TODO：如果任务很多，可以在这个循环里控制代理IP使用的时间，如果快过期了，就调出循环，重新执行（即重新获取代理IP）
            except Exception as ex:
                self.logger.exception(str(ex))
            finally:
                # 关闭浏览器
                if browser:
                    browser.quit()

            self.logger.info('发布一轮完成后，休息 %s 分钟' % (conf.env.POST_INTERVAL))
            time.sleep(int(conf.env.POST_INTERVAL) * 60)

            # 重新加载配置
            importlib.reload(conf)

if __name__ == '__main__':
    # 日志组件
    logger = LoggerFactory.get_logger()

    logger.info('==== post task running start ====')
    from dbs.model.account import Account as AccountModel

     # 获取账号信息
    accountModel = AccountModel()
    accounts = accountModel.get_post_accounts()

    for key, val in accounts.items():
        # print(key, val)
        task = TaskPost(val)
        task.do_process()

    logger.info('==== post task running end ====')