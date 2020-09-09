# -*- coding: utf-8 -*-

"""
"""


__author__ = 'lijingang'


import logging


class WityxSpiderPipeline(object):

    name = 'WityxSpiderPipeline'

    def __init__(self):
        self.logger = logging.LoggerAdapter(logging.getLogger(self.name), {'pipeline': self})

    def process_item(self, item, spider):
        pass

