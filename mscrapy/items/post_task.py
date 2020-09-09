# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PostTaskItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    selfCategory = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    planPostTime = scrapy.Field()
    scrapyTaskId = scrapy.Field()
    distPlatformSn = scrapy.Field()


