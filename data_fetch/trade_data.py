#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/6 0006 15:32
# @Author  : Hadrianl 
# @File    : trade_data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pandas as pd
import pymysql as pm
from util import *
import datetime as dt
from PyQt5.QtCore import QThread

class TradeData():
    def __init__(self, symbol):
        self.type = 'Mark'
        self.name = 'Trade_Data'
        self.symbol = symbol
        self.__active = False
        self.update_thread = self.QThread_update(self.calc)
        F_logger.info(f'D+初始化{self.symbol}交易数据')

    def __call__(self, ohlc):
        self.activate()
        self.update(ohlc)
        return self

    def __str__(self):
        return f'TradeData:<{self.symbol}> *{self.start} --> {self.end}*'

    def __repr__(self):
        return self._trade_data.__repr__()

    def __getitem__(self, key):
        return self._trade_data.__getitem__(key)

    def activate(self):
        self.__active = True
        F_logger.info(f'D#开启{self.symbol}交易数据更新')

    def inactivate(self):
        self.__active = False
        F_logger.info(f'D！暂停{self.symbol}交易数据更新')

    @property
    def is_active(self):
        return self.__active

    def update(self, new_data):
        if self.__active:
            self._conn = pm.connect(host=KAIRUI_MYSQL_HOST, user=KAIRUI_MYSQL_USER,
                                    password=KAIRUI_MYSQL_PASSWD, charset='utf8')
            self.start = new_data.start - dt.timedelta(hours=8)
            self.end = new_data.end - dt.timedelta(hours=8)
            self._sql = f'select Ticket, Account_ID, OpenTime, OpenPrice, CloseTime, ClosePrice, Type, Lots, Status, trader_name ' \
                        f'from `carry_investment`.`order_detail` as od ' \
                        f'join (select id, trader_name from `carry_investment`.`account_info`) as ai on ai.id=od.Account_id ' \
                        f'where Symbol="{self.symbol}" ' \
                        f'and OpenTime>="{self.start}" and CloseTime<"{self.end}" ' \
                        f'and Status>=0'
            self.update_thread.start()

    def calc(self):
        try:
            self._trade_data = pd.read_sql(self._sql, self._conn)
            self._conn.commit()
            self._trade_data['OpenTime'] = self._trade_data['OpenTime'] + dt.timedelta(hours=8)
            self._trade_data['CloseTime'] = self._trade_data['CloseTime'] + dt.timedelta(hours=8)
            F_logger.info(f'D↑更新{self.symbol}交易数据,<{self.start}>-<{self.end}>')
        except Exception as e:
            self._trade_data = pd.DataFrame(columns=['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice',
                                                     'CloseTime', 'ClosePrice', 'Type', 'Lots', 'Status'])
            F_logger.error(f'D↑更新{self.symbol}交易数据,<{self.start}>-<{self.end}>失败.ERROR:', e)

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

    class QThread_update(QThread):
        def __init__(self, handle):
            QThread.__init__(self)
            self.handle = handle
        def run(self):
            self.handle()
