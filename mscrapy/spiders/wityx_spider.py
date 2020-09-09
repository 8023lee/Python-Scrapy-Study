# -*- coding: utf-8 -*-

"""java面试网内容抓取
"""

__author__ = 'lijingang'


import datetime
import scrapy

from mscrapy.items.cnblogs_list import CnblogsListItem


class WityxSpider(scrapy.Spider):

    name = 'wityx_spider'
    host = 'http://www.wityx.com'

    # 抓取内容发布目的平台
    dist_platform_sn = 'csdn'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'https://www.wityx.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
           'mscrapy.middlewares.pipeline.scrapy_task.ScrapyTaskPipeline': 100,
        }
    }

    def __init__(self, category=None, tag=None, *args, **kwargs):
        super(WityxSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.tag = tag

        self.urls = {
            'javase' : 'http://www.wityx.com/javase/1_0_0.html',
            'javaee' : 'http://www.wityx.com/javaee/1_0_0.html',
            'database' : 'http://www.wityx.com/database/1_0_0.html',
            'web' : 'http://www.wityx.com/web/1_0_0.html',
            'fenxiang' : 'http://www.wityx.com/fenxiang/1_0_0.html'
        }

    def start_requests(self):
        urls = [
            self.urls.get(self.category)
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        search_items = response.css('#normalthread_14').css('tr')

        for item in search_items:
            # 标题
            title = item.css('.xst::text').extract_first()

            # URL searchURL
            url = item.css('.xst::attr(href)').extract_first()

            item = CnblogsListItem()
            item['title'] = title
            item['good'] = 0
            item['comments'] = 0
            item['views'] = 0
            item['url'] = self.host + url
            item['publish_date'] = datetime.datetime.today()
            item['category'] = self.category
            item['tag'] = self.tag

            yield item

        # 是否存在下一页，pager
        pager = response.css('.pg').css('a')
        if pager:
            pager = pager[len(pager) - 2]
            # print(pager)
            if pager.css('::text').extract_first() == '下一页':
                next_url = pager.xpath('@href').extract_first()
                yield scrapy.Request(WityxSpider.host + next_url, callback=self.parse)


if __name__ == '__main__':
    # import os
    # import sys
    #
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    import scrapy.cmdline

    scrapy.cmdline.execute(['scrapy', 'crawl', 'wityx_spider', "-a", "category=fenxiang", "-a" "tag=Java面试宝典"])
