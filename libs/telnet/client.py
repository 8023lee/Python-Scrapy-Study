# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

import time
import telnetlib


class Client(object):
    def __init__(self, host=None, timeout=5):
        self.host = host
        self.timeout = timeout
        self.tn = telnetlib.Telnet()

    def open(self):
        self.tn.open(host=self.host, timeout=self.timeout)
        time.sleep(1)
        res = self.tn.read_very_eager()
        return Client.filter_response(res.decode('GBK'))

    def close(self):
        if self.tn.sock:
            self.tn.close()
            return 'telnet连接已关闭'
        else:
            return 'telnet未连接，不需要关闭'

    def execute_cmd(self, cmd=''):
        if self.tn.sock:
            self.tn.write(cmd.encode('ascii') + b"\n")
            time.sleep(1)
            res = self.tn.read_very_eager()
            return Client.filter_response(res.decode('gbk'))
        else:
            return 'telnet未连接，请先连接'

    def filter_response(res):
        rchar = [
            '', '[0m', '[m', '[1m', '[7m', '[30m', '[31m', '[32m', '[33m', '[34m', '[35m', '[36m', '[37m',
            '[40m', '[41m', '[42m', '[43m', '[44m', '[45m', '[46m', '[47m',
            '[1;31m', '[1;32m', '[1;33m', '[1;34m', '[1;36m', '[1;37m', '[1;33;44m', '[1;36;44m2', '[11C6060','[45C2', '[2;25H',
            '[5;33m', '[1;33;', '[1;30;40m', '[30;40m', '[1;30;40m', '[34;44m', '[1;37;47m', '[30;47m',
            '[1;15H', '[23;1H', '[24;4H', '[1;5H', '[2;3H', '[24;20H', '[11;7H', '[12;9H', '[23;9H', '[2;25H',
            '[2;12H', '[11;9H', '[24;17H', '[10;5H', '[11;5H', '[20;17H', '[2;5H', '[5;5H', '[6;5H', '[7;5H',
            '[8;5H', '[9;5H', '[10;5H', '[11;5H', '[20;17H', '[14;9H', '[15;9H', '[16;9H', '[17;9H', '[18;9H',
            '[19;9H', '[21;9H','[22;9H', '[1;33;44m', '[2;12H', '[24;30H', '[1;33;44m752', '[1;47m', '[37;47m',
            '[12;30H', '[1;71H', '[1;42m', '[1;32;42m', '[24;31H', '[3;1H ', '[4;1H', '[16;1H', '[4;3H', '[31;44m',
            '[H[J[1;1H[H[J', '[H[J', '[K', '[C', '[23A', '[A', '[19A',
            '[2B','[3B', '[2C', '[9B','[4B'
        ]
        for char in rchar:
            res = res.replace(char, '')
        return res

