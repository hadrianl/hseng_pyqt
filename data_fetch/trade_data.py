#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/6 0006 15:32
# @Author  : Hadrianl 
# @File    : trade_data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pandas as pd
import pymysql as pm
from data_fetch.util import *
import datetime as dt

class TradeData():
    def __init__(self, start, end, symbol):
        self._conn = pm.connect(host=KAIRUI_MYSQL_HOST, user=KAIRUI_MYSQL_USER,
                                password=KAIRUI_MYSQL_PASSWD, charset='utf8')
        self.start = start - dt.timedelta(hours=8)
        self.end = end - dt.timedelta(hours=8)
        self.symbol = symbol
        self._sql = f'select Ticket, Account_ID, OpenTime, OpenPrice, CloseTime, ClosePrice, Type, Lots, Status, trader_name ' \
                    f'from `carry_investment`.`order_detail` as od ' \
                    f'join (select id, trader_name from `carry_investment`.`account_info`) as ai on ai.id=od.Account_id ' \
                    f'where Symbol="{self.symbol}" ' \
                    f'and OpenTime>="{self.start}" and CloseTime<"{self.end}" ' \
                    f'and Status>=0'

        try:
            self._trade_data = pd.read_sql(self._sql, self._conn)
            self._conn.commit()
            self._trade_data['OpenTime'] = self._trade_data['OpenTime'] + dt.timedelta(hours=8)
            self._trade_data['CloseTime'] = self._trade_data['CloseTime'] + dt.timedelta(hours=8)
            F_logger.info(f'初始化请求{self.symbol}交易数据,<{self.start}>-<{self.end}>成功')
        except Exception as e:
            self._trade_data = pd.DataFrame(columns=['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice',
                                                     'CloseTime', 'ClosePrice', 'Type', 'Lots', 'Status'])
            F_logger.debug(f'初始化请求{self.symbol}交易数据,<{self.start}>-<{self.end}>失败.ERROR:', e)

    def __str__(self):
        return f'TradeData:<{self.symbol}> *{self.start} --> {self.end}*'

    def __repr__(self):
        return self._trade_data.__repr__()

    def __getitem__(self, key):
        return self._trade_data.__getitem__(key)

    def update(self, t):
        self.start = self.start + dt.timedelta(minutes=t)
        self.end = self.end + dt.timedelta(minutes=t)
        self._sql = f'select Ticket, Account_ID, OpenTime, OpenPrice, CloseTime, ClosePrice, Type, Lots, Status, trader_name ' \
                    f'from `carry_investment`.`order_detail` as od ' \
                    f'join (select id, trader_name from `carry_investment`.`account_info`) as ai on ai.id=od.Account_id ' \
                    f'where Symbol="{self.symbol}" ' \
                    f'and OpenTime>="{self.start}" and CloseTime<"{self.end}" ' \
                    f'and Status>=0'
        try:
            self._trade_data = pd.read_sql(self._sql, self._conn)
            self._conn.commit()
            self._trade_data['OpenTime'] = self._trade_data['OpenTime'] + dt.timedelta(hours=8)
            self._trade_data['CloseTime'] = self._trade_data['CloseTime'] + dt.timedelta(hours=8)
            F_logger.info(f'更新{self.symbol}交易数据,<{self.start}>-<{self.end}>成功')
        except Exception as e:
            self._trade_data = pd.DataFrame(columns=['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice',
                                                     'CloseTime', 'ClosePrice', 'Type', 'Lots', 'Status'])
            F_logger.debug(f'更新{self.symbol}交易数据,<{self.start}>-<{self.end}>失败.ERROR:', e)

    @property
    def account(self):
        return self._trade_data.Account_ID.unique().tolist()

    @property
    def data(self):
        return self._trade_data

    @property
    def open(self):
        return self._trade_data[['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice', 'Type', 'Lots']].set_index('OpenTime')

    @property
    def close(self):
        return self._trade_data[['Ticket', 'Account_ID', 'CloseTime', 'ClosePrice', 'Type', 'Lots']].set_index('CloseTime')

    @property
    def long(self):
        return self._trade_data.query('Type==0')[['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice',  'CloseTime', 'ClosePrice', 'Lots']]

    @property
    def short(self):
        return self._trade_data.query('Type==1')[['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice',  'CloseTime', 'ClosePrice', 'Lots']]
