### 一、安装 selenium
    pip install selenium


### 二、安装 chromdriver
    进入： 淘宝镜像源：https://npm.taobao.org/  下载 chromdriver

    一般都是下载当时最新版本  现在我下载的是 2.42 。 
    可以查看 notes.txt 文件，看chrome 和ChromDriver 两者相对应的兼容版本
    下载  chromedriver_linux64.zip
    解压 得到 chromedriver文件
    远程 把chromedirver 文件放到线上服务器 /usr/bin/ 下。
 
### 三、Ubuntu线上服务器 安装chrome（重点）
    命令行  执行下面的命令
    sudo apt-get install libxss1 libappindicator1 libindicator7
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome*.deb    # Might show "errors", fixed by next line
    sudo apt-get install -f
    google-chrome --version      # 查看版本

    如果中文显示乱码，执行下面的字体安装命令：
    sudo apt-get install ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy

### 四.测试
    写一个 test.py  测试

    from selenium import webdriver
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox') # 这个配置很重要
    client = webdriver.Chrome(chrome_options=chrome_options, executable_path='/home/chromedriver')    # 如果没有把chromedriver加入到PATH中，就需要指明路径
    
    client.get("https://www.baidu.com")
    print (client.page_source.encode('utf-8'))
    
    client.quit()

### 注意
    如果没有下面这个配置
    options.add_argument('--no-sandbox')

    会出现下面  报错信息
    selenium.common.exceptions.WebDriverException: Message: unknown error: DevToolsActivePort file doesn't exist