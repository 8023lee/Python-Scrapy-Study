# -*- coding: utf-8 -*-

"""水木社区发布SDK模块"""

__author__ = 'lijingang'


import time
import json
import threading
from datetime import datetime
from dateutil import rrule

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import libs.config as conf
from libs.log.logger import LoggerFactory
from libs.log.profile import Profile
from libs.postsdk.basesdk import BaseSDK
from libs.postsdk.basesdk import PostModel


class NewsmthSDK(BaseSDK):
    """水木社区SDK

    初始化参数
    --------
    postmodel ：PostModel
        发布数据模型对象
    browser: WebDriver
        浏览器实例，如：webdriver.Chrome()
    http_timeout: int
        请求超时时间，默认30秒
    """

    def __init__(self, postmodel, browser=None, http_timeout=30):
        super().__init__(postmodel, browser, http_timeout)

    def login_by_cookie(self):
        """
        通过Cookie登录
        """
        result = True

        # 登录页面加载
        Profile.begin('水木社区登录页面加载 - login_by_cookie -- begin --')
        self.browser.get('http://www.newsmth.net/nForum/index')
        # self.browser.get(self.postmodel.postUrl)
        # 全屏
        self.browser.maximize_window()
        time.sleep(1)
        self.save_screenshot(self.rootDir + "/data/logs/newsmth_login_bycookie_loaded.png")
        Profile.end('水木社区登录页面加载 - login_by_cookie  -- end --')

        # 加载发布页面
        Profile.begin('水木社区发布页面加载 - login_by_cookie  -- begin --')
        # 添加登录Cookie
        for cookie_old in self.postmodel.loginCookie:
            for cookie_new in self.browser.get_cookies():
                if cookie_new['name'] == cookie_old['name']:
                    # Profile.begin('==== 删除Cookie Begin ====')
                    self.browser.delete_cookie(cookie_new['name'])
                    # Profile.begin('==== 删除Cookie End ====')
            # Profile.begin('==== 添加Cookie Begin ==== %s ' % str(cookie_old))
            self.browser.add_cookie(cookie_old)
            # Profile.begin('==== 添加Cookie End ====')

        # self.logger.info('==== 添加完Cookie后 === cookies：%s' % str(self.browser.get_cookies()))

        # 验证登录状态页面加载
        self.browser.get(self.postmodel.postUrl)
        # 睡一秒
        time.sleep(2)

        self.logger.info('current_url=%s' % self.browser.current_url)

        # 截屏:
        self.save_screenshot(self.rootDir + "/data/logs/newsmth_login_bycookie_result.png")
        Profile.end('水木社区发布页面加载 - login_by_cookie  -- end --')

        cookies = self.browser.get_cookies()
        self.logger.info('==== 刷新Cookie登录 === cookies：%s' % str(cookies))
        if cookies:
            for cookie in cookies:
                if cookie['name'] == 'main[UTMPUSERID]' and cookie['value'] == 'guest':
                    result = False
                    self.logger.info('水木社区LoginCooike失效 - login_by_cookie ')
                    break
        else:
            result = False
            self.logger.info('get_cookies 为空 - login_by_cookie ')

        # if self.browser.current_url != self.postmodel.postUrl:
        #     result = False
        #     self.logger.info('水木社区LoginCooike失效 - login_by_cookie ')

        return result

    def do_post(self):
        """处理自动发布逻辑"""
        pass

    def do_comment(self, arc_url, content):
        result = False

        login_result = self.refresh_login_cookie()

        # 登录成功
        if login_result.get('loginCookieEnable'):
            try:
                # 加载文章详情页面
                Profile.begin('加载文章详情页面 -- begin --')
                self.logger.info('回复帖子：%s' % arc_url)
                self.browser.get(arc_url)
                # 全屏
                self.browser.maximize_window()
                time.sleep(1)
                self.save_screenshot(self.rootDir + "/data/logs/newsmth_comment_arctile_loaded.png")
                Profile.end('加载文章详情页面 -- end --')

                # 快捷回复按钮
                a_reply = self.driver_wait.until(
                    EC.presence_of_element_located((By.ID, 'a_reply'))
                )
                # a_reply.clcik()
                js = "document.getElementById('a_reply').click()"
                self.browser.execute_script(js)

                time.sleep(1)

                quick_text = self.driver_wait.until(
                    EC.presence_of_element_located((By.ID, 'quick_text'))
                )
                quick_text.send_keys(content)

                time.sleep(1)

                # 获取当前URL
                curr_url_01 = self.browser.current_url

                quick_submit =  self.driver_wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="quick_submit"]/input'))
                )
                quick_submit.click()

                time.sleep(2)

                # 等待跳转到成功页面
                sleep_num = 0
                while True:
                    curr_url_02 = self.browser.current_url
                    if curr_url_01 != curr_url_02:
                        result = True
                        break
                    else:
                        time.sleep(1)
                        sleep_num += 1
                        self.logger.info('等待回复成功跳转中......，_sleep_num = %d' % (sleep_num))
                        if sleep_num >= 5:
                            break
            except Exception as ex:
                self.logger.exception(str(ex))

        return result

    def refresh_login_cookie(self):
        login_cookie_enable = self.postmodel.loginCookieEnable
        login_cookie = self.postmodel.loginCookie
        login_timeout = False

        try:
            # 登录Cookie有效，只需要刷新验证一下
            if login_cookie_enable:
                login_cookie_enable = int(self.login_by_cookie())

            # 登录Cookie失效，重新登录，获取新的Cookie
            if not login_cookie_enable:
                # 登录页面加载
                Profile.begin('水木社区登录页面加载 - refresh_login_cookie -- begin --')
                # self.browser.get('http://www.newsmth.net/nForum/#!user/info')
                self.browser.get(self.postmodel.postUrl)
                # 全屏
                self.browser.maximize_window()
                # 睡一秒
                time.sleep(1)
                # 截屏
                self.save_screenshot(self.rootDir + "/data/logs/newsmth_refresh_login_loaded.png")
                Profile.end('水木社区登录页面加载 - refresh_login_cookie -- end --')

                # 登录操作
                Profile.begin('水木社区登录操作 - refresh_login_cookie -- begin --')
                # 登录按钮
                login_by_account = self.driver_wait.until(
                    EC.presence_of_element_located((By.ID, 'u_login_submit'))
                )
                self.browser.find_element_by_id('u_login_id').send_keys(self.postmodel.loginname)
                self.browser.find_element_by_id('u_login_passwd').send_keys(self.postmodel.loginpass)
                # 截屏:
                self.save_screenshot(self.rootDir + "/data/logs/newsmth_refresh_login_for_submit.png")
                # 睡一秒，否则下面点击事件报错，具体原因不清楚
                time.sleep(1)
                # 点击登录按钮
                login_by_account.click()
                # 睡一秒
                time.sleep(2)

                self.logger.info('current_url=%s' % (self.browser.current_url))
                # 截屏
                self.save_screenshot(self.rootDir + "/data/logs/newsmth_refresh_login_result.png")

                # 查找登录成功标识
                div_u_login_id = self.driver_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'u-login-id'))
                )

                cookies = self.browser.get_cookies()
                for cookie in cookies:
                    if cookie['name'] == 'main[UTMPUSERID]' and cookie['value'] != 'guest':
                        login_cookie_enable = 1
                        Profile.end('水木社区登录操作，登录成功 - refresh_login_cookie -- end --')
                        break

                if not login_cookie_enable:
                    Profile.end('水木社区登录操作，登录失败 - refresh_login_cookie -- end --')

                # if self.browser.current_url == self.postmodel.postUrl:
                #     login_cookie_enable = 1
                #     Profile.end('水木社区登录操作 - refresh_login_cookie -- end --')

            # 登录Cookie，可能有多个Cookie，每个Cookie都是dict类型
            if login_cookie_enable:
                login_cookie = []

                cookies = self.browser.get_cookies()
                for cookie in cookies:
                    if cookie['name'] in ['main[UTMPKEY]', 'main[UTMPNUM]', 'main[UTMPUSERID]']:
                        cookie.pop('httpOnly')
                        cookie.pop('secure')
                        login_cookie.append(cookie)
                        if cookie['name'] == 'main[UTMPUSERID]' and cookie['value'] == 'guest':
                            login_cookie_enable = 0

                if not login_cookie:
                    login_cookie_enable = 0

                self.logger.info('水木社区登录刷新 - refresh_login_cookie，Cookie = ' + str(login_cookie))
        except TimeoutException as ex:
            login_cookie_enable = 0
            # 登录超时
            login_timeout = True

            # 刷新时长超过设定值，标记为登录失效
            prev_datetime = self.postmodel.loginCookieUpdateTime
            minutes = rrule.rrule(rrule.MINUTELY, prev_datetime, until=datetime.now())
            if self.postmodel.loginCookieEnable and minutes.count() > int(conf.env.COOKIE_REFRESH_INTERVAL_NOPOST):
                login_cookie_enable = 0
                self.logger.info('刷新时长超过设定值，标记为登录失效，minutes = %d' % minutes.count())

            # 记录错误日志
            self.logger.exception(str(ex))
        except Exception as ex:
            login_cookie_enable = 0
            # 登录发生异常，按超时处理，更换代理IP
            login_timeout = True

            # 刷新时长超过设定值，标记为登录失效
            prev_datetime = self.postmodel.loginCookieUpdateTime
            minutes = rrule.rrule(rrule.MINUTELY, prev_datetime, until=datetime.now())
            if self.postmodel.loginCookieEnable and minutes.count() > int(conf.env.COOKIE_REFRESH_INTERVAL_NOPOST):
                login_cookie_enable = 0
                self.logger.info('刷新时长超过设定值，标记为登录失效，minutes = %d' % minutes.count())

            # 记录错误日志
            self.logger.exception(str(ex))
            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/newsmth_refresh_login_error.png")
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()

        return {'loginCookieEnable': login_cookie_enable, 'loginCookie': login_cookie, 'loginTimeout': login_timeout}

    def do_pull_score(self, login_acct, pull_accts):
        """更新积分和登录状态"""

        pull_success_accts = []

        login_result = self.refresh_login_cookie()

        # 登录成功
        if login_result.get('loginCookieEnable'):
            try:
                # 打开查询积分和登录状态窗口
                div_u_login_id = self.driver_wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="u_login"]//a'))
                )
                div_u_login_id.click()

                time.sleep(1)

                for acct in pull_accts:
                    self.logger.info('账户：%s begin ======== ' % acct.get('loginname'))
                    try:
                        u_search_u = self.driver_wait.until(
                            EC.presence_of_element_located((By.ID, 'u_search_u'))
                        )
                        u_query_search = self.driver_wait.until(
                            EC.presence_of_element_located((By.ID, 'u_query_search'))
                        )

                        u_search_u.send_keys(acct.get('loginname'))
                        u_query_search.click()

                        time.sleep(1)

                        u_name = self.driver_wait.until(
                            EC.presence_of_element_located((By.XPATH, '//*[@class="u-name"]/span'))
                        )

                        loop_num = 0
                        while u_name.text != acct.get('loginname'):
                            time.sleep(1)
                            self.logger.exception('查询等待 1 秒钟')
                            loop_num += 1
                            if loop_num >= 5:
                                raise Exception('查询等待超过5秒，触发异常')

                        # time.sleep(1)
                        # # 截屏:
                        # self.save_screenshot(
                        #     self.rootDir + "/data/logs/newsmth_pullscore_%s.png" % acct.get('loginname'), True)

                        dl_dt = self.driver_wait.until(
                            EC.presence_of_all_elements_located((By.XPATH, '//*[@class="u-info u-detail"]/dl/dt'))
                        )

                        dl_dd = self.driver_wait.until(
                            EC.presence_of_all_elements_located((By.XPATH, '//*[@class="u-info u-detail"]/dl/dd'))
                        )

                        _acct = acct.copy()
                        _acct.clear()
                        _acct['id'] = acct.get('id')

                        for dt in dl_dt:
                            dd = dl_dd[dl_dt.index(dt)]
                            if dt.text == '用户积分：':
                                _acct['score'] = int(dd.text)
                            elif dt.text == '当前状态：':
                                _acct['loginStatus'] = dd.text

                        if _acct['score'] == 0:
                            # 截屏:
                            self.save_screenshot(self.rootDir + "/data/logs/newsmth_pullscore_error_%s.png" % acct.get('loginname'), True)
                            self.logger.exception('%s 积分获取失败' % acct.get('loginname'))

                        pull_success_accts.append(_acct)
                    except Exception as ex:
                        # 截屏:
                        self.save_screenshot(self.rootDir + "/data/logs/newsmth_pullscore_error_%s.png" % acct.get('loginname'), True)
                        self.logger.exception(str(ex))

                    self.logger.info('账户：%s end ======== ' % acct.get('loginname'))
            except Exception as ex:
                self.logger.exception(str(ex))
        else:
            self.logger.info('登录失败，爬取积分失败 ======= ')

        return pull_success_accts


if __name__ == '__main__':
    # 日志组件
    threading.currentThread().name = 'newsmthsdk-main-logger'
    logger = LoggerFactory.get_logger(threading.currentThread().name)
    logger.info('==== start ====')

    from dbs.model.account import Account

    data_model = PostModel({
        "loginname": "LeeLv111",
        "loginpass": "5201111.",
        "title": "谁能想到……",
        "refUrl": "",
        "content": '',
        "tags": "生活",
        "selfCategory": "生活",
        "postUrl": "http://www.newsmth.net/nForum/#!user/passwd",
        "loginCookie": json.loads(
            '[{"domain": ".newsmth.net", "expiry": 2191436480, "name": "main[UTMPNUM]", "path": "/", "value": "12918"}, {"domain": ".newsmth.net", "expiry": 2191436480, "name": "main[UTMPKEY]", "path": "/", "value": "24515708"}, {"domain": ".newsmth.net", "expiry": 2191436480, "name": "main[UTMPUSERID]", "path": "/", "value": "leeLv520"}]'),
        "loginCookieEnable": 1,
        "loginCookieUpdateTime": datetime.strptime("2019-06-17 09:02:04", "%Y-%m-%d %H:%M:%S")
    })

    if not data_model.has_error:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        # options.add_argument('--proxy-server=http://%(host)s:%(port)s' % {"host": '103.99.177.247', "port": '80'})
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)

        newsmth_sdk = NewsmthSDK(data_model, driver)
        # article_url = newsmth_sdk.do_post()
        # print(article_url)

        # login_cookie_info = newsmth_sdk.refresh_login_cookie()
        newsmth_sdk.do_comment('http://www.newsmth.net/nForum/#!article/Divorce/1352131', '不错哦!!!')
        # affected_rows = Account().update_login_cookie(login_cookie_info['loginCookieEnable'], login_cookie_info['loginCookie'], 38)

        driver.quit()

    print(data_model.err_message)

    logger.info('==== end ====')
