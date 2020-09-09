Scrapy/Selenium/Flask 学习项目
=========================

功能
====
- /mscrapy 目录：Cnblogs、CSDN 博客文章的爬取，部分代理IP的爬取
- /task、/libs目录：CSDN、和讯博客、简书、新浪博客、水木社区的博客/帖子的自动发布
- flask_site目录：使用Flask框架，实现了通过web页面，连接水木社区 telnet，进行简单的积分兑换操作

# 依赖库

1、浏览器驱动：chromedriver

    Mac安装命令：brew cask install chromedriver

2、Python 扩展

    selenium：
        Mac安装命令：pip3 install -U selenium
    pymysql：
        安装命令：pip3 install pymysql
    requests:
        安装命令：pip3 install requests
    bs4:
        安装命令：pip3 install bs4
    pillow:
        安装命令：pip3 install pillow
    markdown:
        安装命令：pip3 install markdown
    Pygments:
        安装命令：pip3 install Pygments
    xlrd:
        安装命令：pip3 install xlrd
    pandas:
        安装命令：pip3 install pandas
    dateutil:
        安装命令：pip3 install python-dateutil
    pyOpenSSL:
        安装命令：pip3 install pyOpenSSL
    Twisted:
        安装命令：下载源码
        tar -xjvf Twisted-18.9.0.tar.bz2
        python setup.py install
    Scrapy:
        安装命令：pip3 install Scrapy  
    Flask 
        安装命令：pip3 install flask
        安装命令：pip3 install blinker
        安装命令：pip3 install jinja2
        安装命令：pip3 install uwsgi
        安装命令：pip3 install flask-sqlalchemy
        
2.1、增加目录到环境变量
- 创建文件 mypkpath.pth，目录
  - Ubuntu：/usr/local/python3.7/lib/python3.7/site-packages
  - Mac：/usr/local/lib/python3.7/site-packages
- 文件内容：项目绝对路径，比如：/data/www/send_tasks/
   
2.2、任务执行命令
- uwsgi启动：nohup uwsgi --ini flask_site/backend/uwsgi.ini > /dev/null 2>&1 &
- 生成SinaBlog任务：nohup python task/post/task_create_trans.py > /dev/null 2>&1 &
- 刷新登录状态（非发布账号）：nohup python task/post/task_refresh_cookie.py -t refresh_nopost -g 5 -r 10 > /dev/null 2>&1 &
- 爬取cnblog列表：scrapy crawl cnblogs_list_spider -a category=java -a tag=java -a begin_date=2018-01-01 -a end_date=2019-03-31
- 爬取cnblog内容：scrapy crawl cnblogs_detail_spider -a pull_num_day=50 -a post_num_day=5
- 更新CSDN浏览数：scrapy crawl csdnblog_detail_spider -a limit_num=100
- 爬取代理IP：nohup python mscrapy/task/main.py -t crawl > /dev/null 2>&1 &
- 验证代理IP：nohup python mscrapy/task/main.py -t check > /dev/null 2>&1 &
- 水木自动回复：nohup python task/post/task_newsmth.py -t comment -g 1 > /dev/null 2>&1 &
- 水木积分爬取：nohup python task/post/task_newsmth.py -t pullscore -g 0 > /dev/null 2>&1 &

- 手动登录简书：python libs/postsdk/jianshusdk.py -t login -u 17611111111 -p xxxxx
- 手动登录简书：python libs/postsdk/jianshusdk.py -t login -u 18511111111 -p xxxxx
- 刷新登录状态：nohup python37 task/post/task_refresh_cookie.py -t refresh > /dev/null 2>&1 &

- 内容截图生成：nohup python37 task/post/task_screenshot.py > /dev/null 2>&1 &
- 自动发布任务：nohup python37 task/post/main.py > /dev/null 2>&1 &


3、配置文件修改

    修改文件 config.ini.example 为 config.ini，并修改文件这种的配置项

4、相关文档
- [开发规范](doc/开发规范.md)
- [Ubuntu线上无界面Selenium安装](doc/Ubuntu线上无界面服务器使用selenium+chrome+headless.md)
