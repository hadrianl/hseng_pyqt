#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/6 0006 15:32
# @Author  : Hadrianl 
# @File    : trade_data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pandas as pd
import pymysql
import sqlalchemy
from data_fetch.util import *
import datetime as dt

class TradeData():
    def __init__(self, start, end, symbol):
        self._conn = sqlalchemy.create_engine(
            f'mysql+pymysql://{KAIRUI_MYSQL_USER}:{KAIRUI_MYSQL_PASSWD}@{KAIRUI_SERVER_IP}'
        )
        self.start = start - dt.timedelta(hours=8)
        self.end = end - dt.timedelta(hours=8)
        self.symbol = symbol
        self._sql = f'select Ticket, Account_ID, OpenTime, OpenPrice, CloseTime, ClosePrice, Type, Lots, Status ' \
                    f'from `carry_investment`.`order_detail` ' \
                    f'where Symbol="{self.symbol}" ' \
                    f'and OpenTime>="{self.start}" and CloseTime<"{self.end}"'

        try:
            self._trade_data = pd.read_sql(self._sql, self._conn)
            self._trade_data['OpenTime'] = self._trade_data['OpenTime'] + dt.timedelta(hours=8)
            self._trade_data['CloseTime'] = self._trade_data['CloseTime'] + dt.timedelta(hours=8)
        except Exception as e:
            print(e)
            self._trade_data = pd.DataFrame(columns=['Ticket', 'Account_ID', 'OpenTime', 'OpenPrice',
                                                     'CloseTime', 'ClosePrice', 'Type', 'Lots', 'Status'])

    def __str__(self):
        return f'TradeData:<{self.symbol}> *{self.start} --> {self.end}*'

    def __repr__(self):
        return self._trade_data.__repr__()

    def __getitem__(self, key):
        return self._trade_data.__getitem__(key)

    @property
    def account(self):
        return self._trade_data.Account_ID.unique().tolist()

