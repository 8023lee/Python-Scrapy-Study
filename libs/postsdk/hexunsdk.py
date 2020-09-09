# -*- coding: utf-8 -*-

"""和讯博客发布SDK模块"""

__author__ = 'lijingang'

import os
import sys
import time
import json
import urllib.parse

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from libs.log.logger import LoggerFactory
from libs.log.profile import Profile
from libs.postsdk.basesdk import BaseSDK
from libs.postsdk.basesdk import PostModel

class HexunSDK(BaseSDK):
    """和讯博客自动发布SDK
    
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
        Profile.begin('和讯登录页面加载-- begin --')
        self.browser.get('http://reg.hexun.com/login.aspx')
        # 全屏
        self.browser.maximize_window()
        time.sleep(1)
        self.save_screenshot(self.rootDir + "/data/logs/hexun_login_loaded.png")
        Profile.end('和讯登录页面加载 -- end --')

        # 加载发布页面
        Profile.begin('和讯发布页面加载 -- begin --')
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
        self.save_screenshot(self.rootDir + "/data/logs/hexun_post_loaded.png")
        Profile.end('和讯发布页面加载 -- end --')

        if self.browser.current_url != self.postmodel.postUrl:
            result = False
            self.logger.info('和讯LoginCooike失效')

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
                EC.presence_of_element_located((By.ID, 'hxjy_blog_tit'))
            )
            title.clear()
            title.send_keys(self.postmodel.title)

            # 显示个人分类
            # open_select_ul = self.browser.find_element_by_id('hxjy_blog_Classify_trigger')
            # open_select_ul.click()
            js = 'document.getElementById("hxjy_blog_Classify_trigger").click()'
            self.browser.execute_script(js)
            time.sleep(1)
            # 选择添加新分类
            # self.browser.find_element_by_xpath('//*[@class="wt_select1-List-addsort"]').click()
            js = 'document.getElementsByClassName("wt_select1-List-addsort")[0].click()'
            self.browser.execute_script(js)
            time.sleep(1)

            # 输入个人分类
            catetory_input = self.driver_wait.until(
                EC.presence_of_element_located((By.ID, 'NewCategoryTextbox'))
            )
            catetory_input.send_keys(self.postmodel.selfCategory)

            # 标签，空格分割多个标签
            tag_input = self.browser.find_element_by_id('hxjy_blog_label')
            tag_input.send_keys(self.postmodel.tags)

            # 文章来源
            self.browser.find_element_by_id('PostType').click()

            # 选择不投稿
            post_class = self.browser.find_elements_by_name('PostClass')
            post_class[1].click()

            # 内容       
            # 获取编辑器，点击一下，否则发布，提示内容为空
            editor = self.browser.find_element_by_class_name('editor')
            editor.click()
            # 转义字符，黏贴到编辑器
            content = self.filter_content(self.postmodel.content)
            js = 'Editor.pasteHTML("' + content + '");'
            self.browser.execute_script(js)

            # 检查是否有验证码
            verification_div = self.browser.find_element_by_id('VerificationDiv')
            if verification_div and verification_div.is_displayed():
                raise Exception('发布出现图形验证码，发布失败')
            
            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/hexun_post_loaded_for_submit.png")

            Profile.begin('和讯发布操作 -- begin --')
            # 滚动发布按钮到可见区域
            js = 'document.getElementById("postarticle").scrollIntoViewIfNeeded();'
            self.browser.execute_script(js)
            # 存草稿
            # self.browser.find_element_by_id('savearticle').click()
            # 发布文章
            publish_btn = self.browser.find_element_by_id('postarticle')
            publish_btn.click()
            time.sleep(1)
            Profile.end('和讯发布操作 -- end --')

            # 等待跳转到发布成功页面
            sleep_num = 0
            while True:
                curr_url = self.browser.current_url
                # a = 'http://' + self.postmodel.postUrl.split('/')[3] + '.blog.hexun.com'
                if curr_url.find('http://' + self.postmodel.postUrl.split('/')[3] + '.blog.hexun.com') != 0:
                    time.sleep(1)
                    sleep_num += 1
                    self.logger.info('和讯发布成功跳转到详情页面，_sleep_num = %d' % (sleep_num))
                    if sleep_num > 5:
                        # 检查是否有非法词汇
                        error_msg = ''
                        try:
                            error_msg = self.browser.find_element_by_id('Message').text
                        except NoSuchElementException as nex:
                            pass

                        raise Exception('和讯发布失败：%s' % error_msg)
                    else:
                        continue
                else:
                    # 获取文章URL
                    article_url = self.browser.current_url
                    break
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)
            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/hexun_error.png")
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
                Profile.begin('和讯登录页面加载 -- begin --')
                self.browser.get('http://blog.hexun.com')
                # 全屏
                self.browser.maximize_window()
                # 睡一秒
                time.sleep(1)
                # 截屏
                self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_hexun_login_loaded_mask.png")
                # 关闭提示
                read_btn = self.driver_wait.until(
                    EC.presence_of_element_located((By.ID, 'read_btn'))
                )
                read_btn.click()
                # 睡一秒
                time.sleep(1)
                # 截屏
                self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_hexun_login_loaded.png")
                Profile.end('和讯登录页面加载 -- end --')

                # 登录操作
                Profile.begin('和讯登录操作 -- begin --')
                # 登录按钮
                login_by_account = self.driver_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'lg12_sub'))
                )
                self.browser.find_element_by_id('username').send_keys(self.postmodel.loginname)
                self.browser.find_element_by_id('password').send_keys(self.postmodel.loginpass)
                # 截屏:
                self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_hexun_login_loaded_for_submit.png")
                # 睡一秒，否则下面点击事件报错，具体原因不清楚
                time.sleep(1)
                # 点击登录按钮
                login_by_account.click()
                # 睡一秒
                time.sleep(2)

                # 查找"写博客"连接，表示登录成功
                write_blog = self.driver_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'lg12_gb_btn'))
                )

                if write_blog:
                    login_cookie_enable = 1
                    Profile.end('和讯登录操作 -- end --')
            
            # 登录Cookie，可能有多个Cookie，每个Cookie都是dict类型
            if login_cookie_enable:
                login_cookie = []

                cookies = self.browser.get_cookies()
                for cookie in cookies:
                    if cookie['name'] == 'userToken':
                        cookie.pop('httpOnly')
                        cookie.pop('secure')
                        login_cookie.append(cookie)

                self.logger.info('和讯登录刷新，Cookie = ' + str(login_cookie))
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)
            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_hexun_error.png")
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
        "loginpass": "asdf1111",
        "title": "中国妈妈为何这么累？",
        "content": '''<p><p>母爱是人类的共性，几乎所有的妈妈，都是爱孩子的。<p>''',
        "tags": "赚钱 工作",
        "selfCategory": "生活",
        "postUrl": "http://post.blog.hexun.com/31091589/newpostblog.aspx",
        "loginCookie": json.loads('[{"domain": ".hexun.com", "name": "userToken", "path": "/", "value": "31091589%7c0000%7c0%2cQIiHcYeeDx8DsmxdLtHM05ENXgUXSMfceN3%2bK6V4TL7exS7Unekk2dumOX0zUlQl0y10q6g7KZKhNXU6V1e98a3jazJmbDh5WIxjcZT6XAh4c%2bMjqE6RdeHOuh38NhyCs2lWJ99%2buLsVDeTs%2botDUXIlw3Js%2bfHLQo5ms5yQe9W25VKwtltcDwkFBkMEvJ%2b92aT9fw%2f37o3bsofP3z3vDA%3d%3d"}]'),
        "loginCookieEnable": 1
    })


    if not data_model.has_error:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options = options)
        driver.set_page_load_timeout(30)

        hexun_sdk = HexunSDK(data_model, driver)
        article_url = hexun_sdk.do_post()
        print(article_url)

        # login_cookie_info = hexun_sdk.refresh_login_cookie()
        # affected_rows = Account().update_login_cookie(login_cookie_info['loginCookieEnable'], login_cookie_info['loginCookie'], 2)

        # time.sleep(10)

        # article_url = hexun_sdk.do_post()
        # print(_article_url)

        driver.quit()

    print(data_model.err_message)

    logger.info('==== end ====')