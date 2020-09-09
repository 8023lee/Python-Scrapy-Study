# -*- coding: utf-8 -*-

"""自动发布SDK基类模块"""

__author__ = 'lijingang'

import time
import threading
import random
from io import BytesIO
from PIL import Image

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import libs.config as conf
from libs.log.logger import LoggerFactory
from libs.vcode.chaojiying import ChaojiyingClient 
from dbs.model.posttask_platform import PostTaskPlatform as PostTaskPlatformModel


class BaseSDK(object):
    http_timeout = 10

    browser = None
    browser_selfmanage = True

    postmodel = None
    has_login = False

    def __init__(self, postmodel, browser = None, http_timeout = 30):
        # 日志组件
        self.logger = LoggerFactory.get_logger(threading.currentThread().name)

        # 超级鹰组件
        self.chaojiying = ChaojiyingClient(conf.env.CJY_USER, conf.env.CJY_PASS, conf.env.CJY_SOFTID)

        # 程序根目录
        self.rootDir = conf.env.ROOT_DIR

        if browser:
            self.browser = browser
            self.browser_selfmanage = False
        else:
            self.browser_selfmanage = True

        self.driver_wait = WebDriverWait(self.browser, self.http_timeout)

        self.http_timeout = http_timeout
        self.postmodel = postmodel
        self.has_login = False

    def browser_selfmanage_open(self):
        """自己管理浏览器，需要自己打开"""
        if self.browser_selfmanage:
            if self.browser:
                self.browser.quit()
            self.browser = webdriver.Chrome()

    def browser_selfmanage_close(self):
        """自己管理浏览器，需要自己关闭"""
        if self.browser_selfmanage and self.browser:
            self.browser.quit()

    def filter_content(self, content, ref_url=''):
        """转义字符替换"""
        content = content.replace("\r", "</br>").replace("\n", "</br>").replace("'", "\\'").replace('"', '\\"')
        return content

        # appendHeader = [
        #     'Java面试题基础', 'Java面试笔试题汇总', 'Java面试题大全', 'Java面试全面汇总', 'Java面试常问题目总结', '经典Java面试题收集', 'Java面试知识点总结及解析',
        #     'java面试题，一线互联网公司面试总结', 'java面试算法搜集', 'java面试题大合集(开发者必看)', 'Java面试官最喜欢问的问题', 'Java开发校招面试考点汇总'
        # ]
        #
        # appendContent = random.sample(appendHeader, 1)[0]
        appendContent = '</br>我总结出了很多互联网公司的面试题及答案，并整理成了文档，以及各种学习的进阶学习资料，免费分享给大家。</br>扫描二维码或搜索下图红色VX号，加VX好友，拉你进【程序员面试学习交流群】免费领取。也欢迎各位一起在群里探讨技术。'
        appendContent += '</br>推荐文章：<a href=\\"https://blog.csdn.net/alogtech6/article/details/89452491\\">Java 面试知识点解析</a>；<a href=\\"https://blog.csdn.net/kuangdashi/article/details/89332193\\">Mysql优化技巧（数据库设计、命名规范、索引优化</a>'
        appendContent += '</br><img src=\\"http://s.baotutu.com/javazz201903.gif\\"/></br>'

        content = content + appendContent

        # 如果是转载，把转载连接放到后面
        if ref_url:
            content += '</br>转载：<a href=\\"%s\\">%s</a></br>' % (ref_url, ref_url)

        # 推荐内容
        posttask_platform_model = PostTaskPlatformModel()
        recommend_tasks = posttask_platform_model.get_random_task(10)
        if recommend_tasks:
            recommend_content = '推荐内容：<br>'
            for task in recommend_tasks:
                recommend_content += '<a href=\\"%s\\">%s</a><br>' % (task['detailUrl'], task['title'])

            content += recommend_content

        return content

    def filer_title(self, title):
        appendTitle = [
            'java基础面试笔试题',
            'java开发面试笔试题',
            'java初级面试笔试题',
            'java高级面试笔试题',
        ]
        appendTitle = random.sample(appendTitle, 1)[0]
        title += "，%s" % appendTitle
        return title

    def do_post(self):
        """处理自动发布逻辑，子类实现具体逻辑"""
        pass

    def refresh(self):
        """刷新页面，保持登录状态"""
        try:            
            self.browser.get(self.postmodel.postUrl)

            time.sleep(1)
            
            curr_url = self.browser.current_url
            if curr_url.find(self.postmodel.postUrl) != 0:
                self.has_login = False
            else:
                self.has_login = True

            self.logger.info('刷新登录状态，current_url = %s, -- %s' % (self.browser.current_url, time.strftime('%Y-%m-%d %H:%M:%S')))
            if not self.has_login:
                self.logger.info('登录状态失效')
        except Exception as ex:
            self.logger.exception('刷新登录状态，异常：%s, %s' % (str(ex), time.strftime('%Y-%m-%d %H:%M:%S')))

    def save_screenshot(self, save_path, force = False):
        """
        截屏
        """
        if conf.env.IS_OPEN_SCREENSHOT or force:
            self.browser.save_screenshot(save_path)


    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_captcha_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        return None

    def get_captcha_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """

        element = self.get_captcha_element()
        time.sleep(2)
        
        location = element.location
        size = element.size
        self.logger.info('简书验证码图片坐标：x=%d, y=%d' % (location['x'], location['y']))
        self.logger.info('简书验证码大小：width=%d, height=%d' % (size['width'], size['height']))

        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_captcha_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象二进制流
        """

        top, bottom, left, right = self.get_captcha_position()
        self.logger.info('验证码位置：top=%d, bottom=%d, left=%d, right=%d', top, bottom, left, right)
        screenshot = self.get_screenshot()

        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(self.rootDir + "/data/logs/" + name)
        return captcha

    def get_captcha_points(self, position_str):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = position_str.split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations
    
    def captcha_click(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            ActionChains(self.browser).move_to_element_with_offset(self.get_captcha_element(), location[0], location[1]).click().perform()
            time.sleep(1 + round(random.random(), 2))


    def refresh_login_cookie(self):
        """
        刷新登录Cookie

        返回值
        -------------
        dict
            返回dict，包括刷新状态，刷新后的Cookie数组
            例：{'loginCookieEnable': 0, 'loginCookie':[]}
        """
        pass



class PostModel(object):
    """自动发布文章数据模型基类

        初始化参数：
        ---------------
        dict_args : dict
        {
            "loginname": "登录用户名",
            "loginpass": "登录密码",
            "title": "文章标题",
            "refUrl": "",
            "imgUrl": "",
            "content": "文章内容",
            "tags": "标签",
            "self_category": "个人分类",
            "postUrl": "发布页面URL",
            "loginCookie": "",
            "loginCookieEnable": 0,
            "loginCookieUpdateTime": ''
        }
    """
    
    has_error = False
    err_message = ''

    loginname = ''
    loginpass = ''
    title = ''
    refUrl = ''
    imgUrl = ''
    content = ''
    tags = ''
    selfCategory = ''
    postUrl = ''
    loginCookie = ''
    loginCookieEnable = ''
    loginCookieUpdateTime = ''

    def __init__(self, dict_args = {}):
        # 参数验证
        attr = ['loginname', 'loginpass', 'title', 'refUrl', 'imgUrl', 'content', 'tags', 'selfCategory', 'postUrl', 'loginCookie', 'loginCookieEnable', 'loginCookieUpdateTime']
        for i, val in enumerate(attr):
            if val not in dict_args.keys():
                self.has_error = True
                self.err_message += '缺少必要的参数[' + val + ']，请参考注释；'
            # elif not dict_args.get(val):
            #     self.has_error = True
            #     self.err_message += '参数[' + val + ']的值为空；'
            else:                
                # exec("self.{} = '{}'".format(val, dict_args.get(val)))
                setattr(self, val, dict_args.get(val))