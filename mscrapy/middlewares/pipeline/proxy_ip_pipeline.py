# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

import time

from scrapy.exceptions import DropItem

from mscrapy.middlewares.pipeline.mysql import MysqlPipeline


class ProxyIpPipeline(MysqlPipeline):

    name = 'ScrapyTaskPipeline'

    def __init__(self):
        super().__init__()

    def process_item(self, item, spider):
        # print(item.get_ip_hash())
        # return item
        if self.exists(item):
            print('%s===exists===' % item.get('ip'))
            raise DropItem("Ip has exists：%s" % item.get('ip'))
        else:
            try:
                sql = self.get_insert_sql(item, spider)
                # print(sql)
                eff_rows = self.DB.execute(sql)

                self.DB.commit()
            except Exception as ex:
                print(str(ex))
                self.DB.rollback()

            return item

    def exists(self, item):
        """
        :rtype: bool
        """
        sql = "select id from m_proxy_ip where ipHash = '%s'" % item.get_ip_hash()
        rows = self.DB.execute(sql)
        return rows

    # 写入数据
    def get_insert_sql(self, item, spider):
        """
        :rtype: str
        """
        sql = "insert into m_proxy_ip(ip, port, ipHash, protocol, speed, last_checked_time, country, web_site) values('%s', %s, '%s', '%s', '%s', '%s', '%s', '%s')" \
              % (item.get('ip'), item.get('port'), item.get_ip_hash(), item.get('protocol'), item.get('speed'), item.get('last_checked'), item.get('country'), item.get('web_site'))
        return sql
