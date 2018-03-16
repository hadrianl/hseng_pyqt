#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:28
# @Author  : Hadrianl 
# @File    : OHLC.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pandas as pd
import pymysql as pm
from data_fetch.util import *
from threading import Thread, Lock
from PyQt5 import QtCore
from queue import Queue
import zmq
from datetime import datetime
from sp_struct import SPApiTicker


class market_data_base(QtCore.QObject):
    def __init__(self):
        self._conn = pm.connect(host=KAIRUI_SERVER_IP, user=KAIRUI_MYSQL_USER,
                                password=KAIRUI_MYSQL_PASSWD, charset='utf8')
        self._data = pd.DataFrame(columns=['open', 'high', 'low', 'close'], index=['datetime'])
        super(market_data_base, self).__init__()

    @property
    def open(self):
        return self.data.loc[:, 'open']

    @property
    def high(self):
        return self.data.loc[:,'high']

    @property
    def low(self):
        return self.data.loc[:, 'low']

    @property
    def close(self):
        return self.data.loc[:, 'close']

    @property
    def datetime(self):
        return self.data.index.to_series()

    @property
    def timestamp(self):
        return self.data.index.to_series().apply(lambda x: x.timestamp())

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError('data must be an DataFrame')
        if value.columns.tolist() != ['datetime', 'open', 'high', 'low', 'close']:
            raise ValueError("data columns must be ['datetime', 'open', 'high', 'low', 'close']")
        self._data = value


class OHLC(market_data_base):  # 主图表的OHLC数据类
    new_ohlc_1m_sig = QtCore.pyqtSignal()
    ohlc_sig = QtCore.pyqtSignal()
    ticker_sig = QtCore.pyqtSignal(SPApiTicker)
    def __init__(self, start, end,  symbol, minbar=None, ktype='1T'):
        market_data_base.__init__(self)
        self.start = start
        self.end = end
        self.ktype = ktype
        self.symbol = symbol
        self._minbar = minbar
        self.isactive = False
        self._data_queue = Queue()
        self._last_tick = None
        self._thread_lock = Lock()
        self.indicators = {}
        self.bar_size = 200
        self.init_data()
        self.init_sub()

    def __str__(self):
        return f"<{self.ktype}-{self.symbol}> *{self.data['datetime'].min()}-->{self.data['datetime'].max()}*"

    def __repr__(self):
        return self.data.__repr__()

    def __add__(self, indicator):  # 重载+运算符，能够通过“OHLC + 指标”的语句添加指标
        self._indicator_register(indicator)

    def __sub__(self, indicator):  # 重载-运算符，能够通过“OHLC - 指标”的语句取出指标指标
        self._indicator_unregister(indicator)

    def init_data(self):
        if self._minbar:
            self._sql = f"select datetime, open, high, low, close from " \
                        f"(select * from carry_investment.futures_min where datetime<\"{self.end} \" and prodcode=\"{self.symbol}\" " \
                        f"order by id desc limit 0,{self._minbar}) as fm order by fm.id asc"
        else:
            self._sql = f"select datetime, open, high, low, close from carry_investment.futures_min \
                                        where datetime>=\"{self.start}\" \
                                        and datetime<\"{self.end} \"\
                                        and prodcode=\"{self.symbol}\""
        self._data = pd.read_sql(self._sql, self._conn, index_col='datetime')
        self.last_bar_timerange = [self.data.index.floor(self.ktype)[-1],
                                   self.data.index.ceil(self.ktype).shift(int(self.ktype[:-1]), self.ktype[-1])[-1]]

    def init_sub(self):
        try:
            sql = 'select tickertime, price, qty from carry_investment.futures_tick ' \
                  'where tickertime>=(select DATE_FORMAT(TIMESTAMP(max(tickertime)),"%Y-%m-%d %H:%i:00") ' \
                  'from carry_investment.futures_tick)'
            # if len(self._data) >= self.bar_size:
            #     self._data.drop(self._data.index[0], inplace=True)
            self._tickers = pd.read_sql(sql, self._conn, index_col='tickertime')
            ticker_resampled = self._tickers.resample('1T').apply({'price': 'ohlc'})
            self._data = self._data.append(ticker_resampled.iloc[0]['price'])

        except Exception as e:
            self._tickers = pd.DataFrame(columns=['price', 'qty'], index=pd.Index([], name='tickertime'))

        self._sub_socket = zmq.Context().socket(zmq.SUB)
        self._sub_socket.connect(f'tcp://{KAIRUI_SERVER_IP}:6868')
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')

    def _ticker_sub(self):
        while self.isactive:
            ticker = self._sub_socket.recv_pyobj()
            if ticker.ProdCode.decode() == self.symbol and ticker.DealSrc == 1:
                self._data_queue.put(ticker)
        self._sub_socket.disconnect()

    def _ticker_update(self):
        while self.isactive:
            ticker = self._data_queue.get()
            if not self._last_tick:
                self._last_tick = ticker
            # self._thread_lock.acquire()
            if not self._last_tick.TickerTime // 60 == ticker.TickerTime // 60:
                if len(self._data) >= self.bar_size:
                    self._data.drop(self._data.index[0], inplace=True)
                self._tickers = pd.DataFrame(columns=['price', 'qty'], index=pd.Index([], name='tickertime'))
                self._tickers = self._tickers.append(pd.DataFrame({'price': ticker.Price, 'qty': ticker.Qty},
                                                                  index=[datetime.fromtimestamp(ticker.TickerTime)]))
                ticker_resampled = self._tickers.resample('1T').apply({'price': 'ohlc'})
                self._data = self._data.append(ticker_resampled.iloc[0]['price'])
                self.update()
                if not self.last_bar_timerange[0] <=self._data.index[0] <self.last_bar_timerange[1]:
                    self.ohlc_sig.emit()
                    self.last_bar_timerange = [self.data.index.floor(self.ktype)[-1],
                                               self.data.index.ceil(self.ktype).shift(int(self.ktype[:-1]),
                                                                                      self.ktype[-1])[-1]]
            else:
                self._tickers = self._tickers.append(pd.DataFrame({'price': ticker.Price, 'qty': ticker.Qty},
                                                                  index=[datetime.fromtimestamp(ticker.TickerTime)]))
                ticker_resampled = self._tickers.resample('1T').apply({'price': 'ohlc'})
                self._data.iloc[-1] = ticker_resampled.iloc[0]['price']

            # self._thread_lock.release()
            self._last_tick = ticker
            if self.ticker_sig:
                self.ticker_sig.emit(self._last_tick)  # 发出ticker信号


    def active_ticker(self):
        self.isactive = True
        self._ticker_sub_thread = Thread(target=self._ticker_sub)
        self._data_update_thread = Thread(target=self._ticker_update)
        self._ticker_sub_thread.start()
        self._data_update_thread.start()

    def inactive_ticker(self):
        self.isactive = False
        self._ticker_sub_thread.join()
        self._data_update_thread.join()

    @property
    def ticker(self):
        return self._tickers

    @property
    def data(self):
        data_resampled = self._data.resample(self.ktype).apply({'open': 'first',
                                                                     'high': 'max',
                                                                     'low': 'min',
                                                                     'close': 'last'})
        return data_resampled.dropna(how='any')

    @property
    def x(self):
        return pd.Series(range(len(self.data)), index=self.data.index)

    @property
    def last_ohlc(self):
        return self.data.iloc[-1]

    def _indicator_register(self, indicator):  # 添加注册指标进入图表的函数
        self.indicators[indicator.name] = indicator(self)

    def _indicator_unregister(self, indicator):
        self.indicators.pop(indicator.name, None)

    def update(self):
        for i, v in self.indicators.items():
            v.update(self)


if __name__ == '__main__':
    df = OHLC('2018-01-18', '2018-01-19 11:00:00', 'HSIF8')
    print(df)
    print(df.__repr__())
