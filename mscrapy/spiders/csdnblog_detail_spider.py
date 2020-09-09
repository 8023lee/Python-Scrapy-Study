# -*- coding: utf-8 -*-

import re
import scrapy
import datetime

from mscrapy.items.posttask_platform_item import PostTaskPlatformItem
from dbs.model.posttask_platform import PostTaskPlatform


class CsdnblogDetailSpider(scrapy.Spider):

    name = 'csdnblog_detail_spider'
    host = 'https://blog.csdn.net'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'https://blog.csdn.net',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.posttask_platform_pipeline.PostTaskPlatformPipeline': 100,
        }
    }

    def __init__(self, limit_num, *args, **kwargs):
        super(CsdnblogDetailSpider, self).__init__(*args, **kwargs)
        # 每天发布数量
        self.limit_num = int(limit_num)

    def start_requests(self):
        # urls = [
        #     'https://blog.csdn.net/kuangdashi/article/details/88949823',
        # ]

        posttask_platform = PostTaskPlatform()
        task_list = posttask_platform.get_list_for_update_viewcount(self.limit_num)

        for task in task_list:
            request = scrapy.Request(task['detailUrl'], self.parse)
            request.meta['posttask_platform'] = task
            yield request

    def parse(self, response):
        self.logger.info('request.url=%s,response.status=%s' % (response.url, response.status))

        posttask_platform = response.meta['posttask_platform']

        item = PostTaskPlatformItem()
        item['viewCount'] = 0
        item['id'] = posttask_platform['id']

        if response.status == 200:
            view_count = response.css('.read-count::text').extract_first().replace('阅读数：','')

            item['viewCount'] = view_count

        yield item



if __name__ == '__main__':
    # import os
    # import sys
    #
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    import scrapy.cmdline

    scrapy.cmdline.execute(['scrapy', 'crawl', 'csdnblog_detail_spider', "-a", "limit_num=2"])
