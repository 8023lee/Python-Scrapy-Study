# -*- coding: utf-8 -*-
"""表 m_platform_account 的model类"""

__author__ = 'lijingang'

import threading
import time

from libs.log.logger import LoggerFactory
from dbs.model.basemodel import BaseModel


class Account(BaseModel):
    # 登录方式常量
    LOGIN_TYPE_AUTO = 'auto'
    LOGIN_TYPE_MANUAL = 'manual'

    def __init__(self):
        super().__init__()

    def __get_all_accounts(self, where = None, order_by = None):
        data = None

        try:
            sql = "select * from m_platform_account where isEnable=1 "
            if where:
                sql += " and %s" % (where)
            if order_by:
                sql += " order by %s" % (order_by)
            
            self.logger.info('获取账号信息，sql：' + sql)

            self.DB.connect()
            data = self.DB.fetchall(sql)

            # self.logger.info('获取账号信息，数据：%s', str(data))
        except Exception as ex:
            self.logger.exception('获取账号信息，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

    def get_one(self, where=None):
        data = None

        try:
            sql = "select * from m_platform_account where 1=1 "
            if where:
                sql += " and %s" % (where)

            self.DB.connect()
            data = self.DB.fetchone(sql)
        except Exception as ex:
            self.logger.exception('获取账号信息，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

    def get_all(self, where=None, order_by=None):
        data = None

        try:
            sql = "select * from m_platform_account where 1=1 "
            if where:
                sql += " and %s" % where
            if order_by:
                sql += " order by %s" % order_by

            self.DB.connect()
            data = self.DB.fetchall(sql)
        except Exception as ex:
            self.logger.exception('获取账号信息，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

    def get_post_accounts(self):
        #accounts = {
        #     '13011110001' : [
        #         {'id': 1, 'platformsn': 'sinablog',  loginname': '18911418111', 'loginpass': 'asdf1111', ...},
        #         {'id': 2, 'platformsn': 'hexunblog', loginname': '18911418111', 'loginpass': 'asdf1111', ...}
        #     ],
        #     '13011110002' : [
        #         {'id': 3, 'platformsn': 'sinablog', 'loginname': '18911418111', 'loginpass': 'asdf1111', ...},
        #         {'id': 4, 'platformsn': 'hexunblog', 'loginname': '18911418111', 'loginpass': 'asdf1111', ...}
        #     ],
        # }

        accounts = {}

        data = self.__get_all_accounts(where='isPost=1')
        for val in data:
            # print(val)
            if val.get('phoneNum') in accounts.keys():
                accounts[val.get('phoneNum')].append(val)
            else:
                accounts[val.get('phoneNum')] = [val]

        return accounts

    def get_refresh_accounts(self, login_type = None, is_post = 1):
        # accounts = {
        #     '13011110001' : [
        #         {'id': 1, 'platformsn': 'sinablog',  loginname': '18911418111', 'loginpass': 'asdf1111', ...},
        #         {'id': 2, 'platformsn': 'hexunblog', loginname': '18911418111', 'loginpass': 'asdf1111', ...}
        #     ],
        #     '13011110002' : [
        #         {'id': 3, 'platformsn': 'sinablog', 'loginname': '18911418111', 'loginpass': 'asdf1111', ...},
        #         {'id': 4, 'platformsn': 'hexunblog', 'loginname': '18911418111', 'loginpass': 'asdf1111', ...}
        #     ],
        # }

        accounts = {}

        where = "isPost=%d" % is_post
        if is_post == 0:
            where += " and score < 2000"
        if login_type:
            where += " and loginType='%s'" % (login_type)

        data = self.__get_all_accounts(where=where, order_by="id asc")

        if is_post:
            for val in data:
                if val.get('phoneNum') in accounts.keys():
                    accounts[val.get('phoneNum')].append(val)
                else:
                    accounts[val.get('phoneNum')] = [val]
        else:
            accounts = data
        
        self.logger.info('获取账号信息，账户ID：%s', ",".join([str(v.get('id')) for v in data]))
        return accounts

    def update_login_cookie(self, login_cookie_enable, login_cookie, account_id):
        """ 更新 m_post_task_platform 表的状态

        参数
        ----------------
        loginCookieEnable: int
            登录Cookie是否有效
        loginCookie: list
            登录Cookie
        accountId: int
            账户id
        """
        affected_rows = 0

        self.DB.connect()
        try:
            # 更新 m_platform_account
            sql = "update m_platform_account set loginCookieEnable = %d, loginCookie = '%s', loginCookieUpdateTime = '%s' where id = %d " % (login_cookie_enable, str(login_cookie).replace("'","\""), time.strftime('%Y-%m-%d %H:%M:%S'), account_id)

            # self.logger.info('更新表[m_platform_account]loginCooike信息，sql：%s', sql)
            
            affected_rows = self.DB.execute(sql)

            self.DB.commit()
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('更新表[m_platform_account]loginCooike信息，异常：%s', str(ex))
        finally:
            self.DB.close()

        return affected_rows

    def update(self, update_data, where=None):
        """ 更新 m_platform_account 表的数据

        参数
        ----------------
        update_data ：dict 更新的数据，已字段名称为key的字典
        """

        affected_rows = 0

        self.DB.connect()

        try:
            up_data = update_data.copy()
            if where:
                up_where = where
            else:
                up_where = 'id=%d' % up_data.pop("id")

            up_set = ','.join(["%s='%s'" % (key, val) for key, val in up_data.items()])
            if up_where and up_set:
                sql = "update m_platform_account set %s where %s" % (up_set, up_where)

                self.logger.info('更新表[m_platform_account]，sql：%s', sql)

                affected_rows = self.DB.execute(sql)

                self.DB.commit()
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('更新表[m_platform_account]，异常：%s', str(ex))
        finally:
            self.DB.close()

        return affected_rows


if __name__ == '__main__':
    threading.currentThread().name = 'account-model-logger'
    # 日志组件
    logger = LoggerFactory.get_logger('account-model-logger')
    logger.info('==== accout_model runing start ====')

    accts = Account().get_refresh_accounts(is_post=0)
    # accts = Account().get_post_accounts()
    print(accts)

    logger.info('==== accout_model runing end ====')
