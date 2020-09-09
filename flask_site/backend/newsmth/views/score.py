# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

from flask import jsonify
from flask import Blueprint, render_template, request
from sqlalchemy import and_, or_

from libs.telnet.client import Client as TelnetClient
from flask_site.common.model.account import Account

mod = Blueprint('newsmthscore', __name__, url_prefix='/newsmthscore', template_folder='../templates')

cache = {}


@mod.route('/', methods=['GET'])
@mod.route('/transfer/',  methods=['GET'])
def transfer():
    return render_template('transfer.html')


@mod.route('/docmd/', methods=['POST'])
def transfer_docmd():
    res = ''
    cmd = request.form['cmd'].strip()
    isusername = request.form['isusername'].strip()

    if not cmd:
        res = '非法命令'
        return res
    elif cmd == 'enter':
        cmd = ''

    if cmd == 'open':
        tn = TelnetClient('bbs.newsmth.net')
        res = tn.open()
        cache['telnetclient'] = tn
        return res

    tn = cache.get('telnetclient')
    if not tn:
        res = 'telnet未连接，请先连接'
        return res

    if cmd == 'close':
        res = tn.close()
    else:
        res = tn.execute_cmd(cmd)
        if isusername:
            acct = Account.query.filter(Account.loginname == cmd).first()
            res += tn.execute_cmd(acct.loginpass)

    return res


@mod.route('/acct_list/', methods=['GET'])
def acct_list():
    res = {"code":0, "msg":"", "count":0, "data":[]}

    page = int(request.args['page'])
    limit = int(request.args['limit'])

    accts = Account.query.filter(and_(Account.platformSn == 'newsmth', Account.isEnable == 1)).paginate(page,limit)
    for item in accts.items:
        res['data'].append(item.to_dict())

    res['count'] = accts.total

    return jsonify(res)
