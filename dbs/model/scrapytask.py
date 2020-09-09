# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

from libs.log.logger import LoggerFactory
from dbs.model.basemodel import BaseModel

class ScrapyTaskModel(BaseModel):
    STATUS_INIT = 'init'
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'


    def __init__(self):
        super().__init__()

    def __get_list(self, where = None, order_by = None):
        self.DB.connect()
        try:
            sql = "select * from m_scrapy_task where 1=1 "
            if where:
                sql += " and %s" % where
            if order_by:
                sql += " order by %s" % order_by

            self.logger.info('获取[m_scrapy_task]，sql：' + sql)

            task_list = self.DB.fetchall(sql)
        except Exception as ex:
            self.logger.exception('获取[m_scrapy_task]，异常：%s' % (str(ex)))
        finally:
            self.DB.close()

        return task_list

    def get_list_for_process(self, limit_num = 50, spider_name = 'cnblogs_list_spider'):
        """
        获取待处理任务

        :param limit_num: 查询数量
        :return: 待处理任务数组
        """
        where = "status in ('%s','%s')" % (ScrapyTaskModel.STATUS_INIT, ScrapyTaskModel.STATUS_FAIL)
        if spider_name:
            where += " and spiderName = '%s'" % spider_name
        order_by = "updateTime asc limit %d" % limit_num

        return self.__get_list(where=where, order_by=order_by)


if __name__ == '__main__':
    # 日志组件
    logger = LoggerFactory.get_logger()
    logger.info('==== ScrapyTask runing start ====')

    scrapy_task_model = ScrapyTaskModel()
    task_list = scrapy_task_model.get_list_for_process(2)

    print(task_list)

    logger.info('==== ScrapyTask runing end ====')
