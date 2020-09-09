# -*- coding: utf-8 -*-

import re
import scrapy


from mscrapy.items.post_task import PostTaskItem
from dbs.model.scrapytask import ScrapyTaskModel


class WityxDetailSpider(scrapy.Spider):
    name = 'wityx_spider_detail'
    host = 'http://www.wityx.com'

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
            'mscrapy.middlewares.pipeline.wityx_detail_pipeline.WityxDetailPipeline': 100,
        }
    }

    def __init__(self, pull_num_day = 50, plan_posttime='', *args, **kwargs):
        super(WityxDetailSpider, self).__init__(*args, **kwargs)
        # 每次抓取数量
        self.pull_num_day = int(pull_num_day)
        # 计划发布日期
        self.plan_posttime = plan_posttime

    def start_requests(self):
        # urls = [
        #     'https://www.cnblogs.com/jerry-bk/p/10575286.html',
        #     'https://www.cnblogs.com/yxiaodao/p/10540099.html',
        #     'https://www.cnblogs.com/cocoxu1992/p/10570952.html',
        # ]

        scrapy_task_model = ScrapyTaskModel()
        task_list = scrapy_task_model.get_list_for_process(self.pull_num_day, 'wityx_spider')

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
            title = response.css('#thread_subject::text').extract_first()
            if title:
                print('=====' + title + '=====')
            else:
                print('===== 获取文章失败 =====')

            body = response.xpath('//td[@class="t_f"]/*')
            body = "".join(body.extract())
            body = re.sub("<p>(\s+)</p>", "", body)
            body = re.sub("([\r\n]+)", "\r\n", body)
            body = body.replace(u'\u3000', u' ').replace(u'\u00A0', u' ').replace(u'\u0020', u' ').replace(u'\xa0', u' ')

            item['title'] = title
            item['content'] = body

        yield item



if __name__ == '__main__':
    # import os
    # import sys
    #
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    import scrapy.cmdline

    scrapy.cmdline.execute(['scrapy', 'crawl', 'wityx_spider_detail', "-a", "pull_num_day=1000", "-a", "plan_posttime=2019-04-22"])
