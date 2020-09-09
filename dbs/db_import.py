# -*- coding: utf-8 -*-
"""导入文章数据"""

__author__ = 'lijingang'

import sys
import os
import re
import time
import datetime
import codecs
import markdown

from dbs.db import DB
import libs.config as conf
from libs.log.logger import LoggerFactory


class ImportArticle(object):

    def __init__(self):
        # 数据库操作组件
        self.DB = DB()
        # 日志组件
        self.logger = LoggerFactory.get_logger('db_import')
        pass

    def read_file(self, file_path):
        """
        解析文件内容，取出标题和内容部分

        参数
        ----------------
        file_path：string
            文件绝对路径

        返回值
        ----------------
        dict
            文章标题和内容，如：{'title':'标题', 'content':'内容'}
        """

        f = None
        
        article = None

        try:
            ext = os.path.splitext(file_path)[1]
            if ext not in ['.txt', '.md', '.html', '.htm']:
                raise Exception('文件类型错误，只支持【md、html、htm】')

            # 读取文件内容
            f = codecs.open(file_path, 'r', 'utf-8')
            title = f.readline().strip('\n')
            content = f.read().strip('\n')
            f.close()

            # 对标题特殊字符过滤
            title = re.sub(r'<[^>]+>|#','', title).strip()

            if ext in ['.md', '.txt']:
                # markdown 文件，内容需要转化成html
                content = markdown.markdown(content)

            article = {'title': title, 'content': content}
        except Exception as ex:
            self.logger.info(str(ex) + '：' + file_path)
        finally:
            if f:
                f.close()

        return article

    def get_plan_posttime(self, dict_date, count_per_day):
        """
        获取计划发布日期
        """
        curr_date = dict_date

        # 计算发布日期
        if curr_date['count'] >= count_per_day:
            # 开始下一个日期
            c_date = datetime.datetime.strptime(curr_date['date'], "%Y-%m-%d")
            n_date = (c_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            curr_date['date'] = n_date
            curr_date['count'] = 0

        curr_date['count'] += 1

        return curr_date

    def run(self, file_dir, begin_date, count_per_day):
        """
        导入文章数据到表 m_post_task，m_post_task_platform

        参数
        ----------------
        file_dir: string
            文件目录
        begin_date：string
            开始发布日期，格式：2019-02-21
        num_per_day：int
            每天发布数量
        """
        # 存储从文件解析的内容
        articles = []

        # 初始发布日期
        dict_date = {'date': begin_date, 'count': 0}

        files = os.listdir(file_dir)
        for f in files:
            path = os.path.join(file_dir, f)
            if os.path.isfile(path):
                article = self.read_file(path)
                if article:
                    # 计算发布日期
                    dict_date = self.get_plan_posttime(dict_date, count_per_day)
                    
                    # 计划发布日期
                    article['planPostTime'] = dict_date['date']
                    articles.append(article)

        self.logger.info('需要导入的文章数量：%d' % len(articles))
        
        # 写数据库
        task_data = []
        for article in articles:
            article['slefCategory'] = '亲子阅读'
            article['tags'] = '亲子 互动'
            article['status'] = 'init'

            task_data.append((article['title'], article['slefCategory'], article['tags'], article['content'], article['status'], article['planPostTime']))

        # 写入表 m_post_task
        if task_data:
            self.DB.connect()
            task_sql = "insert into m_post_task(title, selfCategory, tags, content, status, planPostTime) values(%s, %s, %s, %s, %s, %s)"
            self.DB.executemany(task_sql, task_data)
            self.DB.commit()
            self.DB.close()

            self.logger.info('成功导入的文章数量：%d' % len(task_data))

        # 写入表 m_post_task_platform
        self.DB.connect()
        try:
            # 查询所有账户
            sql = 'select id, platformSn from m_platform_account where isEnable = 1'
            accounts = self.DB.fetchall(sql)

            # 查询所有未处理 post_task
            sql = 'select id from m_post_task where status = "init"'
            tasks = self.DB.fetchall(sql)

            data = []
            task_ids = ''
            for task in tasks:
                # 循环账户
                for account in accounts:
                    # 任务和账户关系数据是否存在
                    sql = "select id, status from m_post_task_platform where taskId = %d and accountId = %d" % (task['id'], account['id'])
                    task_platform = self.DB.fetchone(sql)

                    if task_platform is None:
                        data.append((task['id'], account['platformSn'], account['id'], 'init'))
                        task_ids += ('%s,' % task['id'])

            # 需要更新任务ID
            task_ids = task_ids.rstrip(',')

            self.logger.info('需要导入的任务数量：%d' % len(data))

            sql = 'insert into m_post_task_platform(taskId, platformSn, accountId, status) values(%s, %s, %s, %s)'
            update_sql = 'update m_post_task set status = "success" where id in (%s)' % (task_ids)
            if data:
                self.DB.executemany(sql, data)
                self.DB.execute(update_sql)
                self.DB.commit()

                self.logger.info('成功导入的任务数量：%d' % len(data))
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('写入表[m_post_task_platform]，更新表[m_post_task]状态，异常：%s', str(ex))
        finally:
            self.DB.close()
        

class CreateArticle(object):
    def __init__(self):
        # 数据库操作组件
        self.DB = DB()
        # 日志组件
        self.logger = LoggerFactory.get_logger('create-article')

    def write_file(self, file_path, content):
        ret = False
        f = None

        try:
            # 写入文件内容
            f = codecs.open(file_path, 'w', 'utf-8')
            f.write(content)
            f.close()

            ret = True
        except Exception as ex:
            self.logger.info(str(ex) + '：' + file_path)
        finally:
            if f:
                f.close()

        return ret

    def run(self, category, count_per_file):
        path = '/data/study/send_tasks/data/logs/md/20190423'

        self.DB.connect()
        try:
            sql = "select * from m_post_task where  status = 'success'  and selfCategory = '%s' order by id asc" % category
            tasks = self.DB.fetchall(sql)
            file_content = ''
            file_count = 0
            task_count = 0
            for task in tasks:
                title = "#### %s" % task.get('title')
                content = task.get('content')

                file_content += '%s\r\n%s\r\n\r\n' % (title, content)

                file_count += 1
                task_count += 1
                if file_count >= count_per_file:
                    # self.write_file('%s/%s-%d.txt' % (path, task.get('tags'), task_count // count_per_file), file_content)
                    self.write_file('%s/%s-%d（%s).txt' % (path, task.get('tags'), task_count // count_per_file, task.get('title')), file_content)
                    file_content = ''
                    file_count = 0

            if file_count:
                # self.write_file('%s/%s-%d.txt' % (path, task.get('tags'), task_count // count_per_file + 1), file_content)
                self.write_file('%s/%s-%d（%s).txt' % (path, task.get('tags'), task_count // count_per_file, task.get('title')),  file_content)
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception(str(ex))
        finally:
            self.DB.close()



if __name__ == '__main__':
    # argv = sys.argv
    # print(argv)
    #
    # if len(argv) != 4:
    #     print('argv error')
    #
    # path = argv[1]
    # begin_date = argv[2]
    # count_per_day = int(argv[3])

    # path  = '/data/study/send_tasks/data/logs/md/201902/'
    # begin_date = '2019-02-23'
    # count_per_day = 3

    # importArticle = ImportArticle()
    # importArticle.run(path, begin_date, count_per_day)

    createArticle = CreateArticle()
    createArticle.run('fenxiang', 1)
