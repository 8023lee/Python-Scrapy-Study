# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

import hashlib
import scrapy


class ProxyIpItem(scrapy.Item):
    # define the fields for your item here like:
    # IP
    ip = scrapy.Field()
    # 端口
    port = scrapy.Field()
    # 协议
    protocol = scrapy.Field()
    # 响应速度
    speed = scrapy.Field()
    # 最后验证时间
    last_checked = scrapy.Field()
    # 国家
    country = scrapy.Field()
    # 网站
    web_site = scrapy.Field()

    def get_ip_hash(self):
        return self.__hash(self.get('ip') + ":" + self.get('port'))

    def __hash(self, source):
        """
        :rtype: str
        """
        sha1 = hashlib.sha1()
        sha1.update(source.encode('utf-8'))
        return sha1.hexdigest()
