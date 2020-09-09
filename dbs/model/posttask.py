# -*- coding: utf-8 -*-
"""表 m_post_task 的model类"""

__author__ = 'lijingang'

import sys
import time

from libs.log.logger import LoggerFactory
from dbs.model.basemodel import BaseModel

class PostTask(BaseModel):
    STATUS_INIT = 'init'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'

    def __init__(self):
        super().__init__()

    def get_last_post_date(self):
        """获取最后发布日期

        :rtype: object
        """
        data = None
        try:
            sql = "select date_format(planPostTime, '%Y-%m-%d') as plan_date, count(*) as post_count " \
                  "from m_post_task " \
                  "group by planPostTime " \
                  "order by planPostTime desc limit 1"

            self.DB.connect()
            data = self.DB.fetchone(sql)
        except Exception as ex:
            self.logger.exception('获取最后发布日期，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data


if __name__ == '__main__':
    logger = LoggerFactory.get_logger()
    logger.info('==== posttask runing start ====')

    postTask = PostTask()
    data  = postTask.get_last_post_date()
    print(data)

    logger.info('==== posttask runing end ====')
