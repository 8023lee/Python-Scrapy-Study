# -*- coding: utf-8 -*-

"""新浪博客发布SDK模块"""

__author__ = 'lijingang'

import os
import sys
import time
import json
import urllib.parse
from datetime import datetime
from optparse import OptionParser
from io import BytesIO
from PIL import Image

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException

import libs.config as conf
from libs.log.logger import LoggerFactory
from libs.log.profile import Profile
from libs.postsdk.basesdk import BaseSDK
from libs.postsdk.basesdk import PostModel

from dbs.model.account import Account as AccountModel


class SinaSDK(BaseSDK):
    """新浪博客自动发布SDK
    
    初始化参数
    --------
    postmodel ： PostModel 
        发布数据模型对象
    browser: WebDriver
        浏览器实例，如：webdriver.Chrome()
    http_timeout: int
        请求超时时间，默认30秒
    """
    
    def __init__(self, postmodel, browser = None, http_timeout = 30):
        super().__init__(postmodel, browser, http_timeout)

    def login_check_code(self):
        """
        图形验证码验证
        """
        # 测试环境，手动点击验证码，不做接口调用，减少浪费提分
        if conf.env.IS_CJY_DEBUG:
            return True
        
        result = False

        Profile.begin('登录验证码验证 -- begin --')
        # 登录按钮
        login_by_account = self.driver_wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="W_btn_a btn_34px"]'))
        )
        # 截屏
        self.save_screenshot(self.rootDir + "/data/logs/sina_login_checkcode_01.png")

        # 截取验证码图片
        check_img = WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.ID, 'check_img'))
        )

        # 验证码打码
        Profile.begin('登录验证码，打码 -- begin --')
        resultJson = self.chaojiying.digital_check(check_img.screenshot_as_png)
        Profile.end('登录验证码，打码 -- end --')

        if (resultJson['err_no'] == 0):
            v_code = resultJson['pic_str']

            # 输入验证码
            door = self.browser.find_element_by_id('door')
            door.clear()
            door.send_keys(v_code)

            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/sina_login_checkcode_02.png")

            # 点击登录按钮
            login_by_account.click()
            time.sleep(2)

            sleep_num = 0
            while True:
                sleep_num += 1
                curr_url = self.browser.current_url
                if curr_url.find('signin.php') > 0:
                    if sleep_num > 3:
                        # 打码失败(登录失败，就认为打码失败)，上报错误，补回题分
                        self.chaojiying.ReportError(resultJson['pic_id'])
                        break
                    else:
                        time.sleep(1)
                        self.logger.info('登录验证码验证，跳转中，sleep_num = %d' % (sleep_num))
                else:
                    result = True
                    Profile.end('登录验证码验证 -- end --')
                    break
        else:
            pass

        return result

    def login_by_cookie(self):
        """
        处理登录逻辑
        """
        result = False

        # 首页页面加载
        Profile.begin('新浪登录页面加载-- begin --')
        self.browser.get('http://blog.sina.com.cn')
        # 全屏
        self.browser.maximize_window()
        time.sleep(1)
        self.save_screenshot(self.rootDir + "/data/logs/sina_login_loaded.png")
        Profile.end('新浪登录页面加载 -- end --')

        _cookies = self.browser.get_cookies()
        print(_cookies)

        # 加载发布页面
        Profile.begin('新浪发布页面加载 -- begin --')
        # 添加登录Cookie
        for cookie_old in self.postmodel.loginCookie:
            for cookie_new in self.browser.get_cookies():
                if cookie_new['name'] == cookie_old['name']:
                    self.browser.delete_cookie(cookie_new['name'])
            self.browser.add_cookie(cookie_old)

        _cookies = self.browser.get_cookies()
        print(_cookies)
        _f = open(self.rootDir + '/data/logs/sina_cookie.txt', 'a')
        _f.write(str(_cookies))
        _f.close()

        # 写博客
        self.browser.get(self.postmodel.postUrl)
        # 睡一秒
        time.sleep(3)
        # 截屏:
        self.save_screenshot(self.rootDir + "/data/logs/sina_post_loaded.png")
        Profile.end('新浪发布页面加载 -- end --')

        if self.browser.current_url != self.postmodel.postUrl:
            self.logger.info('新浪LoginCooike失效')
        else:
            try:
                # 关闭蒙层
                close_help = WebDriverWait(self.browser, 2).until(
                    lambda d: d.find_element_by_class_name('guide_btn')
                )
                close_help.click()
            except TimeoutException as ex:
                self.logger.exception('关闭蒙层，异常：%s', str(ex))
            finally:
                pass

            result = True

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

            # 填写标题
            title = self.driver_wait.until(EC.presence_of_element_located((By.ID, 'article_title')))
            title.clear()
            title.send_keys(self.postmodel.title)

            # 个人分类
            # 显示分类
            # open_select_ul = self.driver_wait.until(lambda d: d.find_element_by_id('blog_cate_select'))
            # time.sleep(1)
            # print(open_select_ul)
            # open_select_ul.click()

            # js = 'document.getElementById("blog_cate_select").click()'
            # self.browser.execute_script(js)
            # time.sleep(1)
            # #选择分类
            # category = self.postmodel.selfCategory
            # cate_list = self.browser.find_elements_by_xpath('//*[@id="blog_cate_list"]/li/a/span')
            # for cate in cate_list:
            #     if cate.text == category:
            #         # js = 'document.getElementById("blog_cate_list").firstElementChild.click()'
            #         # self.browser.execute_script(js)
            #         cate.click()
            #         break

            # 截屏
            # self.save_screenshot(self.rootDir + "/data/logs/sina_select_category.png")

            time.sleep(1)

            # # 标签 空格分割多个标签
            # tag_input = self.browser.find_element_by_id('t_input')
            # tag_input.send_keys(self.postmodel.tags)

            try:
                # 确保编辑器渲染成功
                editor = self.driver_wait.until(EC.presence_of_element_located((By.ID, 'editor')))
                # 内容
                content = self.filter_content(self.postmodel.content)
                content = content + "\n<img src='"+ self.postmodel.imgUrl +"' width='700px' alt='"+ self.postmodel.title +"'/>\n\n"
                js = 'editor.body.innerHTML="' + content + '"'
                self.browser.execute_script(js)
            except WebDriverException as identifier:
                time.sleep(5)
                # 内容
                content = self.filter_content(self.postmodel.content)
                content = content + "\n<img src='" + self.postmodel.imgUrl + "' width='700px' alt='" + self.postmodel.title + "'/>\n\n"
                js = 'editor.body.innerHTML="' + content + '"'
                self.browser.execute_script(js)
                pass
            finally:
                pass

            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/sina_post_loaded_for_submit.png")
            
            Profile.begin('新浪发布操作 -- begin --')
            # 9存草稿
            # self.browser.find_element_by_id('articlePosTempBtn').click()
            # 发布文章
            publish_btn = self.browser.find_element_by_id('articlePostBtn')
            publish_btn.click()
            time.sleep(1)
            Profile.begin('新浪发布操作 -- end --')

            # 获取文章URL
            article_a = self.driver_wait.until(lambda d: d.find_elements_by_xpath('//*[@class="e_prompt_cont e_pro_align"]/p/a'))
            article_url = article_a[0].get_attribute('href')
            article_url = urllib.parse.unquote(article_url)
            article_url = article_url.split('url=')[1]
            # article_url = "http://www.baidu.com"
            #testUrl = 'http://control.blog.sina.com.cn/admin/article/changWeiBo.php?url=http%3A%2F%2Fblog.sina.com.cn%2Fs%2Fblog_19dd310ee0102z1s8.html'
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)
            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/sina_error.png")
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()

        # 返回详情页面URL
        return article_url

    def refresh_login_cookie(self):
        """
        刷新登录Cookie
        """
        login_cookie_enable = self.postmodel.loginCookieEnable
        login_cookie = self.postmodel.loginCookie

        try:
            # 登录Cookie有效，只需要刷新验证一下
            if login_cookie_enable:
                login_cookie_enable = int(self.login_by_cookie())

            # 登录Cookie失效，重新登录，获取新的Cookie
            # if not login_cookie_enable:
            #     # 登录页面加载
            #     Profile.begin('新浪登录页面加载 -- begin --')
            #     self.browser.get('https://login.sina.com.cn/signup/signin.php?entry=blog&r=http%3A%2F%2Fcontrol.blog.sina.com.cn%2Fadmin%2Farticle%2Farticle_add.php%3Fis_new_editor%3D1&from=referer:http://control.blog.sina.com.cn/admin/article/article_add.php?is_new_editor%3D1,func:0006')
            #     # 全屏
            #     self.browser.maximize_window()
            #     # 睡一秒
            #     time.sleep(1)
            #     # 截屏
            #     self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_sina_login_loaded.png")
            #     Profile.end('新浪登录页面加载 -- end --')
            #
            #     # 登录操作
            #     Profile.begin('新浪登录操作 -- begin --')
            #     # 登录按钮
            #     login_by_account = self.driver_wait.until(
            #         EC.presence_of_element_located((By.XPATH, '//*[@class="W_btn_a btn_34px"]'))
            #     )
            #     self.browser.find_element_by_id('username').send_keys(self.postmodel.loginname)
            #     self.browser.find_element_by_id('password').send_keys(self.postmodel.loginpass)
            #
            #     # 点击登录按钮
            #     login_by_account.click()
            #     # 睡一秒
            #     time.sleep(2)
            #
            #     # # TODO: 因为测试时，不出现验证码，所以通过脚本把验证码显示出来，上线时需要注释掉
            #     # js = 'document.getElementById("door_content").style["display"] = "";document.getElementById("door").removeAttribute("disabled");'
            #     # self.browser.execute_script(js)
            #
            #     result = False
            #
            #     # 等待跳转到发布页面
            #     sleep_num = 0
            #     while True:
            #         # 控制尝试次数
            #         sleep_num += 1
            #
            #         curr_url = self.browser.current_url
            #         if curr_url.find('signin.php') > 0:
            #             # 检查是否需要验证码
            #             try:
            #                 door_content = WebDriverWait(self.browser, 2).until(
            #                     EC.presence_of_element_located((By.ID, 'door_content'))
            #                 )
            #             except TimeoutException as ex:
            #                 self.logger.exception('查找验证码表单超时，_sleep_num = %d，_curr_url = %s，异常：%s' % (sleep_num, self.browser.current_url, str(ex)))
            #                 door_content = None
            #             finally:
            #                 pass
            #
            #             # 需要验证码
            #             if door_content and door_content.is_displayed():
            #                 # 验证码验证
            #                 result = self.login_check_code()
            #                 if result == True:
            #                     break
            #                 else:
            #                     # 刷新验证码
            #                     if sleep_num < 3:
            #                         a = self.browser.find_element_by_xpath('//*[@id="door_img"]/a')
            #                         a.click()
            #                         time.sleep(1)
            #             else:
            #                 # 截屏:
            #                 self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_sina_sleep.png")
            #
            #                 self.logger.info('新浪博客登录跳转到发布页面，_sleep_num = %d' % (sleep_num))
            #                 time.sleep(1)
            #
            #             if sleep_num >= 3:
            #                 break
            #             else:
            #                 continue
            #         else:
            #             result = True
            #             break
            #
            #     if result:
            #         login_cookie_enable = 1
            #         Profile.end('新浪登录操作 -- end --')

            # 登录Cookie，可能有多个Cookie，每个Cookie都是dict类型

            if login_cookie_enable:
                login_cookie = []

                cookies = self.browser.get_cookies()
                for cookie in cookies:
                    if cookie['name'] in ['SUB','ALF']:
                        cookie.pop('httpOnly')
                        cookie.pop('secure')
                        login_cookie.append(cookie)

                self.logger.info('%s，账户ID=%s，登录刷新成功，Cookie = %s' % ("新浪", self.postmodel.loginname, str(login_cookie)))
            else:
                self.logger.info('%s，账户ID=%s，登录失效，需要手动登录' % ("新浪", self.postmodel.loginname))

        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)
            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_sina_error.png")
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()

        return {'loginCookieEnable': login_cookie_enable, 'loginCookie':login_cookie}

    def login(self):
        """
        处理登录逻辑
        """
        _result = False

        # 登录页面加载
        Profile.begin('新浪登录页面加载 -- begin --')
        self.browser.get('http://blog.sina.com.cn')
        # 全屏
        self.browser.maximize_window()
        # 睡一秒
        time.sleep(1)
        # 截屏
        self.save_screenshot(self.rootDir + "/data/logs/sina_login_loaded.png")
        Profile.end('新浪登录页面加载 -- end --')

        # 登录按钮
        login_by_account = self.driver_wait.until(
            EC.presence_of_element_located((By.ID, 'submit-btn'))
        )
        self.browser.find_element_by_id('loginName').send_keys(self.postmodel.loginname)
        self.browser.find_element_by_id('loginPassword').send_keys(self.postmodel.loginpass)

        # 点击登录按钮
        login_by_account.click()
        # 睡一秒
        time.sleep(2)

        _result = True
        if _result:
            # 读取Cookie，保存到文件 TODO:
            _cookies = self.browser.get_cookies()
            print(_cookies)
            _f = open(self.rootDir + '/data/logs/sina_cookie.txt', 'a')
            _f.write(str(_cookies))
            _f.close()

            # 写入数据库
            login_cookie = []
            for cookie in _cookies:
                if cookie['name'] in ['SUB', 'ALF']:
                    cookie.pop('httpOnly')
                    cookie.pop('secure')
                    login_cookie.append(cookie)

            # 更新数据库Cookie状态
            acct = AccountModel().get_one(
                "platformSn='sina' and loginname='" + self.postmodel.loginname + "'")
            if acct:
                AccountModel().update_login_cookie(1, login_cookie, acct.get('id'))

        return _result



if __name__ == '__main__':
    loginname = "18911418111"
    loginpass = "asdf1111"

    # 设置帮助参数
    usage = """Example: 'python %prog -t auto -g 5'"""
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--type", action="store", type="string", default='post', dest="type",
                      metavar="[post/login/refresh]", help="Login by manual")
    parser.add_option("-u", "--username", action="store", type="string", default=loginname, dest="username", metavar="",
                      help="login username")
    parser.add_option("-p", "--password", action="store", type="string", default=loginpass, dest="password", metavar="",
                      help="login password")

    (options, args) = parser.parse_args()
    if options.type.lower() not in ['post', 'login', 'refresh']:
        parser.error("options -t is must [post/login/refresh]")

    # 模型
    _data_model = PostModel({
        "loginname": options.username,
        "loginpass": options.password,
        "title": "区块链交易处理流程描述",
        "content": '''恭喜珠宝配饰分类下的”韩国珍珠发夹10个装（款式随机）“，带货商品销量6.7w, 勇夺销量榜第一''',
        "tags": "区块链",
        "selfCategory": "区块链",
        "postUrl": "http://control.blog.sina.com.cn/admin/article/article_add.php?is_new_editor=1",
        "refUrl": "",
        "imgUrl": "http://www.beilulu.com/screenshot/beilulu-20200612.png",
        "loginCookie": json.loads('[{"domain": ".sina.com.cn", "name": "SUB", "path": "/", "value": "_2A25z8evYDeRhGeBH71AZ8izKyDSIHXVQh1oQrDV_PUJbm9AKLWL7kW9NQdWwIEEZ3rtai1FOizXtlH475T5MDGSK"}, {"domain": ".sina.com.cn", "expiry": 1593158038, "name": "ALF", "path": "/", "value": "6942822638"}]'),
        "loginCookieEnable": 1,
        "loginCookieUpdateTime": datetime.strptime("2019-06-26 14:58:04", "%Y-%m-%d %H:%M:%S")

    })

    if _data_model.has_error:
        print(_data_model.err_message)
        exit(0)

    # ==== webdriver ====================================
    _options = webdriver.ChromeOptions()
    # _options.add_argument('--headless')
    _options.add_argument('--disable-gpu')
    _options.add_argument('--no-sandbox')
    _options.add_argument('lang=zh_CN.UTF-8')
    _options.add_argument(
        'User-Agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36"')
    # _options.add_argument('--proxy-server=http://223.215.174.208:4216')

    # prefs = {"profile.managed_default_content_settings.images": 2}
    # _options.add_experimental_option("prefs", prefs)

    _driver = webdriver.Chrome(options=_options)
    _driver.set_page_load_timeout(60)

    # _driver.get("http://httpbin.org/get")
    # print(_driver.page_source)
    # ==== webdriver ====================================

    _sina_sdk = SinaSDK(_data_model, _driver)

    if options.type == 'login':
        _sina_sdk.login()
    elif options.type == 'refresh':
        _sina_sdk.refresh_login_cookie()
    else:
        # 日志组件
        logger = LoggerFactory.get_logger()
        logger.info('==== start ====')

        _article_url = _sina_sdk.do_post()
        print(_article_url)

        logger.info('==== end ====')

    # 关闭浏览器
    _driver.quit()
