# -*- coding: utf-8 -*-
import re
import scrapy

from mscrapy.items.cnblogs_list import CnblogsListItem


class CnblogsListSpider(scrapy.Spider):

    name = 'cnblogs_list_spider'
    host = 'https://zzk.cnblogs.com'

    # 抓取内容发布目的平台
    dist_platform_sn = 'csdn'

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
           'mscrapy.middlewares.pipeline.scrapy_task.ScrapyTaskPipeline': 100,
        }
    }

    def __init__(self, category=None, tag=None, begin_date=None, end_date=None, *args, **kwargs):
        super(CnblogsListSpider, self).__init__(*args, **kwargs)
        self.category = category
        self.tag = tag
        self.begin_date = begin_date
        self.end_date = end_date

    def start_requests(self):
        urls = [
            'https://zzk.cnblogs.com/s/blogpost?Keywords=' + self.tag + '&datetimerange=Customer&from=' + self.begin_date + '&to=' + self.end_date + '&pageindex=1',
        ]

        cookies = {
            'ZzkNoRobotCookie': 'CfDJ8JcopKY7yQlPr3eegllP76P8SEB1_ey1g4giEpe4x2kuFg38AyS_foORbngme5BnWtJ0QgPti-H5h1x0c3hSro87M2SO8xORGSQBuRXa63LGVsa7s2NQsfUUN8tMxcPKoQ'
        }

        for url in urls:
            yield scrapy.Request(url=url, cookies=cookies, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        search_items = response.css('#searchResult').css('.forflow').css('.searchItem')
        for item in search_items:
            # 标题
            title = item.css('h3').css('a').extract_first()
            title = ''.join(re.compile('>(.*?)<').findall(title))

            # 推荐 searchItemInfo-good
            good = item.css('.searchItemInfo-good::text').extract_first()

            # 评论 searchItemInfo-comments
            comments = item.css('.searchItemInfo-comments::text').extract_first()

            # 浏览 searchItemInfo-views
            views = item.css('.searchItemInfo-views::text').extract_first()

            # 发布日期 searchItemInfo-publishDate
            publish_date = item.css('.searchItemInfo-publishDate::text').extract_first()

            # URL searchURL
            url = item.css('.searchURL::text').extract_first()

            item = CnblogsListItem()
            item['title'] = title
            item['good'] = good
            item['comments'] = comments
            item['views'] = views
            item['url'] = url
            item['publish_date'] = publish_date
            item['category'] = self.category
            item['tag'] = self.tag


            yield item

        # 是否存在下一页，pager
        pager = response.css('#searchResult').css('.forflow').css('.pager').css('a')
        if pager:
            pager = pager[len(pager) - 1]
            # print(pager)
            if pager.css('::text').extract_first() == 'Next >':
                next_url = pager.xpath('@href').extract_first()
                yield scrapy.Request(CnblogsListSpider.host + next_url, callback=self.parse)


if __name__ == '__main__':
    # import os
    # import sys
    #
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    import scrapy.cmdline

    scrapy.cmdline.execute(['scrapy', 'crawl', 'cnblogs_list_spider', "-a", "category=Spring", "-a" "tag=Spring", "-a", "begin_date=2019-04-18", "-a", "end_date=2019-04-18"])
