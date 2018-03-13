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
from queue import Queue
import zmq
from datetime import datetime



class market_data_base():
    def __init__(self):
        self._conn = pm.connect(host=KAIRUI_SERVER_IP, user=KAIRUI_MYSQL_USER,
                                password=KAIRUI_MYSQL_PASSWD, charset='utf8')
        self._data = pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close'])

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
        return self.data['datetime']

    @property
    def timestamp(self):
        return self.data['datetime'].apply(lambda x: x.timestamp()).rename('timestamp')

    @property
    def timeindex(self):
        return self.timestamp.index.to_series()

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
    def __init__(self, start, end,  symbol, minbar=None, ktype=1):
        super(OHLC, self).__init__()
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
        self.data = pd.read_sql(self._sql, self._conn)
        self.data.datetime = pd.to_datetime(self.data.datetime)
        self.indicators = {}
        self.bar_size = 200

    def __str__(self):
        return f"<{self.ktype}-{self.symbol}> *{self.data['datetime'].min()}-->{self.data['datetime'].max()}*"

    def __repr__(self):
        return self.data.__repr__()

    def __add__(self, indicator):  # 重载+号，能够通过“OHLC + 指标”的语句添加指标
        self._indicator_register(indicator)

    def _indicator_register(self, indicator):  # 添加注册指标进入图表的函数
            self.indicators[indicator.name] = indicator(self)

    def update(self, last_ohlc_data):
        if len(self.data) >= self.bar_size:
            self.data.drop(self.data.index[0], inplace=True)
        self.data = self.data.append(last_ohlc_data, ignore_index=True)
        for i, v in self.indicators.items():
            v.update(self)

    def _resample(self, ktype):
        self.data_resampled = self.data.resample(ktype, on='datetime').agg({'open': lambda x: x.head(1),
                                                                            'high': lambda x: x.max(),
                                                                            'low': lambda x: x.min(),
                                                                            'close': lambda x: x.tail(1)})
        return self.data_resampled


class NewOHLC(market_data_base):  # 主图表的最新OHLC数据类，即当前最新处于活跃交易状态的OHLC
    def __init__(self, symbol, ktype=1):
        super(NewOHLC, self).__init__()
        self._symbol = symbol
        self.ktype = ktype
        self._ticker = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
        self.isactive = False
        self._data_queue = Queue()
        self._tick_sig = None
        self._ohlc_sig = None

        self._thread_lock = Lock()
        self._last_tick = None

    def bindsignal(self, tick_signal, ohlc_signal):
        self._tick_sig = tick_signal
        self._ohlc_sig = ohlc_signal

    def _ticker_sub(self):
        self._sub_socket = zmq.Context().socket(zmq.SUB)
        self._sub_socket.connect(f'tcp://{KAIRUI_SERVER_IP}:6868')
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        try:
            sql = 'select tickertime, price, qty from carry_investment.futures_tick ' \
                  'where tickertime>=(select DATE_FORMAT(TIMESTAMP(max(tickertime)),"%Y-%m-%d %H:%i:00") ' \
                  'from carry_investment.futures_tick)'
            self._ticker = pd.read_sql(sql, self._conn)
            self._ticker.tickertime = self._ticker.tickertime.apply(lambda x: x.timestamp())
        except Exception as e:
            self._ticker = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
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
            if self._last_tick.TickerTime//(60*self.ktype) == ticker.TickerTime//(60*self.ktype):
                self._ticker = self._ticker.append({'tickertime': ticker.TickerTime,
                                                    'price': ticker.Price,
                                                    'qty': ticker.Qty}, ignore_index=True)
            else:
                self._ohlc_sig.emit(self.data)
                self._ticker = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
                self._ticker = self._ticker.append({'tickertime': ticker.TickerTime,
                                                    'price': ticker.Price,
                                                    'qty': ticker.Qty}, ignore_index=True)
            self._thread_lock.release()
            self._last_tick = ticker
            if self._tick_sig:
                # print(f'{datetime.fromtimestamp(ticker.TickerTime)}-price:{ticker.Price}-qty:{ticker.Qty}')
                # print(f'{datetime.now()}剩余data_queue队列数量：{self._data_queue.qsize()}')
                self._tick_sig.emit()

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
        return self._ticker

    @property
    def data(self):
        d = {'datetime': datetime.fromtimestamp((self._ticker.iloc[0].tickertime // 60) * 60),
             'open': self._ticker.price.iloc[0],
             'high': self._ticker.price.max(),
             'low': self._ticker.price.min(),
             'close': self._ticker.price.iloc[-1]}
        return pd.DataFrame(d, index=[self._timeindex], columns=['datetime', 'open', 'high', 'low', 'close'])


if __name__ == '__main__':
    df = OHLC('2018-01-18', '2018-01-19 11:00:00', 'HSIF8')
    print(df)
    print(df.__repr__())
