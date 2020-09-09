# -*- conding:utf-8 -*-
__author__ = 'lijingang'


#方式一
import os, sys
import time
import threading
from threading import Thread


from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from libs.log.logger import LoggerFactory

# 日志组件
logger = LoggerFactory.get_logger()

class task(Thread):
    def __init__(self, key, accounts):
        super().__init__()
        self.key = key
        self.accounts = accounts

    def run(self):
        print(threading.currentThread().ident)
        logger = LoggerFactory.get_logger(threading.currentThread().ident)
        print(LoggerFactory.loggers())
        logger.info('----' + str(threading.currentThread().ident) +  '---')

        # try:
        #     if self.key == '13011110002':
        #         time.sleep(2)

        #     timeout = 10

        #     _handlers = {}

        #     sina_acct = self.accounts[0]
        #     hexun_acct = self.accounts[1]

        #     login = 'http://blog.sina.com.cn'
        #     driver = webdriver.Chrome()    
        #     driver.set_page_load_timeout(10)

        #     try:
        #         driver.get(login)
        #     except TimeoutException:  
        #         print('time out after 30 seconds when loading page')
        #         driver.execute_script('window.stop()') #当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
        #     except Exception:
        #         raise

        #     _handlers[sina_acct.get('platformsn')] = driver.current_window_handle

        #     # 4.使用账号密码登陆
        #     login_by_account = WebDriverWait(driver, timeout).until(            
        #         EC.presence_of_element_located((By.XPATH, '//*[@id="submit-btn"]'))
        #     )

        #     driver.find_element_by_id('loginName').send_keys(sina_acct.get('loginname'))
        #     driver.find_element_by_id('loginPassword').send_keys(sina_acct.get('loginpwd'))

        #     time.sleep(1)

        #     login_by_account.click()

        #     # =====

        #     # 2.跳转登陆
        #     login = 'http://blog.hexun.com/'            

        #     print(driver.current_window_handle)

        #     new_page='window.open("' + login + '");'
        #     driver.execute_script(new_page)

        #     time.sleep(1)

        #     print(driver.current_window_handle)

        #     _handlers[hexun_acct.get('platformsn')] = driver.window_handles[len(driver.window_handles) - 1]

        #     print(driver.window_handles)
        #     print(_handlers)

        #     driver.switch_to.window(_handlers[hexun_acct.get('platformsn')])

        #     # 关闭提示
        #     read_btn = WebDriverWait(driver, timeout).until(
        #         EC.presence_of_element_located((By.ID, 'read_btn'))
        #     )
        #     read_btn.click()

        #     # 4.使用账号密码登陆
        #     login_by_account = WebDriverWait(driver, timeout).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, 'lg12_sub'))
        #     )

        #     driver.find_element_by_id('username').send_keys(hexun_acct.get('loginname'))
        #     driver.find_element_by_id('password').send_keys(hexun_acct.get('loginpwd'))

        #     login_by_account.click()

        # except Exception as identifier:
        #     raise
        # finally:
        #     driver.quit()

# 测试代理
def test_proxy():
    # 代理服务器
    proxyHost = "42.230.30.147"
    proxyPort = "1246"
    proxyType='http' #socks5

    # 代理隧道验证信息
    # service_args = [
    #     "--proxy-type=%s" % proxyType,
    #     "--proxy=%(host)s:%(port)s" % {
    #         "host" : proxyHost,
    #         "port" : proxyPort,
    #     }
    # ]

    # print(service_args)
    # print('--proxy-server=http://%(host)s:%(port)s' % {"host" : proxyHost, "port" : proxyPort})
    # sys.exit(0)
    
    # driver = webdriver.Chrome(service_args = service_args)

    # options = webdriver.ChromeOptions()
    # options.add_argument('--proxy-server=http://%(host)s:%(port)s' % {"host" : proxyHost, "port" : proxyPort})  
    # driver = webdriver.Chrome(options = options)

    # # 查看本机ip，查看代理是否起作用
    # driver.get("http://httpbin.org/ip")
    # print(driver.page_source)

    # driver.close()
    # driver.quit()

    # return

    proxy = Proxy()
    proxy.http_proxy='%(host)s:%(port)s' % {"host" : proxyHost, "port" : proxyPort}
    proxy.add_to_capabilities(webdriver.DesiredCapabilities.CHROME)

    driver = webdriver.Chrome(proxy)
    # 新建一个会话，并把参数传入，可以多次修改ip，用start_session实现动态修改ip
    # driver.start_session(webdriver.DesiredCapabilities.CHROME)

    # 要访问的目标页面
    driver.get("http://httpbin.org/ip")
    print(driver.page_source)

    # print(driver.title)
    driver.quit()
    pass

lock = threading.Lock()

def Count(id):
    global num;
 
    while True:
        lock.acquire()
        if num <= 10:
 
            print("Thread id is : %s     The num is %s\n" % (id, str(num)))
            num = num + 1
            lock.release()
        else:
            lock.release()
            print(threading.currentThread().name)
            break
        

        time.sleep(1)
 

def test_image():
    #coding=utf-8
    from PIL import Image
    
    _options = webdriver.ChromeOptions()
    _options.add_argument('--headless')
    _options.add_argument('--disable-gpu')
    _options.add_argument('--no-sandbox')

    driver=webdriver.Chrome(options = _options)
    driver.get("https://www.baidu.com")
    # 全屏
    driver.maximize_window()

    driver.save_screenshot('/data/study/send_tasks/data/logs/baidu_button.png')

    # body = driver.find_element_by_tag_name('html')
    # print(body.location)
    # print(body.size)

    element=driver.find_element_by_id("su")
    f = open('/data/study/send_tasks/data/logs/baidu_button3.png','wb')
    f.write(element.screenshot_as_png)
    f.close
    
    print (element.location)
    print (element.size)
    # left=element.location['x']
    # top=element.location['y']
    left = 624
    top = 192
    right=element.location["x"]+element.size['width']
    bottom=element.location['y']+element.size['height']
    im=Image.open('/data/study/send_tasks/data/logs/baidu_button.png')
    im=im.crop((left, top, right, bottom))
    # im=im.crop((500,300,right,bottom))
    im.save('/data/study/send_tasks/data/logs/baidu_button2.png')
    driver.quit()

import requests,json

def check_ip(ip, port):
    result = False
    speed = 0

    url = 'https://httpbin.org/get'

    proxy = {
        'http': 'http://%s:%s' % (ip, port),
        'https': 'https://%s:%s' % (ip, port)
    }
    try:
        begin_time = time.time()
        response = requests.get(url, proxies=proxy, timeout=3)
        content = response.content.decode('utf-8')
        # print(content)
        content = json.loads(content)
        origin_ip = content.get('origin')
        origin_ip_list = origin_ip.split(',')
        if ip in origin_ip_list:
            result = True
            end_time = time.time()
            speed = round(end_time - begin_time, 4)

    except requests.exceptions.ConnectionError as ex:
        # print(str(ex))
        pass
    except requests.exceptions.ReadTimeout as ex:
        # print(str(ex))
        pass
    except Exception as ex:
        # print(str(ex))
        pass

    return {'result': result, 'speed': speed}

def get_ip():
    list_ip = [
        {'ip': '182.52.74.77', 'port': 34825},
        {'ip': '85.214.103.72', 'port': 8080},
        {'ip': '177.71.95.6', 'port': 8080},
        {'ip': '201.158.107.98', 'port': 37748},
        {'ip': '190.152.71.230', 'port': 54354},
        {'ip': '36.66.61.7', 'port': 56232},
        {'ip': '195.158.250.97', 'port': 41582},
        {'ip': '217.24.183.72', 'port': 58739},
        {'ip': '177.10.250.166', 'port': 31783},
        {'ip': '72.250.28.64', 'port': 36851},
        {'ip': '72.250.28.64', 'port': 36851},
        {'ip': '150.95.131.24', 'port': 8181},
        {'ip': '185.36.159.78', 'port': 48608},
        {'ip': '181.47.8.154', 'port': 42230},
        {'ip': '68.183.137.143', 'port': 8080},
        {'ip': '87.252.238.192', 'port': 3128},
        {'ip': '185.67.191.75', 'port': 34531},
        {'ip': '103.6.104.104', 'port': 38898},
        {'ip': '219.89.125.191', 'port': 23500},
        {'ip': '185.160.60.50', 'port': 51996},
        {'ip': '178.216.24.80', 'port': 53281},
        {'ip': '123.132.232.254', 'port': 61017},
        {'ip': '180.250.70.12', 'port': 51540},
        {'ip': '182.52.51.59', 'port': 38238},
        {'ip': '182.53.197.24', 'port': 56383},
        {'ip': '5.135.164.72', 'port': 3128},
        {'ip': '202.77.107.243', 'port': 61917},
        {'ip': '92.253.166.71', 'port': 8080},
        {'ip': '201.131.224.21', 'port': 56200},
        {'ip': '113.190.252.73', 'port': 3128},
        {'ip': '124.105.29.184', 'port': 3128},
        {'ip': '194.88.105.156', 'port': 3128},
        {'ip': '184.105.143.66', 'port': 3128},
        {'ip': '62.149.14.70', 'port': 3128},
        {'ip': '197.81.195.28', 'port': 3128},
        {'ip': '5.10.86.242', 'port': 3128},
        {'ip': '5.129.155.3', 'port': 51390},
        {'ip': '59.125.31.116', 'port': 45965},
        {'ip': '62.210.73.153', 'port': 54321},
        {'ip': '142.93.62.60', 'port': 3128},
        {'ip': '149.202.121.231', 'port': 8082},
        {'ip': '85.204.49.90', 'port': 54321},
        {'ip': '85.204.49.145', 'port': 54321},
        {'ip': '51.15.68.179', 'port': 3128},
        {'ip': '31.184.252.69', 'port': 443},
        {'ip': '82.196.5.200', 'port': 3128},
        {'ip': '85.47.31.179', 'port': 3128},
        {'ip': '54.37.136.149', 'port': 3128},
        {'ip': '190.2.146.80', 'port': 80},
        {'ip': '66.70.136.184', 'port': 3128},
        {'ip': '95.85.25.124', 'port': 4444},
        {'ip': '51.77.147.98', 'port': 3128},
        {'ip': '46.33.98.94', 'port': 8080},
        {'ip': '114.203.208.136', 'port': 3128},
        {'ip': '45.63.54.173', 'port': 8082},
        {'ip': '170.239.180.6', 'port': 3128},
        {'ip': '201.148.127.58', 'port': 31280},
        {'ip': '196.202.153.67', 'port': 3128},
        {'ip': '12.133.183.51', 'port': 8080},
        {'ip': '139.162.1.73', 'port': 3128},
        {'ip': '178.128.83.47', 'port': 8080},
        {'ip': '51.68.112.254', 'port': 3128},
        {'ip': '142.4.204.85', 'port': 3128},
        {'ip': '139.59.198.140', 'port': 3128},
        {'ip': '209.188.21.229', 'port': 3128},
        {'ip': '185.132.133.184', 'port': 8080},
        {'ip': '178.128.99.107', 'port': 8000},
        {'ip': '51.75.109.81', 'port': 3128},
        {'ip': '142.93.44.251', 'port': 3128},
        {'ip': '34.244.2.233', 'port': 8123},
        {'ip': '178.62.210.107', 'port': 8080},
        {'ip': '200.195.28.21', 'port': 3128},
        {'ip': '35.245.208.185', 'port': 3128},
        {'ip': '106.249.44.10', 'port': 3128},
        {'ip': '209.97.191.169', 'port': 3128},
        {'ip': '151.80.197.192', 'port': 80},
        {'ip': '201.64.22.50', 'port': 8081},
        {'ip': '104.248.190.115', 'port': 8080},
        {'ip': '142.93.44.49', 'port': 3128},
        {'ip': '94.177.241.9', 'port': 80},
        {'ip': '142.93.34.9', 'port': 3128},
        {'ip': '142.93.34.9', 'port': 3128},
        {'ip': '192.227.228.186', 'port': 3128},
        {'ip': '204.12.219.162', 'port': 3128},
        {'ip': '142.93.34.45', 'port': 3128},
        {'ip': '51.77.148.201', 'port': 3128},
        {'ip': '212.237.52.148', 'port': 3128},
        {'ip': '68.183.121.154', 'port': 8080},
        {'ip': '35.235.75.244', 'port': 3128},
        {'ip': '54.186.221.7', 'port': 3128},
        {'ip': '132.248.17.90', 'port': 3128},
        {'ip': '68.183.20.148', 'port': 8080},
        {'ip': '209.97.161.88', 'port': 8080},
        {'ip': '80.65.168.166', 'port': 3128},
        {'ip': '170.239.87.17', 'port': 3128},
        {'ip': '191.252.195.210', 'port': 8080},
        {'ip': '36.89.68.98', 'port': 3128},
        {'ip': '95.88.12.230', 'port': 3128},
        {'ip': '1.54.133.242', 'port': 8080},
        {'ip': '1.54.133.251', 'port': 8080},
        {'ip': '1.54.133.248', 'port': 8080},
        {'ip': '195.230.131.210', 'port': 3128},
        {'ip': '178.33.39.70', 'port': 3128},
        {'ip': '144.76.223.58', 'port': 3128},
        {'ip': '176.9.192.215', 'port': 3128},
        {'ip': '207.180.253.113', 'port': 3128},
        {'ip': '5.39.87.211', 'port': 3128},
        {'ip': '202.51.189.195', 'port': 8080},
        {'ip': '83.174.205.134', 'port': 3127},
        {'ip': '212.233.119.42', 'port': 60379},
        {'ip': '195.112.252.180', 'port': 49044},
        {'ip': '193.150.107.150', 'port': 38521},
        {'ip': '194.190.171.214', 'port': 43960},
        {'ip': '195.98.74.141', 'port': 35123},
        {'ip': '213.142.206.146', 'port': 53281},
        {'ip': '212.119.229.18', 'port': 33852},
        {'ip': '194.226.61.18', 'port': 51310},
        {'ip': '194.190.93.136', 'port': 56574},
        {'ip': '213.134.196.12', 'port': 38723},
        {'ip': '195.9.149.6', 'port': 61619},
        {'ip': '194.135.246.178', 'port': 42010},
        {'ip': '62.140.252.72', 'port': 51217},
        {'ip': '62.148.146.3', 'port': 35823},
        {'ip': '80.251.48.215', 'port': 45157},
        {'ip': '84.52.76.91', 'port': 41258},
        {'ip': '46.229.187.169', 'port': 53281},
        {'ip': '87.103.234.116', 'port': 3128},
        {'ip': '95.210.249.150', 'port': 39349},
        {'ip': '222.165.195.75', 'port': 55949},
        {'ip': '93.186.200.200', 'port': 80},
        {'ip': '13.56.2.56', 'port': 8090},
        {'ip': '182.52.132.37', 'port': 8080},
        {'ip': '197.216.2.13', 'port': 8080},
        {'ip': '103.230.182.55', 'port': 8080},
        {'ip': '41.169.11.210', 'port': 45088},
        {'ip': '91.134.221.168', 'port': 80},
        {'ip': '71.179.162.119', 'port': 80},
        {'ip': '96.80.89.69', 'port': 8080},
        {'ip': '45.255.126.33', 'port': 80},
        {'ip': '181.113.7.194', 'port': 57087},
        {'ip': '198.23.143.23', 'port': 8080},
        {'ip': '1.20.217.221', 'port': 8080},
        {'ip': '190.152.6.106', 'port': 49471},
        {'ip': '27.254.220.12', 'port': 8080},
        {'ip': '1.179.198.37', 'port': 8080},
        {'ip': '212.33.197.155', 'port': 8080},
        {'ip': '114.31.6.182', 'port': 8080},
        {'ip': '103.76.253.156', 'port': 3128},
        {'ip': '154.127.32.245', 'port': 60020},
        {'ip': '84.201.195.147', 'port': 30338},
        {'ip': '168.228.6.66', 'port': 8080},
        {'ip': '31.186.101.10', 'port': 3128},
        {'ip': '61.91.232.220', 'port': 8080},
        {'ip': '37.187.116.199', 'port': 80},
        {'ip': '104.207.159.34', 'port': 3128},
        {'ip': '91.137.140.89', 'port': 8082},
        {'ip': '36.66.210.211', 'port': 31437},
        {'ip': '50.242.77.169', 'port': 46996},
        {'ip': '50.242.77.169', 'port': 46996},
        {'ip': '12.133.205.36', 'port': 8080},
        {'ip': '94.131.204.196', 'port': 57952},
        {'ip': '67.205.153.192', 'port': 3128},
        {'ip': '118.97.197.229', 'port': 3128},
        {'ip': '202.138.242.101', 'port': 30487},
        {'ip': '154.68.43.182', 'port': 32755},
        {'ip': '78.47.157.159', 'port': 8888},
        {'ip': '50.232.162.89', 'port': 80},
        {'ip': '216.66.74.83', 'port': 8080},
        {'ip': '74.207.244.241', 'port': 80},
        {'ip': '50.73.137.241', 'port': 3128},
        {'ip': '50.73.137.241', 'port': 3128},
        {'ip': '50.250.144.57', 'port': 36003},
        {'ip': '75.73.52.43', 'port': 80},
        {'ip': '35.163.249.229', 'port': 80},
        {'ip': '98.190.18.187', 'port': 43162},
        {'ip': '137.135.71.199', 'port': 80},
        {'ip': '67.209.121.36', 'port': 80},
        {'ip': '52.38.67.232', 'port': 8978},
        {'ip': '50.197.38.230', 'port': 60724},
        {'ip': '18.214.33.97', 'port': 3128},
        {'ip': '35.198.147.143', 'port': 80},
        {'ip': '205.145.146.34', 'port': 48942},
        {'ip': '31.209.103.79', 'port': 8080},
        {'ip': '46.29.195.210', 'port': 8080},
        {'ip': '46.101.120.137', 'port': 3128},
        {'ip': '35.233.106.236', 'port': 3128},
        {'ip': '165.16.3.54', 'port': 53281},
        {'ip': '77.120.137.143', 'port': 8080},
        {'ip': '187.95.125.66', 'port': 53281}
    ]
    list_ip2 = [
        {'ip': '58.221.227.38', 'port': 3128},
        {'ip': '178.32.5.178', 'port': 3128},
        {'ip': '94.23.154.55', 'port': 3128},
        {'ip': '178.32.5.190', 'port': 3128},
        {'ip': '178.32.5.164', 'port': 3128},
        {'ip': '178.32.5.161', 'port': 3128},
        {'ip': '212.45.5.172', 'port': 3128},
        {'ip': '81.200.26.217', 'port': 3128},
        {'ip': '134.121.64.4', 'port': 3127},
        {'ip': '222.52.99.131', 'port': 8081},
        {'ip': '61.190.28.166', 'port': 8080},
        {'ip': '94.232.65.104', 'port': 3128},
        {'ip': '137.165.1.111', 'port': 3127},
        {'ip': '82.199.113.2', 'port': 3128},
        {'ip': '212.23.70.188', 'port': 3128},
        {'ip': '92.50.152.62', 'port': 3128},
        {'ip': '69.163.96.2', 'port': 8080},
        {'ip': '95.31.2.114', 'port': 3128},
        {'ip': '82.91.170.116', 'port': 8080},
        {'ip': '218.204.240.26', 'port': 8080},
        {'ip': '60.63.79.127', 'port': 8909},
        {'ip': '114.241.36.11', 'port': 8909},
        {'ip': '85.237.46.141', 'port': 8080},
        {'ip': '209.97.203.64', 'port': 8080},
        {'ip': '109.75.111.37', 'port': 3128},
        {'ip': '132.151.1.2', 'port': 8080},
        {'ip': '124.207.97.85', 'port': 8909},
        {'ip': '210.75.203.4', 'port': 8909},
        {'ip': '58.116.45.110', 'port': 8909},
        {'ip': '124.16.152.38', 'port': 8909},
        {'ip': '116.77.12.89', 'port': 8909},
        {'ip': '116.76.13.247', 'port': 8909},
        {'ip': '221.217.8.240', 'port': 8909},
        {'ip': '117.117.145.4', 'port': 8909},
        {'ip': '114.248.25.62', 'port': 8909},
        {'ip': '222.39.72.69', 'port': 8909},
        {'ip': '222.131.42.3', 'port': 8909},
        {'ip': '222.80.31.123', 'port': 8909},
        {'ip': '218.19.119.99', 'port': 8080},
        {'ip': '83.142.228.98', 'port': 8081},
        {'ip': '77.122.203.24', 'port': 54321},
        {'ip': '128.163.142.21', 'port': 3127},
        {'ip': '123.4.106.96', 'port': 8909},
        {'ip': '184.106.170.252', 'port': 8080},
        {'ip': '113.7.210.74', 'port': 8909},
        {'ip': '128.10.19.52', 'port': 3128},
        {'ip': '140.114.79.231', 'port': 3124},
        {'ip': '200.68.91.41', 'port': 8080},
        {'ip': '211.80.61.22', 'port': 8909},
        {'ip': '221.223.123.170', 'port': 8909},
        {'ip': '222.197.169.20', 'port': 8909},
        {'ip': '59.121.33.4', 'port': 8909},
        {'ip': '119.246.29.249', 'port': 8909},
        {'ip': '123.53.79.120', 'port': 8909},
        {'ip': '118.182.61.254', 'port': 8909},
        {'ip': '27.16.228.176', 'port': 8909},
        {'ip': '165.230.49.115', 'port': 3124},
        {'ip': '58.35.194.67', 'port': 8909},
        {'ip': '59.78.62.71', 'port': 8909},
        {'ip': '118.232.109.35', 'port': 8909},
        {'ip': '118.80.120.237', 'port': 8909},
        {'ip': '156.56.250.227', 'port': 3128},
        {'ip': '125.58.152.153', 'port': 8909},
        {'ip': '116.2.38.101', 'port': 8909},
        {'ip': '113.232.27.96', 'port': 8909},
        {'ip': '114.26.53.101', 'port': 8909},
        {'ip': '114.102.254.34', 'port': 8909},
        {'ip': '118.132.65.184', 'port': 8909},
        {'ip': '118.171.130.229', 'port': 8909},
        {'ip': '123.117.144.11', 'port': 8909},
        {'ip': '222.248.104.54', 'port': 8909},
        {'ip': '118.133.229.69', 'port': 8909},
        {'ip': '119.247.162.83', 'port': 8909},
        {'ip': '118.133.132.43', 'port': 8909},
        {'ip': '131.247.2.247', 'port': 3128},
        {'ip': '124.237.67.76', 'port': 8909},
        {'ip': '222.18.176.76', 'port': 8909},
        {'ip': '221.137.113.198', 'port': 8909},
        {'ip': '221.137.123.24', 'port': 8909},
        {'ip': '200.101.82.216', 'port': 3128},
        {'ip': '222.248.110.88', 'port': 8909},
        {'ip': '128.10.19.52', 'port': 3124},
        {'ip': '89.36.26.64', 'port': 8118},
        {'ip': '221.137.223.238', 'port': 8909},
        {'ip': '124.193.216.169', 'port': 8909},
        {'ip': '221.137.242.100', 'port': 8909},
        {'ip': '222.20.47.215', 'port': 8909},
        {'ip': '58.25.35.178', 'port': 8909},
        {'ip': '118.132.203.10', 'port': 8909},
        {'ip': '113.252.100.9', 'port': 8909},
        {'ip': '222.197.168.205', 'port': 8909},
        {'ip': '121.77.95.226', 'port': 8909},
        {'ip': '128.8.126.111', 'port': 3128},
        {'ip': '69.163.96.3', 'port': 8080},
        {'ip': '219.224.38.144', 'port': 8909},
        {'ip': '222.186.105.97', 'port': 8909},
        {'ip': '58.25.28.176', 'port': 8909},
        {'ip': '124.237.123.176', 'port': 8909},
        {'ip': '60.221.206.50', 'port': 8909},
        {'ip': '118.134.9.92', 'port': 8909},
    ]
    list_ip3 = [
        {'ip': '101.109.143.71', 'port': 36127},
        {'ip': '101.109.83.221', 'port': 31860},
        {'ip': '101.132.100.26', 'port': 80},
        {'ip': '101.255.120.170', 'port': 6969},
        {'ip': '101.255.103.209', 'port': 61598},
        {'ip': '101.255.116.113', 'port': 53281},
        {'ip': '101.255.120.161', 'port': 8080},
        {'ip': '101.255.58.225', 'port': 61598},
        {'ip': '101.255.40.18', 'port': 47966},
        {'ip': '101.50.1.2', 'port': 80},
        {'ip': '101.4.136.34', 'port': 81},
        {'ip': '101.4.136.34', 'port': 80},
        {'ip': '101.51.141.119', 'port': 40671},
        {'ip': '101.255.97.74', 'port': 53281},
        {'ip': '101.71.140.5', 'port': 3128},
        {'ip': '102.176.160.70', 'port': 61279},
        {'ip': '102.176.160.84', 'port': 8080},
        {'ip': '102.164.248.46', 'port': 30824},
        {'ip': '102.177.105.34', 'port': 3128},
        {'ip': '102.140.4.14', 'port': 53281},
        {'ip': '102.164.252.24', 'port': 38910},
        {'ip': '102.164.248.35', 'port': 8080},
        {'ip': '103.100.96.174', 'port': 53281},
        {'ip': '102.177.194.26', 'port': 59042},
        {'ip': '103.100.188.50', 'port': 8080},
        {'ip': '103.10.171.132', 'port': 41043},
        {'ip': '103.106.119.154', 'port': 8080},
        {'ip': '103.106.34.10', 'port': 61784},
        {'ip': '103.109.57.226', 'port': 53281},
        {'ip': '103.108.88.158', 'port': 51387},
        {'ip': '103.108.158.139', 'port': 8080},
        {'ip': '103.106.237.103', 'port': 30513},
        {'ip': '103.111.219.170', 'port': 53281},
        {'ip': '103.110.88.64', 'port': 39843},
        {'ip': '103.109.97.22', 'port': 44527},
        {'ip': '103.111.134.85', 'port': 31194},
        {'ip': '103.109.58.245', 'port': 8080},
        {'ip': '103.111.55.142', 'port': 30559},
        {'ip': '103.111.54.26', 'port': 49781},
        {'ip': '103.112.212.221', 'port': 82},
        {'ip': '103.111.54.74', 'port': 8080},
        {'ip': '103.117.230.18', 'port': 42337},
        {'ip': '103.118.169.81', 'port': 47842},
        {'ip': '103.12.246.10', 'port': 8080},
        {'ip': '103.116.37.28', 'port': 44760},
        {'ip': '103.119.247.9', 'port': 51496},
        {'ip': '103.12.163.187', 'port': 53281},
        {'ip': '103.12.151.6', 'port': 50374},
        {'ip': '103.12.246.13', 'port': 8080},
        {'ip': '103.12.246.12', 'port': 8080},
        {'ip': '103.14.235.26', 'port': 8080},
        {'ip': '103.14.45.250', 'port': 8080},
        {'ip': '103.14.36.218', 'port': 8080},
        {'ip': '103.15.60.21', 'port': 8080},
        {'ip': '103.15.226.124', 'port': 80},
        {'ip': '103.16.61.134', 'port': 8080},
        {'ip': '103.18.152.22', 'port': 32967},
        {'ip': '103.1.93.213', 'port': 45648},
        {'ip': '103.16.63.125', 'port': 56752},
        {'ip': '103.194.90.242', 'port': 53682},
        {'ip': '103.194.192.80', 'port': 37227},
        {'ip': '103.194.90.178', 'port': 44487},
        {'ip': '103.197.92.118', 'port': 33465},
        {'ip': '103.198.172.4', 'port': 50820},
        {'ip': '103.197.48.98', 'port': 8080},
        {'ip': '103.198.137.97', 'port': 44533},
        {'ip': '103.203.173.149', 'port': 40160},
        {'ip': '103.199.157.130', 'port': 40052},
        {'ip': '103.205.27.46', 'port': 44286},
        {'ip': '103.206.178.1', 'port': 56357},
        {'ip': '103.209.64.19', 'port': 6666},
        {'ip': '103.210.120.42', 'port': 44700},
        {'ip': '103.216.51.44', 'port': 38900},
        {'ip': '103.216.172.1', 'port': 50031},
        {'ip': '103.216.82.195', 'port': 6666},
        {'ip': '103.216.48.166', 'port': 80},
        {'ip': '103.216.82.214', 'port': 6666},
        {'ip': '103.216.82.209', 'port': 54806},
        {'ip': '103.216.82.29', 'port': 6666},
        {'ip': '103.217.156.31', 'port': 8080},
        {'ip': '103.216.48.83', 'port': 8080},
        {'ip': '103.218.25.220', 'port': 53281},
        {'ip': '103.218.25.52', 'port': 53281},
        {'ip': '103.221.254.125', 'port': 51630},
        {'ip': '103.21.92.254', 'port': 33929},
        {'ip': '103.22.173.230', 'port': 8080},
        {'ip': '103.224.5.5', 'port': 54143},
        {'ip': '103.224.36.193', 'port': 8080},
        {'ip': '103.224.37.129', 'port': 8080},
        {'ip': '103.224.185.217', 'port': 54209},
        {'ip': '103.227.147.142', 'port': 37581},
        {'ip': '103.226.202.54', 'port': 53281},
        {'ip': '103.228.117.244', 'port': 8080},
        {'ip': '103.228.76.46', 'port': 58703},
        {'ip': '103.23.101.58', 'port': 8080},
        {'ip': '103.23.103.203', 'port': 32137},
        {'ip': '103.231.229.90', 'port': 53281},
        {'ip': '103.235.199.72', 'port': 40379},
        {'ip': '103.239.255.170', 'port': 38146},
        {'ip': '103.239.54.17', 'port': 35889}
    ]
    return list_ip3


if __name__ == '__main__':
    def index_generator(L, target):
        for i, num in enumerate(L):
            if num == target:
                yield i

    print(list(index_generator([1, 6, 2, 4, 5, 2, 8, 6, 3, 2], 2)))


    def is_subsequence(a, b):
        b = iter(b)
        print(b)

        gen = (i for i in a)
        print(gen)

        for i in gen:
            print(i)

        # gen = (i for i in b)
        # print(gen)
        #
        # for i in gen:
        #     print(i)

        gen = ((i in b) for i in a)
        print(gen)

        for i in gen:
            print(i)

        return all(((i in b) for i in a))



    print(is_subsequence([1, 3, 5], [1, 2, 3, 4, 5]))
    # print(is_subsequence([1, 4, 3], [1, 2, 3, 4, 5]))

    # ips = get_ip()
    # for ip in ips:
    #     rtn = check_ip(ip.get('ip'), ip.get('port'))
    #     print(rtn)


    # _num =0
    # while True:
    #     _num += 1
    #     print(_num)
    #     time.sleep(1)
    #
    #     if _num >= 5:
    #         break
    #
    # sys.exit(0)
    #
    # print(threading.currentThread().ident)
    # print(threading.currentThread().name)
    #
    # _threads = []
    #
    # num = 1
    # t1 = threading.Thread(target=Count, args=('A', ))
    # t1.setDaemon(True)
    # t1.start()
    # _threads.append(t1)
    #
    # time.sleep(1)
    #
    # t2 = threading.Thread(target=Count, args=('B', ))
    # t2.setDaemon(True)
    # t2.start()
    # _threads.append(t2)
    #
    # for thread in _threads:
    #     thread.join()
    #
    # sys.exit(0)
    #
    #
    #
    #
    #
    # # _begin_time = time.strftime('%Y-%m-%d %H:%M:%S')
    # _begin_time = time.time()
    # print('和讯登录页面 -- begin -- %s' % (time.strftime('%Y-%m-%d %H:%M:%S')))
    #
    # _end_time = time.time()
    # d = _end_time - _begin_time
    # print('和讯登录页面 -- end -- %s -- 耗时：%f' % (time.strftime('%Y-%m-%d %H:%M:%S'), d))
    #
    #
    #
    # _userMobileList = {
    #     '13011110001' : [
    #         {'loginname': '18911418111', 'loginpwd': 'asdf1111', 'platformsn': 'sinablog'},
    #         {'loginname': '18911418111', 'loginpwd': 'asdf1111', 'platformsn': 'hexunblog'}
    #     ],
    #     '13011110002' : [
    #         {'loginname': '18911418111', 'loginpwd': 'asdf1111', 'platformsn': 'sinablog'},
    #         {'loginname': '18911418111', 'loginpwd': 'asdf1111', 'platformsn': 'hexunblog'}
    #     ],
    # }
    #
    # # print(_userMobileList)
    #
    # threads=[]
    #
    # for key, val in _userMobileList.items():
    #     # print(key, val)
    #     t = task(key, val)
    #     t.start()
    #
    #     threads.append(t)
    #
    # for thread in threads:
    #     thread.join()
    #
    # print("All thread done!!!!!")
    #
    # sys.exit(0)


    
