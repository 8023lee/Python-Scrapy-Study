# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'

import datetime

from flask_site.ext.db import db


class Account(db.Model):
    __tablename__ = 'm_platform_account'

    id = db.Column(db.Integer, primary_key=True)
    platformSn = db.Column(db.String(30), nullable=False)
    platformName = db.Column(db.String(30), nullable=False)
    loginname = db.Column(db.String(30), nullable=False)
    loginpass = db.Column(db.String(30), nullable=False)
    loginCookieEnable = db.Column(db.Boolean, nullable=False)
    loginCookieUpdateTime = db.Column(db.TIMESTAMP, nullable=False)
    phoneNum = db.Column(db.String(11), nullable=False)
    isEnable = db.Column(db.Boolean, nullable=False, default=1)
    isPost = db.Column(db.Boolean, nullable=False, default=1)
    score = db.Column(db.Integer, nullable=False, default=0)
    loginStatus = db.Column(db.String(60), nullable=False, default='')
    postUrl = db.Column(db.String(100), nullable=False, default='')
    loginType = db.Column(db.String(30), nullable=False, default='auto')
    loginCookie = db.Column(db.String(2000), nullable=False, default='[]')
    createTime = db.Column(db.TIMESTAMP, nullable=False, default=datetime.datetime)
    updateTime = db.Column(db.TIMESTAMP, nullable=False, default=datetime.datetime)

    def to_dict(self):
        _acct = {}
        _acct['id'] = self.id
        _acct['platformSn'] = self.platformSn
        _acct['platformName'] = self.platformName
        _acct['loginname'] = self.loginname
        _acct['loginCookieEnable'] = self.loginCookieEnable
        _acct['loginCookieUpdateTime'] = self.loginCookieUpdateTime.strftime("%Y-%m-%d %H:%M:%S")
        _acct['phoneNum'] = self.phoneNum
        _acct['isEnable'] = self.isEnable
        _acct['isPost'] = self.isPost
        _acct['score'] = self.score
        _acct['loginStatus'] = self.loginStatus
        _acct['postUrl'] = self.postUrl
        _acct['loginType'] = self.loginType
        _acct['createTime'] = self.createTime.strftime("%Y-%m-%d %H:%M:%S")
        _acct['updateTime'] = self.updateTime.strftime("%Y-%m-%d %H:%M:%S")

        return _acct


