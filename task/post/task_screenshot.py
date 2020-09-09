# -*- conding:utf-8 -*-

import re
import time
import threading
from io import BytesIO
from PIL import Image

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from dbs.db import DB
from libs.log.logger import LoggerFactory
from libs.log.profile import Profile

import libs.config as conf

class TaskScreenshot(object):
    def __init__(self):
        # DB组件
        self.DB = DB()
        # 日志组件
        self.logger = LoggerFactory.get_logger(threading.currentThread().name)

    def __get_tasks(self):
        data = None

        try:
            sql = "select id, url from m_post_task where imgUrl = ''"

            self.DB.connect()
            data = self.DB.fetchall(sql)
        except Exception as ex:
            self.logger.exception('获取待截图任务，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

    def __update_img_url(self, taskId, imgUrl):
        self.DB.connect()
        try:
            sql = 'update m_post_task set imgUrl = "%s" where id=%d' % (imgUrl, taskId)

            affected_rows = self.DB.execute(sql)

            self.DB.commit()
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('更新 imgUrl，异常：%s', str(ex))
        finally:
            self.DB.close()

    def __get_screenshot_position(self, browser):
        driver_wait = WebDriverWait(browser, 60)

        element = driver_wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'container')))

        element = element[1]

        location = element.location
        size = element.size
        self.logger.info('排行榜截图：x=%d, y=%d' % (location['x'], location['y']))
        self.logger.info('排行榜截图大小：width=%d, height=%d' % (size['width'], size['height']))

        top, bottom, left, right = location['y'] + 100, location['y'] + size['height'] + 600, location['x'], location['x'] + size['width'] + 1500

        return (top, bottom, left, right)

    def __get_screenshot(self, browser):
        screenshot = browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def do_execute(self):
        while True:
            # 日志组件，每天都创建新的logger，保证每天一个日志文件
            self.logger = LoggerFactory.get_logger(threading.currentThread().name)

            # 取数据
            _tasks = self.__get_tasks()

            Profile.begin('北鹿鹿、音法数据排行榜 截图 -- begin --')

            try:
                # 浏览器对象
                browser = None

                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument("--no-sandbox")
                options.add_argument(
                    'User-Agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36"')
                # options.add_argument('--proxy-server=http://%(host)s:%(port)s' % {"host" : proxy_ip['ip'], "port" : proxy_ip['port']})

                browser = webdriver.Chrome(options=options)
                browser.set_page_load_timeout(60)

                for task in _tasks:

                    browser.get(task['url'])
                    browser.maximize_window()
                    # 睡一秒
                    time.sleep(2)

                    scroll_width = 1500
                    scroll_height = 700
                    browser.set_window_size(scroll_width, scroll_height)
                    # 睡一秒
                    time.sleep(2)

                    # top, bottom, left, right = self.__get_screenshot_position(browser)
                    #
                    # self.logger.info('验证码位置：top=%d, bottom=%d, left=%d, right=%d', top, bottom, left, right)

                    img_date = re.findall("[0-9]{8}", task['url'])
                    if task['url'].find('yinfa') > 0:
                        img_name = 'yinfa-' + img_date[0] + '.png'
                    else:
                        img_name = 'beilulu-' + img_date[0] + '.png'

                    save_path = conf.env.IMG_SAVE_PATH + '/' + img_name

                    # screenshot = self.__get_screenshot(browser)
                    # captcha = screenshot.crop((left, top, right, bottom))
                    # captcha.save(save_path)

                    browser.save_screenshot(save_path)

                    # 更新数据库
                    self.__update_img_url(task['id'], conf.env.IMG_DOMAIN + '/' + img_name)

            except Exception as ex:
                self.logger.exception(str(ex))
            finally:
                # 关闭浏览器
                if browser:
                    browser.quit()

            Profile.end('北鹿鹿、音法数据排行榜 截图 -- end --')

            self.logger.info('处理一轮完成后，休息 %s 分钟' % 180)

            time.sleep(180 * 60)


if __name__ == '__main__':

    threading.currentThread().name = 'task-screenshot-logger-main'
    TaskScreenshot().do_execute()


