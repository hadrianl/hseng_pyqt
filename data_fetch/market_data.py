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
        self._data = pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close'])
        super(market_data_base, self).__init__()

    @property
    def open(self):
        return self.data['open']

    @property
    def high(self):
        return self.data['high']

    @property
    def low(self):
        return self.data['low']

    @property
    def close(self):
        return self.data['close']

    @property
    def datetime(self):
        return self.data.index.to_series()

    @property
    def timestamp(self):
        return self.datatime.apply(lambda x: x.timestamp())
    # @property
    # def timestamp(self):
    #     return self.data['datetime'].apply(lambda x: x.timestamp()).rename('timestamp')
    #
    # @property
    # def timeindex(self):
    #     return self.timestamp.index.to_series()
    @property
    def x(self):
        return pd.Series(range(len(self.data)), index=self.data.index)

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
    resample_sig = QtCore.pyqtSignal(str)
    update_sig = QtCore.pyqtSignal()
    def __init__(self, start, end,  symbol, minbar=None, ktype='1T'):
        market_data_base.__init__(self)
        self.start = start
        self.end = end
        self.ktype = ktype
        self.symbol = symbol
        if minbar:
            self._sql = f"select datetime, open, high, low, close from " \
                        f"(select * from carry_investment.futures_min where datetime<\"{end} \" and prodcode=\"{symbol}\" " \
                        f"order by id desc limit 0,{minbar}) as fm order by fm.id asc"
        else:
            self._sql = f"select datetime, open, high, low, close from carry_investment.futures_min \
                                        where datetime>=\"{start}\" \
                                        and datetime<\"{end} \"\
                                        and prodcode=\"{symbol}\""
        self._data = pd.read_sql(self._sql, self._conn, index_col='datetime')
        # self._data.datetime = pd.to_datetime(self._data.datetime)
        self.indicators = {}
        self.bar_size = 200

    def __str__(self):
        return f"<{self.ktype}-{self.symbol}> *{self.data['datetime'].min()}-->{self.data['datetime'].max()}*"

    def __repr__(self):
        return self.data.__repr__()

    def __add__(self, indicator):  # 重载+运算符，能够通过“OHLC + 指标”的语句添加指标
        self._indicator_register(indicator)

    def __sub__(self, indicator):  # 重载-运算符，能够通过“OHLC - 指标”的语句取出指标指标
        self._indicator_unregister(indicator)

    @property
    def data(self):
        if self.ktype == '1T':
            return self._data
        else:
            return self._resample()

    def _indicator_register(self, indicator):  # 添加注册指标进入图表的函数
        self.indicators[indicator.name] = indicator(self)

    def _indicator_unregister(self, indicator):
        self.indicators.pop(indicator.name, None)

    def update(self, last_ohlc_data):
        if len(self.data) >= self.bar_size:
            self.data.drop(self.data.index[0], inplace=True)
        self.data = self.data.append(last_ohlc_data, ignore_index=True)
        for i, v in self.indicators.items():
            v.update(self)

    def _resample(self):
        self.data_resampled = self._data.resample(self.ktype).apply({'open': 'first',
                                                                            'high': 'max',
                                                                            'low': 'min',
                                                                            'close': 'last'})
        return self.data_resampled.dropna(how='any')


class NewOHLC(market_data_base):  # 主图表的最新OHLC数据类，即当前最新处于活跃交易状态的OHLC，多重继承QObject增加其信号槽特性
    ticker_sig = QtCore.pyqtSignal(SPApiTicker)
    ohlc_sig = QtCore.pyqtSignal(pd.DataFrame)
    def __init__(self, symbol, ktype='1T'):
        market_data_base.__init__(self)
        self._symbol = symbol
        self.ktype = ktype
        self._tickers = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
        self.isactive = False
        self._data_queue = Queue()
        self._tick_sig = None
        self._ohlc_sig = None

        self._thread_lock = Lock()
        self._last_tick = None

    def _ticker_sub(self):
        self._sub_socket = zmq.Context().socket(zmq.SUB)
        self._sub_socket.connect(f'tcp://{KAIRUI_SERVER_IP}:6868')
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        try:
            sql = 'select tickertime, price, qty from carry_investment.futures_tick ' \
                  'where tickertime>=(select DATE_FORMAT(TIMESTAMP(max(tickertime)),"%Y-%m-%d %H:%i:00") ' \
                  'from carry_investment.futures_tick)'
            self._tickers = pd.read_sql(sql, self._conn)
            self._tickers.tickertime = self._tickers.tickertime.apply(lambda x: x.timestamp())
        except Exception as e:
            self._tickers = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
        while self.isactive:
            ticker = self._sub_socket.recv_pyobj()
            if ticker.ProdCode.decode() == self._symbol and ticker.DealSrc == 1:
                # print(f'data_sub队列数量：{self._data_queue.qsize()}')
                self._data_queue.put(ticker)
        self._sub_socket.disconnect()

    def _ticker_update(self):
        while self.isactive:
            ticker = self._data_queue.get()
            if not self._last_tick:
                self._last_tick = ticker
            self._thread_lock.acquire()
            if self._last_tick.TickerTime // 60 == ticker.TickerTime // 60:
                self._tickers = self._tickers.append({'tickertime': ticker.TickerTime,
                                                    'price': ticker.Price,
                                                    'qty': ticker.Qty}, ignore_index=True)
            else:
                self.ohlc_sig.emit(self.data)  # 发出ohlc信号
                self._tickers = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
                self._tickers = self._tickers.append({'tickertime': ticker.TickerTime,
                                                    'price': ticker.Price,
                                                    'qty': ticker.Qty}, ignore_index=True)
            self._thread_lock.release()
            self._last_tick = ticker
            if self.ticker_sig:
                self.ticker_sig.emit(self._last_tick)  # 发出ticker信号

    def active(self):
        self.isactive = True
        self._ticker_sub_thread = Thread(target=self._ticker_sub)
        self._data_update_thread = Thread(target=self._ticker_update)
        self._ticker_sub_thread.start()
        self._data_update_thread.start()

    def inactive(self):
        self.isactive = False
        self._ticker_sub_thread.join()
        self._data_update_thread.join()

    @property
    def ticker(self):
        return self._tickers

    @property
    def data(self):
        d = {'datetime': datetime.fromtimestamp((self._tickers.iloc[0].tickertime // 60) * 60),
             'open': self._tickers.price.iloc[0],
             'high': self._tickers.price.max(),
             'low': self._tickers.price.min(),
             'close': self._tickers.price.iloc[-1]}
        return pd.DataFrame(d, index=[self._x], columns=['datetime', 'open', 'high', 'low', 'close'])


if __name__ == '__main__':
    df = OHLC('2018-01-18', '2018-01-19 11:00:00', 'HSIF8')
    print(df)
    print(df.__repr__())
