# -*- coding: utf-8 -*-

"""
"""

import sys
import time

from libs.log.logger import LoggerFactory
from dbs.model.basemodel import BaseModel


class ProxyIp(BaseModel):
    # 登录方式常量
    STATUS_INIT = 'init'
    STATUS_ENABLE = 'enable'
    STATUS_UNENABLE = 'unenable'

    def __init__(self):
        super().__init__()

    def get_all_enable(self, limit_num, except_ip_ids):
        where = 'status = "%s"' % ProxyIp.STATUS_ENABLE
        if except_ip_ids:
            where += ' and id not in (%s)' % except_ip_ids
        data = self.__get_all(where=where, order_by='speed asc, last_checked_time desc limit %d' % limit_num )
        return data

    def get_all_for_check(self, limit_num=0):
        order_bys = 'status desc, last_checked_time desc'
        if limit_num:
            order_bys += ' limit %d' % limit_num
        data = self.__get_all(where='invalidNum < 5', order_by=order_bys)
        return data

    def __get_all(self, where=None, order_by=None):
        data = None

        try:
            sql = "select * from m_proxy_ip where 1=1 "
            if where:
                sql += " and %s" % where
            if order_by:
                sql += " order by %s" % order_by

            self.logger.info('获取代理IP信息，sql：' + sql)

            self.DB.connect()
            data = self.DB.fetchall(sql)

            # self.logger.info('获取代理IP信息，数据：%s', str(data))
        except Exception as ex:
            self.logger.exception('获取代理IP信息，异常：%s', str(ex))
        finally:
            self.DB.close()

        return data

    def update(self, update_data, where=None):
        """ 更新 m_proxy_ip 表的数据

        参数
        ----------------
        update_data ：dict 更新的数据，已字段名称为key的字典
        """

        affected_rows = 0

        self.DB.connect()

        try:
            proxy_ip = update_data.copy()
            if where:
                up_where = where
            else:
                up_where = 'id=%d' % proxy_ip.pop("id")

            up_set = ','.join(["%s='%s'" % (key, val) for key, val in proxy_ip.items()])
            if up_where and up_set:
                sql = "update m_proxy_ip set %s where %s" % (up_set, up_where)

                self.logger.info('更新表[m_proxy_ip]，sql：%s', sql)

                affected_rows = self.DB.execute(sql)

                self.DB.commit()
        except Exception as ex:
            self.DB.rollback()
            self.logger.exception('更新表[m_proxy_ip]，异常：%s', str(ex))
        finally:
            self.DB.close()

        return affected_rows


if __name__ == '__main__':
    # 日志组件
    logger = LoggerFactory.get_logger()
    logger.info('==== proxyip_model runing start ====')
    logger.info('==== proxyip_model runing end ====')
