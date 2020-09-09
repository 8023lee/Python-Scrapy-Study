# -*- coding: utf-8 -*-

"""
"""


__author__ = 'lijingang'

import datetime

import pymysql

from mscrapy.middlewares.pipeline.mysql import MysqlPipeline


class WityxDetailPipeline(MysqlPipeline):

    name = 'WityxDetailPipeline'

    def __init__(self):
        super().__init__()
        self.plan_post_date = {'plan_date': datetime.date.today().strftime('%Y-%m-%d'), 'post_count': 0}


    def open_spider(self, spider):
        super().open_spider(spider)
        print('=====open_spider=======')
        # # 获取最后一条任务的预计发布日期
        # last_date = PostTaskModel().get_last_post_date()
        # if last_date and last_date.get('plan_date') >= datetime.date.today().strftime('%Y-%m-%d'):
        #     self.plan_post_date = last_date

    # def __calculate_plan_postdate(self, post_num_day):
    #     """计算计划发布日期
    #
    #     :rtype: object
    #     """
    #     if self.plan_post_date['post_count'] >= post_num_day:
    #         # 开始下一个日期
    #         c_date = datetime.datetime.strptime(self.plan_post_date['plan_date'], "%Y-%m-%d")
    #         n_date = (c_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    #         self.plan_post_date['plan_date'] = n_date
    #         self.plan_post_date['post_count'] = 1
    #     else:
    #         self.plan_post_date['post_count'] += 1
    #
    #     return self.plan_post_date['plan_date']

    def process_item(self, item, spider):
        try:
            # 写入表 m_post_task
            if item['title']:
                # 查询所有账户
                sn_list = item['distPlatformSn'].split(',')
                str_sn = ','.join(["'%s'" % item for item in sn_list])
                sql = "select id, platformSn from m_platform_account where isEnable = 0 and isPost = 1 and platformSn in (%s) order by id desc" % str_sn
                accounts = self.DB.fetchall(sql)
                if not accounts:
                    raise Exception('抓取任务[%s]失败，没有匹配平台[%s]的账户。' % (item['title'], spider.dist_platform_sn))

                # 计划发布日期
                # plan_post_date = self.__calculate_plan_postdate(spider.post_num_day * len(accounts))
                if item['planPostTime']:
                    self.plan_post_date = item['planPostTime']

                # 转义字符
                item['content'] = pymysql.escape_string(item['content'])
                task_data = (item['title'], item['selfCategory'], item['tags'], item['content'], 'success', self.plan_post_date)

                # 写入表 m_post_task
                task_sql = "insert into m_post_task(title, selfCategory, tags, content, status, planPostTime) values('%s', '%s', '%s', '%s', '%s', '%s')" % task_data
                affected_rows = self.DB.execute(task_sql)
                if affected_rows == 0:
                    raise Exception('抓取任务[%s]失败，写入表[m_post_task]异常。' % item['title'])

                update_sql_2 = 'update m_scrapy_task set status = "success" where id = %d' % (item['scrapyTaskId'])
                self.DB.execute(update_sql_2)
                self.logger.info('抓取任务[%s]成功。' % item['title'])

        except Exception as ex:
            self.DB.rollback()
            self.logger.exception(str(ex))

        finally:
            update_sql_2 = 'update m_scrapy_task set status = "success" where id = %d' % (item['scrapyTaskId'])
            self.DB.execute(update_sql_2)
            self.DB.commit()

        return item


