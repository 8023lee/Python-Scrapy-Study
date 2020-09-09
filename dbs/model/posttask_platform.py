# -*- coding: utf-8 -*-
"""表 m_post_task_platform 的model类"""

__author__ = 'lijingang'


import time
import random

from libs.log.logger import LoggerFactory
from dbs.model.basemodel import BaseModel


class PostTaskPlatform(BaseModel):

    STATUS_INIT = 'init'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'

    def __init__(self):
        super().__init__()

    def get_posttask_platform(self, account_id):
        """ 获取需要处理的任务"""

        post_task = None

        self.DB.connect()
        try:
            sql = "select b.id, b.platformSn, b.accountId, b.refUrl, a.url, a.imgUrl, a.title, a.selfCategory, a.tags, a.content \
                    from m_post_task as a \
                        inner join m_post_task_platform as b on a.id = b.taskId \
                    where a.imgUrl != '' and b.accountId = %d and b.status in ('%s', '%s') and a.planPostTime < '%s' \
                    order by b.updateTime asc \
                    limit 1" % (account_id, PostTaskPlatform.STATUS_INIT, PostTaskPlatform.STATUS_FAIL, time.strftime('%Y-%m-%d %H:%M:%S'))
            
            self.logger.info('获取待处理任务，account_id = %d' % account_id)
            # self.logger.info('获取待处理任务，sql：' + sql)

            post_task = self.DB.fetchone(sql)
        except Exception as ex:
            self.logger.exception('获取待处理任务，account_id = %d，异常：%s' % (account_id, str(ex)))
        finally:
            self.DB.close()

        return post_task

    def update_posttask_platform(self, posttask_platform_id, articleUrl):
        """ 更新 m_post_task_platform 表的状态

        参数
        ----------------
        posttask_platform_id ：发布的文章任务ID
        articleUrl ：文章详情页面url
        """

        affected_rows = 0

        self.DB.connect()

        try:
            # 更新 m_post_task_platform
            status = PostTaskPlatform.STATUS_FAIL
            if articleUrl:
                status = PostTaskPlatform.STATUS_SUCCESS
            
            sql = "update m_post_task_platform set detailUrl = '%s', status = '%s', lastViewTime = '%s', updateTime = '%s' where id = %d " % (articleUrl, status, time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), posttask_platform_id)

            self.logger.info('更新表[m_post_task_platform]状态，id = %d, detailUrl = %s' % (posttask_platform_id, articleUrl))
            # self.logger.info('更新表[m_post_task_platform]状态，sql：%s', sql)
            
            affected_rows = self.DB.execute(sql)

            self.DB.commit()
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('更新表[m_post_task_platform]状态，异常：%s', str(ex))
        finally:
            self.DB.close()

        return affected_rows

    def update(self, update_data):
        """ 更新 m_post_task_platform 表的数据

        参数
        ----------------
        update_data ：dict 更新的数据，已字段名称为key的字典
        """

        affected_rows = 0

        self.DB.connect()

        try:
            up_where = 'id=%d' % update_data.pop("id")
            up_set = ','.join(["%s='%s'" % (key, val) for key, val in update_data.items()])
            if up_where and up_set:
                sql = "update m_post_task_platform set %s where %s" % (up_set, up_where)

                self.logger.info('更新表[m_post_task_platform]，sql：%s', sql)

                affected_rows = self.DB.execute(sql)

                self.DB.commit()
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('更新表[m_post_task_platform]，异常：%s', str(ex))
        finally:
            self.DB.close()

        return affected_rows

    def get_list_for_update_viewcount(self, limit_num):
        """获取需要更新浏览数的任务

        :rtype: list，任务数组
        """
        return self.__get_all("platformSn='csdn' and status='success'", "lastViewTime asc limit %d" % (limit_num))

    def get_random_task(self, random_num = 10):
        data = None

        try:
            sql = "select b.id, b.title, min(a.detailUrl) as detailUrl " \
                  "from m_post_task_platform as a  " \
                  "     inner join m_post_task as b on a.taskId = b.id " \
                  "where a.platformSn='csdn' and a.status ='success' " \
                  "group by b.id, b.title"

            self.DB.connect()
            data = self.DB.fetchall(sql)

            if data:
                data = random.sample(data, random_num)
        except Exception as ex:
            self.logger.exception('获取推荐数据，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

    def __get_all(self, where=None, order_by=None):
        data = None

        try:
            sql = "select * from m_post_task_platform where 1=1 "
            if where:
                sql += " and %s" % (where)
            if order_by:
                sql += " order by %s" % (order_by)

            self.DB.connect()
            data = self.DB.fetchall(sql)
        except Exception as ex:
            self.logger.exception('获取[m_post_task_platform]表数据，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

if __name__ == '__main__':
    # 日志组件
    logger = LoggerFactory.get_logger()
    logger.info('==== posttask_platform runing start ====')

    from dbs.model.account import Account as AccountModel

    accountModel = AccountModel()
    accounts = accountModel.get_post_accounts()

    porttask_platform = PostTaskPlatform()
    # random_tasks = porttask_platform.get_random_task(1)

    for key, val in accounts.items():
        for v in val:
            task = porttask_platform.get_posttask_platform(v['id'])
            # print(task)
            porttask_platform.update_posttask_platform(task['id'], 'https://www.baidu.com/')

    logger.info('==== posttask_platform runing end ====')
