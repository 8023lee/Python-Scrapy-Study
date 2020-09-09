# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import hashlib
import scrapy


class CnblogsListItem(scrapy.Item):
    # define the fields for your item here like:
    # 标题
    title = scrapy.Field()
    # 推荐数
    good = scrapy.Field()
    # 评论数
    comments = scrapy.Field()
    # 浏览数
    views = scrapy.Field()
    # 详情页面URL
    url = scrapy.Field()
    # 发布日期
    publish_date = scrapy.Field()
    # 分类
    category = scrapy.Field()
    # 标签
    tag = scrapy.Field()



