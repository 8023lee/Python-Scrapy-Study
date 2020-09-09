# -*- coding: utf-8 -*-

"""
"""


__author__ = 'lijingang'

import hashlib

from scrapy.exceptions import DropItem

from mscrapy.middlewares.pipeline.mysql import MysqlPipeline


class ScrapyTaskPipeline(MysqlPipeline):

    name = 'ScrapyTaskPipeline'

    def __init__(self):
        super().__init__()

    def process_item(self, item, spider):
        if self.exists(item):
            raise DropItem("Url has exists：%s" % item.get('url'))
        else:
            try:
                sql = self.get_insert_sql(item, spider)
                self.DB.execute(sql)

                self.DB.commit()
            except Exception as ex:
                self.DB.rollback()

            return item

    def exists(self, item):
        """
        :rtype: bool
        """
        sql = "select id from m_scrapy_task where sourceUrlHash = '%s'" % (self.hash(item.get('url')))
        rows = self.DB.execute(sql)
        return rows

    def hash(self, source_url):
        """
        :rtype: str
        """
        sha1 = hashlib.sha1()
        sha1.update(source_url.encode('utf-8'))
        return sha1.hexdigest()

    # 写入数据
    def get_insert_sql(self, item, spider):
        """
        :rtype: str
        """
        sql = "insert into m_scrapy_task(spiderName, title, sourceUrl, sourceUrlHash, category, tag, publishDate, distPlatformSn) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
              % (spider.name, item.get('title'), item.get('url'), self.hash(item.get('url')), item.get('category'), item.get('tag'), item.get('publish_date'), spider.dist_platform_sn)
        return sql
