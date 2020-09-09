# -*- coding: utf-8 -*-

"""简书发布SDK模块"""

__author__ = 'lijingang'

import json
import time
from datetime import datetime
from optparse import OptionParser
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from libs.log.logger import LoggerFactory
from libs.log.profile import Profile
from libs.postsdk.basesdk import BaseSDK
from libs.postsdk.basesdk import PostModel

from dbs.model.account import Account as AccountModel


class JianshuSDK(BaseSDK):
    """简书自动发布SDK
    
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

    def get_captcha_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_widget')))
        return element

    def get_captcha_position(self):
        """
        修正验证码图像的高度

        覆盖基类的方法，因为需要对高度做修正
        """
        top, bottom, left, right = super().get_captcha_position()
        bottom -= 58
        return (top, bottom, left, right)

    def login_check_code(self):
        """
        图形验证码验证
        """
        # 测试环境，手动点击验证码，不做接口调用，减少浪费提分
        # if conf.env.IS_CJY_DEBUG:
        #     return True
        
        _result = False

        Profile.begin('登录验证码验证 -- begin --')
        # 登录按钮
        _login_by_account = self.driver_wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_commit"]'))
        )
        # 截屏
        self.save_screenshot(self.rootDir + "/data/logs/jianshu_login_checkcode_01.png")

        # 截取验证码图片
        _check_img = self.get_captcha_image('jianshu_login_checkcode_img.png')
        _bytes_array = BytesIO()
        _check_img.save(_bytes_array, format='PNG')

        # 验证码打码
        Profile.begin('登录验证码，打码 -- begin --')
        _resultJson = self.chaojiying.axes_check(_bytes_array.getvalue())
        Profile.end('登录验证码，打码 -- end --')

        if (_resultJson['err_no'] == 0):
            _v_code = _resultJson['pic_str']
            
            # 解析验证码坐标
            _locations = self.get_captcha_points(_v_code)
            self.logger.info('登录验证码坐标 = %s' % (str(_locations)))

            # 顺序点击验证
            self.captcha_click(_locations)

            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/jianshu_login_checkcode_02.png")

            # 点击登录按钮
            _login_by_account.click()
            time.sleep(2)

            _sleep_num = 0
            while True:
                _sleep_num += 1
                _curr_url = self.browser.current_url
                if _curr_url.find('sign_in') > 0:
                    if _sleep_num >= 3:
                        # 打码失败(登录失败，就认为打码失败)，上报错误，补回题分
                        self.chaojiying.ReportError(_resultJson['pic_id'])
                        break
                    else:
                        time.sleep(1)
                        self.logger.info('登录验证码验证，跳转中，_sleep_num = %d' % (_sleep_num))
                else:
                    _result = True
                    Profile.end('登录验证码验证 -- end --')
                    break
        else:
            pass

        return _result

    def login(self):
        """
        处理登录逻辑
        """
        _result = False

        # 登录页面加载
        Profile.begin('简书登录页面加载 -- begin --')
        self.browser.get('https://www.jianshu.com/sign_in')
        # 全屏
        self.browser.maximize_window()
        # 睡一秒
        time.sleep(1)
        # 截屏
        self.save_screenshot(self.rootDir + "/data/logs/jianshu_login_loaded.png")
        Profile.end('简书登录页面加载 -- end --')

        # 登录操作
        # Profile.begin('简书登录操作 -- begin --')
        # 登录按钮
        _login_by_account = self.driver_wait.until(
            EC.presence_of_element_located((By.ID, 'sign-in-form-submit-btn'))
        )
        self.browser.find_element_by_id('session_email_or_mobile_number').send_keys(self.postmodel.loginname)
        self.browser.find_element_by_id('session_password').send_keys(self.postmodel.loginpass)
        # 点击登录按钮
        _login_by_account.click()
        # 睡一秒
        time.sleep(10)

        # # 等待跳转到发布页面
        # _sleep_num = 0
        # while True:
        #     # 控制尝试次数
        #     _sleep_num += 1

        #     # 验证码验证
        #     _result = self.login_check_code()
        #     if _result == True:
        #         break
            
        #     if _sleep_num >= 1:
        #         break

        _result = True
        if _result:
            # Profile.end('简书登录操作 -- end --')
            # 读取Cookie，保存到文件 TODO:
            _cookies = self.browser.get_cookies()
            print(_cookies)
            _f = open(self.rootDir + '/data/logs/jianshu_cookie.txt', 'a')
            _f.write(str(_cookies))
            _f.close()

            # 写入数据库
            login_cookie = []
            for cookie in _cookies:
                if cookie['name'] in ['_m7e_session_core']:
                    cookie.pop('httpOnly')
                    cookie.pop('secure')
                    cookie.pop('expiry')
                    login_cookie.append(cookie)

            # 更新数据库Cookie状态
            acct = AccountModel().get_one("platformSn='jianshu' and loginname='" + self.postmodel.loginname + "'")
            if acct:
                AccountModel().update_login_cookie(1, login_cookie, acct.get('id'))

        return _result

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

            # 登录Cookie，可能有多个Cookie，每个Cookie都是dict类型
            if login_cookie_enable:
                login_cookie = []

                cookies = self.browser.get_cookies()
                for cookie in cookies:
                    if cookie['name'] in ['_m7e_session_core']:
                        cookie.pop('httpOnly')
                        cookie.pop('secure')
                        cookie.pop('expiry')
                        login_cookie.append(cookie)

                self.logger.info('%s，账户ID=%s，登录刷新成功，Cookie = %s' % ("简书", self.postmodel.loginname, str(login_cookie)))
            else:
                self.logger.info('%s，账户ID=%s，登录失效，需要手动登录' % ("简书", self.postmodel.loginname))
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)
            # 截屏:
            self.save_screenshot(self.rootDir + "/data/logs/refresh_cookie_jianshu_error.png", True)
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()

        return {'loginCookieEnable': login_cookie_enable, 'loginCookie':login_cookie}

    def login_by_cookie(self):
        """
        处理登录逻辑
        """
        _result = False

        # # # 登录页面加载
        Profile.begin('简书Cookie登录页面加载 -- begin --')
        self.browser.get('https://www.jianshu.com/sign_in')
        # 全屏
        self.browser.maximize_window()
        # 睡一秒
        time.sleep(1)
        # 截屏
        self.save_screenshot(self.rootDir + "/data/logs/jianshu_cookie_login_loaded.png")

        _cookies = self.browser.get_cookies()
        print(_cookies)

        # 添加登录Cookie
        for cookie_old in self.postmodel.loginCookie:
            for cookie_new in _cookies:
                if cookie_new['name'] == cookie_old['name']:
                    self.browser.delete_cookie(cookie_new['name'])
            self.browser.add_cookie(cookie_old)

        _cookies = self.browser.get_cookies()
        print(_cookies)
        _f = open(self.rootDir + '/data/logs/jianshu_cookie.txt', 'a')
        _f.write(str(_cookies))
        _f.close()

        # 加载发布页面
        _write_blog_url = self.postmodel.postUrl
        self.browser.get(_write_blog_url)

        # 睡一秒
        time.sleep(3)

        # 判断登录是否成功
        if self.browser.current_url.find('https://www.jianshu.com/writer') >= 0:
            _result = True

        return _result

    def do_post(self):
        """
        处理自动发布逻辑
        """
        # 发布文章的URL
        _article_url = ''

        # 自己管理浏览器，需要自己打开
        self.browser_selfmanage_open()

        try:
            if not self.has_login:
                # 登录逻辑处理
                _result = self.login_by_cookie()
                if _result == False:
                    raise Exception('登录失败')

                # 记录登录状态
                self.has_login = True
            
            # 加载发布页面
            Profile.begin('简书发布页面加载 -- begin --')
            # 写博客
            _write_blog_url = self.postmodel.postUrl
            self.browser.get(_write_blog_url)
            # 睡一秒
            time.sleep(1)

            # 截屏
            self.save_screenshot(self.rootDir + "/data/logs/jianshu_post_loaded_01.png")
            Profile.end('简书发布页面加载 -- end --')

            time.sleep(1)

            # 分类
            _cate_list = self.driver_wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_3DM7w')))
            for c in _cate_list:
                _c_title = c.get_attribute('title')
                if self.postmodel.selfCategory == _c_title:
                    c.click()
                    break
                else:
                    # TODO 如果分类不存在，还可以直接新建分类
                    pass
            
            time.sleep(1)

            # 点击'新建文章'
            _new_article_btn = self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1GsW5')))
            _new_article_btn.click()
            # # 选择刚刚创建的文章
            # _curr_article = self.driver_wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="_2TxA-"]/li[1]')))
            # _curr_article.click()

            time.sleep(1)

            # 标题
            _title = self.browser.find_element_by_class_name('_24i7u')
            _title.clear()
            _title.send_keys(self.postmodel.title)

            # 内容
            _editor = self.browser.find_element_by_class_name('_3swFR')
            _editor.clear()
            _editor.send_keys('')
            # 转义字符，黏贴到编辑器
            # _content = self.filter_content(self.postmodel.content)
            # js = 'document.getElementById("editor").firstChild.innerHTML = "' + _content + '"'
            # self.browser.execute_script(js)
            # 给编辑器赋值空值，否则 发布 时提示内容为空
            # _editor.send_keys(' ')

            _content = self.postmodel.content;
            _content = _content + '!['+ self.postmodel.title +'](' + self.postmodel.imgUrl + ')'
            _editor.send_keys(_content)

            # 编辑器获得焦点
            _editor.send_keys(Keys.ENTER)
            time.sleep(2)

            # ==== 测试上传图片 ====

            # time.sleep(2)

            # _upImg = self.browser.find_element_by_class_name('fa-picture-o')
            # _upImg.click()
            #
            # time.sleep(1)
            #
            # _md7x2 = self.browser.find_element_by_class_name('md7x2')
            # _md7x2.click()
            #
            # time.sleep(1)
            #
            # _imgUrl = self.browser.find_element_by_id('email')
            # _imgUrl.clear()
            # _imgUrl.send_keys(self.postmodel.imgUrl)
            #
            # self.save_screenshot(self.rootDir + "/data/logs/jianshu_post_upload_img_01.png")
            # time.sleep(1)
            #
            # _upBtn = self.browser.find_element_by_css_selector("[class='Bz3IP _3zXcJ _3QfkW']")
            # _upBtn.click()
            #
            # time.sleep(1)
            #
            # scroll_width = 1500
            # scroll_height = 2000
            # self.browser.set_window_size(scroll_width, scroll_height)
            # time.sleep(1)
            # self.save_screenshot(self.rootDir + "/data/logs/jianshu_post_upload_img_02.png")
            # time.sleep(10)
            #
            # # ==== 测试上传图片 ====
            #
            # # 截屏
            # self.save_screenshot(self.rootDir + "/data/logs/jianshu_post_loaded_02.png")
            #
            # time.sleep(2)

            Profile.begin('简书发布操作 -- begin --')
            # 发布文章
            _publish_btn = self.browser.find_element_by_css_selector("[class='tGbI7 cztJE']")
            _publish_btn.click()
            time.sleep(5)
            Profile.end('简书发布操作 -- end --')

            self.save_screenshot(self.rootDir + "/data/logs/jianshu_published.png")

            # return ''
            # 获取文章URL
            _article_li = self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1HWk1')))
            _article_url = _article_li.get_attribute('data-clipboard-text')
            # _article_url = "http://www.baidu.com"
        except Exception as ex:
            # 记录错误日志
            self.logger.exception(ex)

            # todo:
            self.save_screenshot(self.rootDir + "/data/logs/jianshu_error.png")
        finally:
            # 自己管理浏览器，需要自己关闭
            self.browser_selfmanage_close()

        # 返回详情页面URL
        return _article_url


if __name__ == '__main__':
    loginname = "18911418111"
    loginpass = "asdf12341111"

    # 设置帮助参数
    usage = """Example: 'python %prog -t auto -g 5'"""
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--type", action="store", type="string", default='post', dest="type",
                      metavar="[post/login]", help="Login by manual")
    parser.add_option("-u", "--username", action="store", type="string", default=loginname, dest="username", metavar="",
                      help="login username")
    parser.add_option("-p", "--password", action="store", type="string", default=loginpass, dest="password", metavar="",
                      help="login password")

    (options, args) = parser.parse_args()
    if options.type.lower() not in ['post', 'login']:
        parser.error("options -t is must [post/login]")

    # 模型
    _data_model = PostModel({
        "loginname": options.username,
        "loginpass": options.password,
        "title": "区块链交易处理流程描述",
        "content": '''恭喜珠宝配饰分类下的”韩国珍珠发夹10个装（款式随机）“，带货商品销量6.7w, 勇夺销量榜第一''',
        "tags": "区块链",
        "selfCategory": "区块链",
        "postUrl": "https://www.jianshu.com/writer",
        "refUrl": "",
        "imgUrl": "http://www.beilulu.com/screenshot/beilulu-20200612.png",
        "loginCookie": json.loads(
            '[{"domain": ".jianshu.com", "name": "_m7e_session_core", "path": "/", "value": "5bc0d4e6aba249fa760d4cc6f8d321d5"}]'),
        "loginCookieEnable": 1,
        "loginCookieUpdateTime": datetime.strptime("2019-06-17 09:02:04", "%Y-%m-%d %H:%M:%S")
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

    _jianshu_sdk = JianshuSDK(_data_model, _driver)

    if options.type == 'login':
        _jianshu_sdk.login()
    else:
        # 日志组件
        logger = LoggerFactory.get_logger()
        logger.info('==== start ====')

        _article_url = _jianshu_sdk.do_post()
        print(_article_url)

        # _article_url = _jianshu_sdk.do_post()
        # print(_article_url)

        logger.info('==== end ====')

    # 关闭浏览器
    _driver.quit()