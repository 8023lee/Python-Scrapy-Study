# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'


import random

from mscrapy.settings import USER_AGENT_LIST


class UserAgentMiddleware(object):
    def __init__(self, user_agent='Scrapy'):
        self.user_agent = user_agent


    def process_request(self, request, spider):
        # print('UserAgentMiddleware.process_request')
        self.user_agent = random.choice(USER_AGENT_LIST)
        if self.user_agent:
            request.headers.setdefault(b'User-Agent', self.user_agent)
