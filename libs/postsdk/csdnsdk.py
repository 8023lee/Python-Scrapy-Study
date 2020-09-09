# -*- coding: utf-8 -*-

"""CSDN发布SDK模块"""

__author__ = 'lijingang'

import time
import json

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from libs.log.logger import LoggerFactory
from libs.log.profile import Profile
from libs.postsdk.basesdk import BaseSDK
from libs.postsdk.basesdk import PostModel


class CsdnSDK(BaseSDK):
    """CSDN自动发布SDK
    
    初始化参数
    --------
    postmodel ：PostModel 
        发布数据模型对象
    browser: WebDriver
        浏览器实例，如：webdriver.Chrome()
    http_timeout: int
        请求超时时间，默认30秒
    """

    def __init__(self, postmodel, browser = None, http_timeout = 30):
        super().__init__(postmodel, browser, http_timeout)

    def login_by_cookie(self):
        """
        通过Cookie登录
        """
        result = True

        # 登录页面加载
        Profile.begin('CSDN登录页面加载-- begin --')
        self.browser.get('https://www.csdn.net')
        # 全屏
        self.browser.maximize_window()
        time.sleep(1)
        self.save_screenshot(self.rootDir + "/data/logs/csdn_login_loaded.png")
        Profile.end('CSDN登录页面加载 -- end --')

        # 加载发布页面
        Profile.begin('CSDN发布页面加载 -- begin --')
        # 添加登录Cookie
        for cookie_old in self.postmodel.loginCookie:
            for cookie_new in self.browser.get_cookies():
                if cookie_new['name'] == cookie_old['name']:
                    self.browser.delete_cookie(cookie_new['name'])
            self.browser.add_cookie(cookie_old)

        # 写博客
        self.browser.get(self.postmodel.postUrl)
        # 睡一秒
        time.sleep(1)
        # 截屏:
        self.save_screenshot(self.rootDir + "/data/logs/csdn_post_loaded_mask.png")
        # 点击"开始写作"
        start = self.driver_wait.until(
            EC.presence_of_element_located((By.ID, 'btnStart'))
        )
        start.click()
        # 截屏:
        self.save_screenshot(self.rootDir + "/data/logs/csdn_post_loaded.png")
        Profile.end('CSDN发布页面加载 -- end --')

        if self.browser.current_url != self.postmodel.postUrl:
            result = False
            self.logger.info('CSDNLoginCooike失效')

        return result

    def do_post(self):
        """
        处理自动发布逻辑
        """

        # 发布文章的URL
        article_url = ''

        # 自己管理浏览器，需要自己打开
        self.browser_selfmanage_open()

        try:
            if not self.has_login:
                # 登录逻辑处理
                result = self.login_by_cookie()
                if result == False:
                    raise Exception('登录失败')
                
                # 记录登录状态
                self.has_login = True

            time.sleep(1)

            # 标题
            title = self.driver_wait.until(
                EC.presence_of_element_located((By.ID, 'txtTitle'))
            )
            title.clear()
            title.send_keys(self.filer_title(self.postmodel.title))

            # 内容
            # 转义字符，黏贴到编辑器
            content = self.filter_content(self.postmodel.content, self.postmodel.refUrl)
            js = 'CKEDITOR.instances.editor.setData("' + content + '");'
            self.browser.execute_script(js)

            # 标签 
            tags = self.postmodel.tags.split(' ')
            add_tag = self.driver_wait.until(
                EC.presence_of_element_located((By.ID, 'addTag'))
            )            
            for i, tag in enumerate(tags):
                add_tag.click()
                tag_input = self.driver_wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="articleTagBox"]/div[' + str(i + 1) + ']/span'))
                )
                tag_input.send_keys(tag)

            #个人分类
            cats = self.postmodel.selfCategory.split(' ')
            add_category = self.driver_wait.until(
                    EC.presence_of_element_located((By.ID, 'addCategorie'))
            )
            for i, cat in enumerate(cats):
                add_category.click()
                cat_input = self.driver_wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="categorieBox"]/div[' + str(i + 1) + ']/span'))
                )
                cat_input.send_keys(cat)

            #文章类型
            select = Select(self.browser.find_element_by_id('selType'))
            # select.select_by_visible_text(self.postmodel.article_type)
            select.select_by_visible_text('原创')

            #博客分类
            select = Select(self.browser.find_element_by_id('radChl'))
            # select.select_by_visible_text(self.postmodel.sys_type)
            select.select_by_visible_text('互联网')
           
            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/csdn_post_loaded_for_submit.png")

            Profile.begin('CSDN发布操作 -- begin --')
            # 存草稿
            # self.browser.find_element_by_id('btnDraft').click()
            # 发布文章
            publish_btn = self.browser.find_element_by_id('btnPublish')
            publish_btn.click()
            time.sleep(1)
            Profile.end('CSDN发布操作 -- end --')

            # 获取文章URL 
            article_A = self.driver_wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="toarticle"]'))
            )
            article_url = article_A.get_attribute('href')

            if not article_url:
                # 截屏
                self.save_screenshot(self.rootDir + "/data/logs/csdn_post_fail_not_articleurl.png", True)
                raise Exception('CSDN发布失败：未获取到文章URL')
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)

            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/csdn_error.png", True)
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()
        
        # 返回详情页面URL
        return article_url

    def refresh_login_cookie(self):
        login_cookie_enable = self.postmodel.loginCookieEnable
        login_cookie = self.postmodel.loginCookie

        try:
            # 登录Cookie有效，只需要刷新验证一下
            if login_cookie_enable:
                login_cookie_enable = int(self.login_by_cookie())

            # 登录Cookie失效，重新登录，获取新的Cookie
            if not login_cookie_enable:
                # 登录页面加载
                Profile.begin('CSDN登录页面加载 -- begin --')
                self.browser.get('https://passport.csdn.net/login')
                # 全屏
                self.browser.maximize_window()
                # 睡一秒
                time.sleep(1)
                # 使用账号密码登陆
                login_by_account = self.driver_wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="main-select"]//li[2]'))
                )
                login_by_account.click()
                # 睡一秒
                time.sleep(1)
                # 截屏
                self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_csdn_login_loaded.png")
                Profile.end('CSDN登录页面加载 -- end --')

                # 登录操作
                Profile.begin('CSDN登录操作 -- begin --')
                # 登录按钮
                login_by_account = self.driver_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'btn'))
                )
                self.browser.find_element_by_id('all').send_keys(self.postmodel.loginname)
                self.browser.find_element_by_id('password-number').send_keys(self.postmodel.loginpass)
                # 截屏:
                self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_csdn_login_loaded_for_submit.png")
                # 睡一秒
                time.sleep(1)
                # 点击登录按钮
                login_by_account.click()
                # 睡一秒
                time.sleep(2)

                # 检查当前URL，判断登录是否成功
                curr_url = self.browser.current_url

                self.logger.info('登录成功后url=%s', curr_url)
                # 截屏:
                self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_csdn_login_end.png", True)

                if curr_url in ['https://www.csdn.net/', 'https://mp.csdn.net/mdeditor#']:
                    login_cookie_enable = 1
                    Profile.end('CSDN登录操作 -- end --')

            # 登录Cookie，可能有多个Cookie，每个Cookie都是dict类型
            if login_cookie_enable:
                login_cookie = []

                cookies = self.browser.get_cookies()
                for cookie in cookies:
                    if cookie['name'] in ['UserInfo', 'UserName', 'UserNick', 'UserToken']:
                        cookie.pop('httpOnly')
                        cookie.pop('secure')
                        login_cookie.append(cookie)

                self.logger.info('CSDN登录刷新，Cookie = ' + str(login_cookie))
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)
            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_csdn_error.png", True)
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()

        return {'loginCookieEnable': login_cookie_enable, 'loginCookie':login_cookie}


if __name__ == '__main__':
    # 日志组件
    logger = LoggerFactory.get_logger()
    logger.info('==== start ====')

    from dbs.model.account import Account

    data_model = PostModel({
        "loginname": "18911418111",
        "loginpass": "111",
        "title": "我是怎么把一个项目带崩的",
        "refUrl": "",
        "content": '''<p>我是一名项目经理，在过去的四个月里，我把一个项目带崩了（上线后频出问题，用户无法使用）。在最近的几天，我每天都在反思自己，我都在问自己以下几个问题：<br>''',
        "tags": "项目管理",
        "selfCategory": "项目管理",
        "postUrl": "https://mp.csdn.net/postedit?not_checkout=1",
        "loginCookie": json.loads('[{"domain": ".csdn.net", "expiry": 1558000292.363064, "name": "UserNick", "path": "/", "value": "weixin_42907620_Lee"}, {"domain": ".csdn.net", "expiry": 1558000292.362889, "name": "UserToken", "path": "/", "value": "2cdf34e811b24fd99fefd1bf06ed289b"}, {"domain": ".csdn.net", "expiry": 1558000292.362786, "name": "UserInfo", "path": "/", "value": "2cdf34e811b24fd99fefd1bf06ed289b"}, {"domain": ".csdn.net", "expiry": 1558000292.362603, "name": "UserName", "path": "/", "value": "weixin_42907620"}]'),
        "loginCookieEnable": 1
    })

    if not data_model.has_error:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options = options)
        driver.set_page_load_timeout(30)

        csdn_sdk = CsdnSDK(data_model, driver)

        # article_url = csdn_sdk.do_post()
        # print(article_url)

        # login_cookie_info = csdn_sdk.refresh_login_cookie()
        # affected_rows = Account().update_login_cookie(login_cookie_info['loginCookieEnable'], login_cookie_info['loginCookie'], 6)

        # time.sleep(10)

        article_url = csdn_sdk.do_post()
        print(article_url)

        driver.quit()

    # print(data_model.err_message)

    logger.info('==== end ====')