# -*- coding: utf-8 -*-

import re
import scrapy
import datetime

from mscrapy.items.post_task import PostTaskItem
from dbs.model.scrapytask import ScrapyTaskModel


class CnblogsDetailSpider(scrapy.Spider):

    name = 'cnblogs_detail_spider'
    host = 'https://www.cnblogs.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'https://www.cnblogs.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.post_task.PostTaskPipeline': 100,
        }
    }

    def __init__(self, pull_num_day = 50, post_num_day=5, plan_posttime='', *args, **kwargs):
        super(CnblogsDetailSpider, self).__init__(*args, **kwargs)
        # 每次抓取数量
        self.pull_num_day = int(pull_num_day)
        # 每天发布数量
        self.post_num_day = int(post_num_day)
        # 计划发布日期
        self.plan_posttime = plan_posttime

    def start_requests(self):
        # urls = [
        #     'https://www.cnblogs.com/jerry-bk/p/10575286.html',
        #     'https://www.cnblogs.com/yxiaodao/p/10540099.html',
        #     'https://www.cnblogs.com/cocoxu1992/p/10570952.html',
        # ]

        scrapy_task_model = ScrapyTaskModel()
        task_list = scrapy_task_model.get_list_for_process(self.pull_num_day)

        for task in task_list:
            request = scrapy.Request(task['sourceUrl'], self.parse)
            request.meta['scrapy_task'] = task
            yield request #scrapy.Request(task['sourceUrl'], self.parse)

    def parse(self, response):

        self.logger.info('request.url=%s,response.status=%s' % (response.url, response.status))

        scrapy_task = response.meta['scrapy_task']

        item = PostTaskItem()
        item['title'] = ''
        item['content'] = ''
        item['selfCategory'] = scrapy_task['category']
        item['tags'] = scrapy_task['tag']
        item['planPostTime'] = self.plan_posttime
        item['scrapyTaskId'] = scrapy_task['id']
        item['distPlatformSn'] = scrapy_task['distPlatformSn']

        if response.status == 200:
            title = response.css('#cb_post_title_url::text').extract_first()
            if title:
                print('=====' + title + '=====')
            else:
                print('===== 获取文章失败 =====')

            body = response.xpath('//div[@id="cnblogs_post_body"]/*')
            body = "".join(body.extract())
            body = re.sub("<p>(\s+)</p>", "", body)
            body = re.sub("([\r\n]+)", "\r\n", body)
            body = body.replace(u'\u3000', u' ').replace(u'\u00A0', u' ').replace(u'\u0020', u' ').replace(u'\xa0', u' ')
            body += "</br></br>转载：%s" % response.url

            item['title'] = title
            item['content'] = body

        yield item



if __name__ == '__main__':
    # import os
    # import sys
    #
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    import scrapy.cmdline

    scrapy.cmdline.execute(['scrapy', 'crawl', 'cnblogs_detail_spider', "-a", "pull_num_day=10", "-a", "post_num_day=3", "-a", "plan_posttime=2018-04-17"])
