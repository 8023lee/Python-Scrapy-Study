# -*- conding:utf-8 -*-

"""发布文章和回复文章模块"""

__author__ = 'lijingang'


import importlib
import time
import threading
import json
import random

from optparse import OptionParser
from selenium import webdriver

import libs.config as conf
from libs.log.logger import LoggerFactory
from libs.proxy.ip_manager import IpManager
from task.post.basetask import BaseTask
from dbs.model.account import Account as AccountModel


class TaskMewsmth(BaseTask):
    # 账号信息
    __list_accounts = []

    def __init__(self):
        super().__init__()

    def do_comment(self, __num_of_ip):
        threading.currentThread().name = 'task-newsmth-comment'
        while True:
            try:
                # 日志组件
                self.logger = LoggerFactory.get_logger(threading.currentThread().name)

                # 获取回复内容
                comment_content_list = conf.env.NEWSMTH_COMMENT_CONTENT.split('|')

                # 取出可用账户
                list_accouts = AccountModel().get_all(where="platformSn='newsmth' and isEnable=1 and score>=2500")

                # 账户分组
                acct_group = {}
                group_index = 1

                for acct in list_accouts:
                    if group_index in acct_group.keys():
                        acct_group[group_index].append(acct)
                    else:
                        acct_group[group_index] = [acct]

                    if (list_accouts.index(acct) + 1) % __num_of_ip == 0:
                        group_index += 1

                # 获取可回复帖子URL 列表
                articles = self.__get_article_list()

                # 循环账户分组
                for key, accts in acct_group.items():
                    # 获取代理IP
                    proxy_ip = None

                    # 循环账户
                    for acct in accts:
                        # 浏览器对象
                        browser = None

                        try:
                            # POP出 URL 列表第一项，然后追加到末尾
                            arc_url = articles.pop(0)
                            articles.append(arc_url)

                            # 构建PostModel数据
                            _acct = acct.copy()
                            _acct['title'] = ''
                            _acct['content'] = ''
                            _acct['tags'] = ''
                            _acct['selfCategory'] = ''
                            _acct['loginCookie'] = json.loads(acct['loginCookie'])
                            _acct['refUrl'] = ''

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

                            # 获取SDK
                            sdk = self.get_sdk(_acct, browser)
                            if sdk:
                                result = sdk.do_comment(arc_url, random.choice(comment_content_list))

                                # 回复失败
                                if not result:
                                    # 剔除代理IP
                                    IpManager.clear_ip('%s-%s' % (threading.currentThread().name, key))
                                    proxy_ip = None

                        except Exception as ex:
                            self.logger.exception(str(ex))

                        # 关闭浏览器
                        if browser:
                            browser.quit()

                    # 一组账号回复完成，休息 ** 分钟，变量可配置
                    self.logger.info('回复一组完成后，休息 %s 分钟' % conf.env.NEWSMTH_COMMENT_GROUP_INTERVAL)
                    time.sleep(int(conf.env.NEWSMTH_COMMENT_GROUP_INTERVAL) * 60)

                # 输出使用中的IP
                self.logger.info(IpManager.get_using_ip())

                # 账户循环一遍，休息 ** 分钟，变量可配置
                self.logger.info('回复一轮完成后，休息 %s 分钟' % conf.env.NEWSMTH_COMMENT_INTERVAL)
                time.sleep(int(conf.env.NEWSMTH_COMMENT_INTERVAL) * 60)

                # 重新加载配置
                importlib.reload(conf)
            except Exception as ex:
                self.logger.exception(str(ex))

    def __get_article_list(self):
        """
        获取可以回复的文章URL
        :return:
        """
        arc_urls = []

        browser = None
        try:
            # 浏览器对象，一个线程任务共用一个
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--user-agent=%s" % IpManager.get_headers().get('User-Agent'))

            browser = webdriver.Chrome(options=chrome_options)
            browser.set_page_load_timeout(30)
            browser.get('http://www.newsmth.net/nForum/#!mainpage')
            # 全屏
            browser.maximize_window()

            div_list = browser.find_elements_by_xpath('//*[@id="top10"]//li//div')
            for div in div_list:
                a_cat = div.find_elements_by_tag_name('a')[0].get_attribute('title')
                if a_cat == '股票研究':
                    continue
                a_url = div.find_elements_by_tag_name('a')[1].get_attribute('href')
                if a_url:
                    arc_urls.append(a_url)
        except Exception as ex:
            self.logger.exception(ex)
        finally:
            if browser:
                browser.quit()

        return arc_urls

    def do_post(self):
        pass

    def do_pull_score(self, is_auto=0):
        threading.currentThread().name = 'task-newsmth-score'

        while True:
            # 日志组件
            logger = LoggerFactory.get_logger(threading.currentThread().name)

            if is_auto:
                h = time.localtime().tm_hour
                if h != 6:
                    logger.info('没有到执行时间，休息 1 个小时')
                    time.sleep(1 * 60 * 60)
                    continue

            logger.info("============爬取积分 begin ============")

            try:
                # 取出可用账户
                list_accouts = AccountModel().get_all(where="platformSn='newsmth' and isEnable=1")

                # 获取代理IP
                proxy_ip = None

                # 登录账户（LeeLv520）
                login_acct = None
                # 需要获取积分的账户
                pull_accts = []

                # 循环账户
                for acct in list_accouts:
                    # 构建PostModel数据
                    _acct = acct.copy()
                    _acct['title'] = ''
                    _acct['content'] = ''
                    _acct['tags'] = ''
                    _acct['selfCategory'] = ''
                    _acct['loginCookie'] = json.loads(acct['loginCookie'])
                    _acct['refUrl'] = ''

                    if _acct.get('loginname') == 'generation':
                        login_acct = _acct

                    pull_accts.append(_acct)

                # 浏览器对象
                browser = None
                try:
                    # if proxy_ip is None:
                    #     proxy_ip = IpManager.get_ip('%s' % threading.currentThread().name)
                    #     if proxy_ip is None:
                    #         logger.info("获取代理IP失败，没有有效的代理IP")
                    #         return
                    #     else:
                    #         logger.info('获取代理IP：%s' % proxy_ip['ip'])

                    # 浏览器对象，一个线程任务共用一个
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--user-agent=%s" % IpManager.get_headers().get('User-Agent'))
                    if proxy_ip:
                        chrome_options.add_argument('--proxy-server=http://%(host)s:%(port)d' % {"host": proxy_ip['ip'], "port": proxy_ip['port']})

                    browser = webdriver.Chrome(options=chrome_options)
                    browser.set_page_load_timeout(30)

                    # 获取SDK
                    sdk = self.get_sdk(login_acct, browser)
                    if sdk:
                        success_accts = sdk.do_pull_score(login_acct, pull_accts)
                        for acct in success_accts:
                            acct['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            # 更新数据库
                            affect_rows = AccountModel().update(acct)
                            logger.info('更新账户结果 - affect_rows：%s' % affect_rows)

                except Exception as ex:
                    logger.exception(str(ex))

                # 关闭浏览器
                if browser:
                    browser.quit()
            except Exception as ex:
                logger.exception(str(ex))

            logger.info("============爬取积分 end ============")

            if is_auto:
                logger.info('爬取完成，休息 1 个小时')
                time.sleep(1 * 60 * 60)
            else:
                break


def do_execute(do_type, num_of_ip):
    if do_type.lower() == 'post':
        TaskMewsmth().do_post()
    elif do_type.lower() == 'comment':
        TaskMewsmth().do_comment(num_of_ip)
    elif do_type.lower() == 'pullscore':
        TaskMewsmth().do_pull_score(num_of_ip)


if __name__ == '__main__':
    threading.currentThread().name = 'task-newsmth-main'
    # 设置帮助参数
    usage = """Example: 'python %prog -t comment'"""
    parser = OptionParser(usage = usage)
    parser.add_option("-t", "--type", action="store", type="string", default='comment', dest="doType", metavar="[post/comment/pullscore]", help="Post or Comment or Pullscore")
    parser.add_option("-g", "--num_of_ip", action="store", type="int", default=5, dest="numOfIp", metavar="", help="number of per ip")
    (options, args) = parser.parse_args()

    if options.doType.lower() not in ['post', 'comment', 'pullscore']:
        parser.error("options -t is must [post/comment/pullscore]")

    do_execute(options.doType, options.numOfIp)
    # do_execute('comment', 1)
    # do_execute('pullscore', 0)
