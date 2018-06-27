#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:28
# @Author  : Hadrianl 
# @File    : OHLC.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pandas as pd
import pymysql as pm
from util import *
from threading import Lock
from PyQt5 import QtCore
from queue import Queue
import queue
import zmq
from datetime import datetime
from spapi.sp_struct import SPApiTicker, SPApiPrice
from collections import deque
from threading import Thread


class market_data_base(QtCore.QObject):
    def __init__(self):
        self._conn = pm.connect(host=KAIRUI_MYSQL_HOST, user=KAIRUI_MYSQL_USER,
                                password=KAIRUI_MYSQL_PASSWD, charset='utf8')
        self._data = pd.DataFrame(columns=['open', 'high', 'low', 'close'], index=['datetime'])
        super(market_data_base, self).__init__()

    @property
    def open(self):
        return self.data.loc[:, 'open']

    @property
    def high(self):
        return self.data.loc[:, 'high']

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
        raise NotImplementedError

    @data.setter
    def data(self, value):
        if not isinstance(value, pd.DataFrame):
            raise ValueError('data must be an DataFrame')
        if value.columns.tolist() != ['datetime', 'open', 'high', 'low', 'close']:
            raise ValueError("data columns must be ['datetime', 'open', 'high', 'low', 'close']")
        self._data = value


class OHLC(market_data_base):  # 主图表的OHLC数据类
    """
    OHLC主要有三个数据构成：
    A.当前分钟的ticker数据-ticker（如果订阅）
    B.所有一分钟的OHLC数据-_data
    C.根据ktype重采样后的OHLC数据-data
    """
    resample_sig = QtCore.pyqtSignal()
    new_ohlc_1m_sig = QtCore.pyqtSignal()
    ohlc_sig = QtCore.pyqtSignal()
    ticker_sig = QtCore.pyqtSignal(SPApiTicker)
    price_sig = QtCore.pyqtSignal(SPApiPrice)

    def __init__(self, symbol, minbar=None, ktype='1T', db='futures_min'):
        market_data_base.__init__(self)
        self.__ktype = ktype
        self.symbol = symbol
        self._minbar = minbar
        self.__is_ticker_active = False
        self.__is_price_active = False
        self._last_tick = None
        self._thread_lock = Lock()
        self.extra_data = {}
        self.bar_size = 200
        self.db = db
        F_logger.info(f'D+初始化请求{self.symbol}数据')

    def __str__(self):
        return f"<{self.__ktype}-{self.symbol}> *{self.datetime.min()}-->{self.datetime.max()}*"

    def __repr__(self):
        return self.data.__repr__()

    def __add__(self, data):  # 重载+运算符，能够通过“OHLC + 指标”的语句添加指标
        self._data_register(data)

    def __sub__(self, data):  # 重载-运算符，能够通过“OHLC - 指标”的语句取出指标指标
        self._data_unregister(data)

    def __getattr__(self, item):
        return self.extra_data.get(item)

    def __call__(self, daterange, limit_bar=True):
        start, end = daterange
        symbol = self.symbol[:3] if self.db != 'futures_min' else self.symbol
        if bool(self._minbar) & limit_bar:
            self._sql = f"select datetime, open, high, low, close from " \
                        f"(select * from carry_investment.{self.db} " \
                        f"where datetime<\"{end} \" and prodcode=\"{symbol}\" " \
                        f"order by id desc limit 0,{self._minbar}) as fm order by fm.id asc"
            F_logger.info(f'D+初始化{symbol}数据,请求结束时间：<{end}>前至{self._minbar}条1min bar')
        else:
            self._sql = f"select datetime, open, high, low, close from carry_investment.{self.db} \
                                        where datetime>=\"{start}\" \
                                        and datetime<\"{end} \"\
                                        and prodcode=\"{symbol}\""
            F_logger.info(f'D+初始化{symbol}数据,请求时间<{start}>-<{end}>')
        try:
            self._data = pd.read_sql(self._sql, self._conn, index_col='datetime')  # _data是一分钟的OHLC
            self._conn.commit()
            self.last_bar_timerange = [self.data.index.floor(self.__ktype)[-1],
                                       self.data.index.ceil(self.__ktype).shift(int(self.__ktype[:-1]), self.__ktype[-1])[-1]]
            F_logger.info(f'D+初始化{self.symbol}数据完成.{self.start}-->{self.end}')
        except:
            F_logger.error(f'D+初始化{self.symbol}数据失败.ERROR,')
        return self

    def change_symbol(self, symbol, daterange=None, limit_bar=True):
        self.inactive_ticker()
        self.inactive_price()
        self.symbol = symbol
        if daterange:
            self.__call__(daterange, limit_bar)
        else:
            self.__call__([self.start, self.end], limit_bar)

        self.active_ticker()
        self.active_price()
        self.ohlc_sig.emit()
        self.update()

    def amend_ohlc(self, ticker):
        l_datetime = self._data.index[-2]
        n_datetime = dt.datetime.fromtimestamp(ticker.TickerTime)
        print(l_datetime, n_datetime)
        if  l_datetime < n_datetime - dt.timedelta(seconds=n_datetime.second):
            sql = f"select datetime, open, high, low, close from carry_investment.futures_min " \
                  f"where datetime>\"{l_datetime}\" and datetime<=\"{n_datetime}\" and prodcode=\"{self.symbol}\" "
            try:
                amend_data = pd.read_sql(sql, self._conn, index_col='datetime')  # _data是一分钟的OHLC
                self._conn.commit()
                self._data = self._data.append(amend_data)
            except Exception as e:
                print(e)

    # def repair_ohlc(self):
    #     index = self._data.index
    #     for i0, i1 in zip(index, index.offset(1))[1:]:
    #         if dt.timedelta(minutes=1) < i1 - i0 < dt.timedelta(minutes=10):
    #             sql = f"select datetime, open, high, low, close from carry_investment.futures_min " \
    #                   f"where datetime>\"{i0}\" and datetime<=\"{i1}\" and prodcode=\"{self.symbol}\" "
    #             try:
    #                 repair_data = pd.read_sql(sql, self._conn, index_col='datetime')
    #                 self._data = self._data.append(repair_data)
    #             except Exception as e:
    #                 print(e)


    def __init_ticker_sub(self):
        """
        初始化订阅连接
        :return:
        """
        try:
            sql = 'select tickertime, price, qty from carry_investment.futures_tick ' \
                  'where tickertime>=(select DATE_FORMAT(TIMESTAMP(max(tickertime)),"%Y-%m-%d %H:%i:00") ' \
                  'from carry_investment.futures_tick)'
            # if len(self._data) >= self.bar_size:
            #     self._data.drop(self._data.index[0], inplace=True)
            self._tickers = pd.read_sql(sql, self._conn, index_col='tickertime')
            self._conn.commit()
            ticker_resampled = self._tickers.resample('1T').apply({'price': 'ohlc'})
            self._data = self._data.append(ticker_resampled.iloc[0]['price'])
            F_logger.info(f'D+初始化请求{self.symbol}当前min-TICKER数据')
        except Exception as e:
            self._tickers = pd.DataFrame(columns=['price', 'qty'], index=pd.Index([], name='tickertime'))
            F_logger.error(f'D+初始化请求{self.symbol}当前min-TICKER数据失败')

        self._sub_tickers_queue = Queue()
        self._tickers_sub_socket = zmq.Context().socket(zmq.SUB)
        self._tickers_sub_socket.connect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}')
        self._tickers_sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._tickers_sub_socket.setsockopt(zmq.RCVTIMEO, 5000)
        F_logger.info(f'P+初始化{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}订阅端口')

    def __ticker_sub(self):
        F_logger.info(f'开始订阅{self.symbol}-TICKER数据')
        while self.__is_ticker_active:
            try:
                ticker = self._tickers_sub_socket.recv_pyobj()
                if ticker.ProdCode.decode() == self.symbol and ticker.DealSrc == 1:
                    self._sub_tickers_queue.put(ticker)
            except zmq.error.ZMQError:
                F_logger.debug('接收{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}订阅端口TICKER数据超时')
                ...
        F_logger.info(f'暂停订阅{self.symbol}-TICKER数据')

    def __ticker_update(self):
        """订阅的基础tick数据构造成1min的ohlc，同时只保留当前分钟的ticker数据"""
        F_logger.info(f'D↑开始更新{self.symbol}-TICKER数据')
        _first = True
        while self.__is_ticker_active:
            try:
                ticker = self._sub_tickers_queue.get(timeout=5)
                if _first:
                    _first = False
                    self.amend_ohlc(ticker)
                if not self._last_tick:
                    self._last_tick = ticker
                # self._thread_lock.acquire()
                if not self._last_tick.TickerTime // 60 == ticker.TickerTime // 60:  # 判断新tick是否与上一tick处于同一分钟
                    if len(self._data) >= self.bar_size:  # 如果_data的bar数量已经超出bar_size则drop第一根bar
                        self._data.drop(self._data.index[0], inplace=True)
                    self._tickers = pd.DataFrame(columns=['price', 'qty'], index=pd.Index([], name='tickertime'))
                    self._tickers = self._tickers.append(pd.DataFrame({'price': ticker.Price, 'qty': ticker.Qty},
                                                                      index=[datetime.fromtimestamp(ticker.TickerTime)]))
                    ticker_resampled = self._tickers.resample('1T').apply({'price': 'ohlc'})  # 上一分钟内的所有tick构造出新的_data bar
                    self._data = self._data.append(ticker_resampled.iloc[0]['price'])
                    self.update()  # 更新相关的指标数据
                    if not self.last_bar_timerange[0] <= self._data.index[0] < self.last_bar_timerange[1]:
                        # 判断是否已经超出data的最后一根bar的范围
                        self.ohlc_sig.emit()
                        self.last_bar_timerange = [self.data.index.floor(self.__ktype)[-1],
                                                   self.data.index.ceil(self.__ktype).shift(int(self.__ktype[:-1]),
                                                                                            self.__ktype[-1])[-1]]
                else:
                    self._tickers = self._tickers.append(pd.DataFrame({'price': ticker.Price, 'qty': ticker.Qty},
                                                                      index=[datetime.fromtimestamp(ticker.TickerTime)]))
                    ticker_resampled = self._tickers.resample('1T').apply({'price': 'ohlc'})
                    # self._data.iloc[-1] = ticker_resampled.iloc[0]['price']
                    self._data = self._data.append(ticker_resampled.iloc[0]['price'])
                # self._thread_lock.release()
                self._last_tick = ticker
                self.ticker_sig.emit(self._last_tick)  # 发出ticker信号
            except queue.Empty:
                F_logger.debug('接收TICKER队列数据超时')
                ...
        F_logger.info(f'D-暂停更新{self.symbol}-TICKER数据')

    def active_ticker(self):
        if not self.__is_ticker_active:
            self.__is_ticker_active = True
            self.__init_ticker_sub()
            self._ticker_sub_thread = Thread(target=self.__ticker_sub)
            self._ticker_update_thread = Thread(target=self.__ticker_update)
            self._ticker_sub_thread.start()
            self._ticker_update_thread.start()

    def inactive_ticker(self):
        if self.__is_ticker_active:
            self.__is_ticker_active = False
            self._ticker_sub_thread.join()
            self._tickers_sub_socket.disconnect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}')
            F_logger.info(f'P-断开{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}订阅端口连接')
            self._ticker_update_thread.join()

    @property
    def ticker(self):
        return self._tickers

    @property
    def start(self):
        return self.datetime.min()

    @property
    def end(self):
        return self.datetime.max()

    @property
    def data(self):
        data_resampled = self._data.resample(self.__ktype).apply({'open': 'first',
                                                                  'high': 'max',
                                                                  'low': 'min',
                                                                  'close': 'last'})
        return data_resampled.dropna(how='any')

    @property
    def x(self):
        index = self.data.index
        return pd.Series(range(len(index)), index=index)

    @property
    def last_ohlc(self):
        return self.data.iloc[-1]

    @property
    def ktype(self):
        return self.__ktype

    def set_ktype(self, value):
        KTYPES = ['1T', '5T', '10T', '30T', '60T']
        if value in KTYPES and value != self.__ktype:
            self.__ktype = value
            F_logger.info(f'D↑更新OHLC数据,重采样->{self.ktype}')
            self.resample_sig.emit()
            self.update()

    # -----------------------------------------------------------------------------------------------------

    def _data_register(self, data):  # 添加注册指标进入图表的函数
        self.extra_data[data.name] = data(self)
        F_logger.info(f'D+加入{data.type}-{data.name}')

    def _data_unregister(self, data):
        if self.extra_data.pop(data.name, None):
            F_logger.info(f'D-删除{data.type}-{data.name}')

    def update(self):
        for i, v in self.extra_data.items():
            v.update(self)

    # -------------------------------------price---------------------------------------------------------------
    def __init_price_sub(self):
        self.maxlen = 300
        self._sub_price_queue = Queue()
        self.price_queue = deque(maxlen=self.maxlen)
        self._price_sub_socket = zmq.Context().socket(zmq.SUB)
        self._price_sub_socket.connect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}')
        self._price_sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._price_sub_socket.setsockopt(zmq.RCVTIMEO, 5000)
        F_logger.info(f'P+初始化{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}订阅端口')

    def __price_sub(self):
        F_logger.info(f'开始订阅{self.symbol}-PRICE数据')
        while self.__is_price_active:
            try:
                price = self._price_sub_socket.recv_pyobj()
                if price.ProdCode.decode() == self.symbol:
                    self._sub_price_queue.put(price)
                    self.price_queue.append(price)
            except zmq.error.ZMQError:
                F_logger.debug(f'接收{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}订阅端口PRICE数据超时')
                ...
        F_logger.info(f'暂停订阅{self.symbol}-PRICE数据')

    def __price_update(self):
        F_logger.info(f'D↑开始更新{self.symbol}-PRICE数据')
        while self.__is_price_active:
            try:
                price = self._sub_price_queue.get(timeout=5)
                self.price_sig.emit(price)
            except queue.Empty:
                F_logger.debug('接收PRICE队列数据超时')

        F_logger.info(f'D-暂停更新{self.symbol}-PRICE数据')

    def active_price(self):
        if not self.__is_price_active:
            self.__is_price_active = True
            self.__init_price_sub()
            self._price_sub_thread = Thread(target=self.__price_sub)
            self._price_update_thread = Thread(target=self.__price_update)
            self._price_sub_thread.start()
            self._price_update_thread.start()

    def inactive_price(self):
        if self.__is_price_active:
            self.__is_price_active = False
            self._price_sub_thread.join()
            self._price_sub_socket.disconnect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}')
            F_logger.info(f'P-断开{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}订阅端口连接')
            self._price_update_thread.join()

    @property
    def price_list(self):
        return list(self.price_queue).reverse()


# class Price(QtCore.QObject):
#     price_sig = QtCore.pyqtSignal(SPApiPrice)
#     def __init__(self, symbol, maxlen = 300):
#         self.symbol = symbol
#         self.__is_price_active = False
#         self.maxlen = maxlen
#         self._data_queue = Queue()
#         self.price_queue = deque(maxlen=self.maxlen)
#
#     def __init_price_sub(self):
#         self._sub_socket = zmq.Context().socket(zmq.SUB)
#         self._sub_socket.connect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}')
#         self._sub_socket.set_string(zmq.SUBSCRIBE, '')
#         self._sub_socket.setsockopt(zmq.RCVTIMEO, 5000)
#
#     def __price_sub(self):
#         F_logger.info(f'开始订阅{self.symbol}-PRICE数据')
#         while self.__is_price_active:
#             try:
#                 price = self._sub_socket.recv_pyobj()
#                 if price.ProdCode.decode() == self.symbol and price.DealSrc == 1:
#                     self._data_queue.put(price)
#                     self.price_queue.append(price)
#             except zmq.error.ZMQError:
#                 F_logger.debug('接收{ZMQ_SOCKET_HOST}:{ZMQ_TICKER_PORT}订阅端口PRICE数据超时')
#                 ...
#         F_logger.info(f'暂停订阅{self.symbol}-PRICE数据')
#
#     def __price_update(self):
#         F_logger.info(f'开始更新{self.symbol}-PRICE数据')
#         while self.__is_price_active:
#             try:
#                 price = self._data_queue.get(timeout=5)
#                 self.price_sig.emit(price)
#             except queue.Empty :
#                 F_logger.debug('接收PRICE队列数据超时')
#
#         self._data_queue = Queue()
#         F_logger.info(f'暂停更新{self.symbol}-PRICE数据')
#
#     def active_price(self):
#         if not self.__is_price_active:
#             self.__is_price_active = True
#             self.__init_price_sub()
#             self._price_sub_thread = Thread(target=self.__price_sub)
#             self._price_update_thread = Thread(target=self.__price_update)
#             self._price_sub_thread.start()
#             self._price_update_thread.start()
#
#     def inactive_price(self):
#         if self.__is_price_active:
#             self.__is_price_active = False
#             self._price_sub_thread.join()
#             self._sub_socket.disconnect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}')
#             F_logger.info(f'断开{ZMQ_SOCKET_HOST}:{ZMQ_PRICE_PORT}订阅端口连接')
#             self._price_update_thread.join()
#
#     @property
#     def price_list(self):
#         return  list(self.price_queue).reverse()


if __name__ == '__main__':
    df = OHLC('2018-01-18', '2018-01-19 11:00:00', 'HSIF8')
    print(df)
    print(df.__repr__())
