# -*- coding: utf-8 -*-

"""
爬取免费代理IP
"""

import re
import time
import datetime
import scrapy

from mscrapy.items.proxy_ip import ProxyIpItem


class DinkSpider(scrapy.Spider):
    name = 'dink_spider'
    host = 'http://www.mrhinkydink.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.mrhinkydink.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(DinkSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = [
            'http://www.mrhinkydink.com/proxies.htm',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        search_items = response.css('td.text tr.text')
        for item in search_items:
            ip = item.css('td::text')[0].extract()
            port = item.css('td::text')[1].extract()
            speed = item.css('td::text')[3].extract()
            country = item.css('td::text')[4].extract()
            last_checked = item.css('td::text')[7].extract().strip().replace('\xa0',' ').replace('‑','-')

            # print(ip, port, speed, last_checked)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = ''
            item['speed'] = speed.replace('sec.', '').strip()
            item['last_checked'] = last_checked
            item['country'] = country
            item['web_site'] = self.host

            yield item

        # 是否存在下一页，pager
        url = response.url
        page_index = re.findall(r"proxies(.+?).htm", response.url)
        if page_index:
            page_index = int(page_index[0])
        else:
            page_index = 1

        td_h = response.css('td.text td.horizontal')
        pager = (td_h[len(td_h)-1]).css('a')
        if pager and len(pager) > (page_index - 1):
            # print(pager)
            next_url = DinkSpider.host + '/proxies%d.htm' % (page_index + 1)
            yield scrapy.Request(next_url, callback=self.parse)


class KuaidailiSpider(scrapy.Spider):
    name = 'kuaidaili_spider'
    host = 'http://www.kuaidaili.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.kuaidaili.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(KuaidailiSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['https://www.kuaidaili.com/free/inha/%s/' % i for i in range(1, 6)] + \
               ['https://www.kuaidaili.com/free/intr/%s/' % i for i in range(1, 6)]

        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(1)

    def parse(self, response):
        print(response.status)
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('.table.table-bordered.table-striped').css('tbody tr')
        for item in search_items:
            ip = item.css('td::text')[0].extract()
            port = item.css('td::text')[1].extract()
            protocol = item.css('td::text')[3].extract()
            speed = item.css('td::text')[5].extract().replace('秒','')
            last_checked = item.css('td::text')[6].extract()

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class Data5uSpider(scrapy.Spider):
    name = 'data5u_spider'
    host = 'http://www.data5u.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.data5u.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(Data5uSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = [
            # 'http://www.data5u.com/free/index.shtml',
            # 'http://www.data5u.com/free/gngn/index.shtml',
            # 'http://www.data5u.com/free/gnpt/index.shtml'
            'http://www.data5u.com/'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('ul.l2')
        for item in search_items:
            ip = item.css('li::text')[0].extract()
            port = item.css('li::text')[1].extract()
            protocol = item.css('li::text')[3].extract()
            speed = item.css('li::text')[7].extract().replace(' 秒', '')
            last_checked = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #item.css('li::text')[8].extract()

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class TxtSpider(scrapy.Spider):
    name = 'txt_spider'
    host = 'http://ab57.ru'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            # 'referer': 'http://ab57.ru',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(TxtSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = [
            'http://ab57.ru/downloads/proxyold.txt',
            # 'http://www.proxylists.net/http_highanon.txt',
            # 'https://www.rmccurdy.com/scripts/proxy/good.txt'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        ip_list = response.body.decode('utf-8').replace('\r', '').split('\n')
        # print(ip_list)
        for p_ip in ip_list:
            ip_info = p_ip.split(':')
            if ip_info[0] and ip_info[1]:
                ip = ip_info[0]
                port = ip_info[1]
                protocol = ''
                speed = 0
                last_checked = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # print(ip + ',' + response.url)

                item = ProxyIpItem()
                item['ip'] = ip
                item['port'] = port
                item['protocol'] = protocol
                item['speed'] = speed
                item['last_checked'] = last_checked
                item['country'] = 'china'
                item['web_site'] = response.url

                yield item


class XicidailiSpider(scrapy.Spider):
    name = 'xicidaili_spider'
    host = 'https://www.xicidaili.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'https://www.xicidaili.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(XicidailiSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['https://www.xicidaili.com/nn/%s' % i for i in range(1, 6)] + \
               ['https://www.xicidaili.com/wn/%s' % i for i in range(1, 6)] + \
               ['https://www.xicidaili.com/wt/%s' % i for i in range(1, 6)] + \
               ['https://www.xicidaili.com/nt/%s' % i for i in range(1, 6)]

        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('table#ip_list').css('tr[class]')
        for item in search_items:
            ip = item.css('td')[1].css('::text')[0].extract()
            port = item.css('td')[2].css('::text')[0].extract()
            protocol = item.css('td')[5].css('::text')[0].extract()
            speed = item.css('td')[6].css('div::attr(title)')[0].extract().replace('秒','')
            last_checked = item.css('td')[9].css('::text')[0].extract()

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class Ip3366Spider(scrapy.Spider):
    name = 'ip3366_spider'
    host = 'http://www.ip3366.net'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.ip3366.net',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(Ip3366Spider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['http://www.ip3366.net/free/?stype=1&page=%s' % i for i in range(1, 8)] + \
               ['http://www.ip3366.net/free/?stype=2&page=%s' % i for i in range(1, 8)]
        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('table.table.table-bordered.table-striped').css('tbody tr')
        for item in search_items:
            ip = item.css('td::text')[0].extract()
            port = item.css('td::text')[1].extract()
            protocol = item.css('td::text')[3].extract()
            speed = item.css('td::text')[5].extract().replace('秒','')
            last_checked = item.css('td::text')[6].extract()

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class FeiyiproxySpider(scrapy.Spider):
    name = 'feiyiproxy_spider'
    host = 'http://www.feiyiproxy.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.feiyiproxy.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(FeiyiproxySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['http://www.feiyiproxy.com/?page_id=1457']
        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('div.et_pb_code.et_pb_module.et_pb_code_1').css('table tr')
        search_items.pop(0)

        for item in search_items:
            ip = item.css('td::text')[0].extract()
            port = item.css('td::text')[1].extract()
            protocol = item.css('td::text')[3].extract()
            speed = item.css('td::text')[6].extract().replace('秒','')
            last_checked = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class CnproxySpider(scrapy.Spider):
    name = 'cnproxy_spider'
    host = 'https://cn-proxy.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'https://cn-proxy.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(CnproxySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['https://cn-proxy.com']
        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('table.sortable').css('tbody tr')

        for item in search_items:
            ip = item.css('td::text')[0].extract()
            port = item.css('td::text')[1].extract()
            protocol = ''
            speed = 0
            last_checked = item.css('td::text')[5].extract()

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class GoubanjiaSpider(scrapy.Spider):
    """
    由于页面渲染加了js加密处理，无法获取正确结果，放弃
    """
    name = 'goubanjia_spider'
    host = 'http://www.goubanjia.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.goubanjia.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(GoubanjiaSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['http://www.goubanjia.com']
        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('table.table-hover').css('tbody tr')

        for item in search_items:
            ip = ''
            port = ''
            ip_tags = item.css('td')[0].xpath('*')
            for tag in ip_tags:
                style = tag.css('::attr(style)').extract_first()
                if style != 'display: none;':
                    txt = tag.css('::text').extract_first()

                    class_attr = tag.css('::attr(class)').extract_first()
                    if txt is not None and class_attr is None:
                        ip += txt
                    elif class_attr is not None:
                        port = txt

            # port = item.css('td::text')[1].extract()
            protocol = item.css('td')[2].css('a::text').extract_first()
            speed = item.css('td::text')[5].extract()
            last_checked = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


class NimadailiSpider(scrapy.Spider):
    name = 'nimadaili_spider'
    host = 'http://www.nimadaili.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'referer': 'http://www.goubanjia.com',
        },
        'DOWNLOADER_MIDDLEWARES': {
            # Engine side
            'mscrapy.middlewares.downloader.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # Downloader side
        },
        'ITEM_PIPELINES': {
            'mscrapy.middlewares.pipeline.proxy_ip_pipeline.ProxyIpPipeline': 100,
        }
    }

    def __init__(self, *args, **kwargs):
        super(NimadailiSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = ['http://www.nimadaili.com/putong/%s/' % i for i in range(1, 6)] + \
               ['http://www.nimadaili.com/gaoni/%s/' % i for i in range(1, 6)] + \
               ['http://www.nimadaili.com/http/%s/' % i for i in range(1, 6)] + \
               ['http://www.nimadaili.com/https/%s/' % i for i in range(1, 6)]

        for url in urls:
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # print(response.request.headers)
        # print(response.url)
        search_items = response.css('table.fl-table').css('tbody tr')

        for item in search_items:
            ip_port = item.css('td::text')[0].extract()
            ip = ip_port.split(':')[0]
            port = ip_port.split(':')[1]

            protocol = item.css('td::text')[1].extract()
            speed = item.css('td::text')[4].extract()
            last_checked = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # print(ip + ',' + response.url)

            item = ProxyIpItem()
            item['ip'] = ip
            item['port'] = port
            item['protocol'] = protocol
            item['speed'] = speed
            item['last_checked'] = last_checked
            item['country'] = 'china'
            item['web_site'] = self.host

            yield item


if __name__ == '__main__':
    import scrapy.cmdline

    # scrapy.cmdline.execute(['scrapy', 'crawl', 'dink_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'kuaidaili_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'data5u_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'txt_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'xicidaili_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'ip3366_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'feiyiproxy_spider'])
    # scrapy.cmdline.execute(['scrapy', 'crawl', 'cnproxy_spider'])
    scrapy.cmdline.execute(['scrapy', 'crawl', 'nimadaili_spider'])


