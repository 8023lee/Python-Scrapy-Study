# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'



import getpass

import sys
import re
import time
import telnetlib
from libs.telnet.client import Client as TelnetClient


HOST = "bbs.newsmth.net"

USER = "LeeLv520".encode('ascii')

PASSWORD = "520@LvK.".encode('ascii')

tn = TelnetClient(host=HOST, timeout=5)
res = tn.open()
print(res)

cmd = None
while cmd != 'exit':
    print('before input')
    cmd = input()
    print('after input')
    res = tn.execute_cmd(cmd)
    print(res)

tn.close()


#
#
# tn = telnetlib.Telnet(host=HOST, timeout=5)
# # tn.open(HOST)
# time.sleep(2)
# res = tn.read_very_eager()
# print(res.decode('gbk'))
# print('====begin====')
# cmd=None
# while cmd != 'exit':
#     print('before input')
#     cmd = input()
#     print('after input')
#     tn.write(cmd.encode('ascii') + b"\n")
#     time.sleep(2)
#     res = tn.read_very_eager()
#     print(res.decode('gbk'))
#
# tn.close()

    # res = tn.read_until('\r'.encode('ascii'), timeout=5)
    # res = tn.expect(utf8_encode([
    #     '请输入代号:',
    #     '请输入密码:',
    #     '按 [RETURN] 继续',
    #     '按任何键继续 ..',
    #     '本日十大热门话题',
    #     '按任意键继续...',
    #     '如何处理以上密码输入错误记录',
    #     '请输入你的性别',
    #     '请输入您的出生日期',
    #     '出生月',
    #     '出生日',
    #     '主选单',
    #     '工具箱选单',
    #     '请选择消费项目:',
    #     '当前积分不满足转让要求，不能转让积分',
    #     '请输入积分接收ID:',
    #     '请输入转让的积分:',
    #     '输入积分不满足积分转让要求，不能转让积分'
    # ]))
#     res = tn.expect([
#             re.compile("请输入密码:".encode('gbk'), re.I),
#             re.compile("请输入代号:".encode('gbk'), re.I)
#
#         ], 10)
#
#     print(res[0])
#     print(res[1])
#     print(res[2].decode('gbk'))
#     cmd = input()
# tn.close()

# res = tn.read_until('请输入代号:'.encode('utf8'), timeout=5)
# res = tn.read_until('XXXX'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
#
# tn.write(USER + b"\n")
#
# res = tn.read_until('请输入密码:'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
#
# tn.write(PASSWORD + b"\n")
#
# res = tn.read_until('按 [RETURN] 继续'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('按任何键继续 ..'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('本日十大热门话题'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('按任意键继续...'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('按任意键继续...'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('主选单'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write("I".encode('ascii') + b"\n")
#
# res = tn.read_until('工具箱选单'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write("Z".encode('ascii') + b"\n")
#
# res = tn.read_until('请选择消费项目:'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write("8".encode('ascii') + b"\n")
#
# res = tn.read_until('当前积分不满足转让要求，不能转让积分, 按 <ENTER> 键继续'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('请选择消费项目:'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write("0".encode('ascii') + b"\n")
#
# res = tn.read_until('退出 ...<Enter>'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write(b"\n")
#
# res = tn.read_until('工具箱选单'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write("E".encode('ascii') + b"\n")
#
# res = tn.read_until('主选单'.encode('utf8'), timeout=5)
# print(res.decode('gbk'))
# tn.write("G".encode('ascii') + b"\n")
# tn.write("4".encode('ascii') + b"\n")
# tn.write(b"\n")

# tn.write("exit".encode('ascii') + b"\n")
# tn.close()

# 请输入积分接收ID:
# leeLv520 当前积分不满足转让要求，不能接收积分, 按 <ENTER> 键继续...