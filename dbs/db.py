# -*- coding: utf-8 -*-
"""数据库组件"""

__author__ = 'lijingang'

import pymysql

import libs.config as conf


class DB(object):
    _conn = None
    _cursor = None
    _affected_rows = 0
    
    def __init__(self):
        pass

    def connect(self, is_create_db = False):
        if not self._conn:
            _db = conf.env.DB_NAME
            if is_create_db:
                _db = None

            self._conn = pymysql.connect(
                host = conf.env.DB_HOST,
                port = int(conf.env.DB_PORT),
                user = conf.env.DB_USER,
                passwd = conf.env.DB_PASS,
                db = _db
            )
        # 游标
        self.__cursor()
        # 数据库连接
        return self._conn

    def close(self):
        self.__cursor_close()

        if self._conn:
            self._conn.close()
            self._conn = None


    def commit(self):
        if self._conn:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            self._conn.rollback()

    def __cursor(self):
        self._cursor = self._conn.cursor(pymysql.cursors.DictCursor)
        # self._cursor = self._conn.cursor()
        return self._cursor

    def __cursor_close(self):
        if self._cursor:
            self._cursor.close()
            self._cursor = None

    def execute(self, sql, args = None):
        self._affected_rows = self._cursor.execute(sql, args)
        return self._affected_rows

    def executemany(self, sql, args = None):
        self._affected_rows = self._cursor.executemany(sql, args)
        return self._affected_rows

    def fetchone(self, sql, args = None):
        self._affected_rows = self._cursor.execute(sql, args)
        data = self._cursor.fetchone()
        return data
    
    def fetchmany(self, top, sql, args = None):
        self._affected_rows = self._cursor.execute(sql, args)
        data = self._cursor.fetchmany(top)
        return data

    def fetchall(self, sql, args = None):
        self._affected_rows = self._cursor.execute(sql, args)
        data = self._cursor.fetchall()
        return data

    def get_affected_rows(self):
        return self._affected_rows

    def get_lastrowid(self):
        return self._cursor.lastrowid
