#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/27 0027 14:45
# @Author  : Hadrianl 
# @File    : tickdata.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import market_data_base
import pandas as pd
from datetime import datetime
import zmq
from threading import Thread, Lock
from queue import Queue


class tickdatas(market_data_base):
    def __init__(self, symbol):
        self._symbol = symbol
        # self._done = False
        self._data = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
        self.isactive = False
        self._sub_socket = zmq.Context().socket(zmq.SUB)
        self._sub_socket.connect('tcp://192.168.2.226:6868')
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._ohlc_queue = Queue()
        self._data_queue = Queue()
        self._sig = None
        self._data_sub_thread = Thread()
        self._data_sub_thread = Thread(target=self.data_sub)
        self._thread_lock = Lock()
        self._last_tick = None

    def bindsignal(self, signal):
        self._sig = signal
        self._data_update_thread = Thread(target=self.data_update)

    def data_sub(self):
        while self.isactive:
            ticker = self._sub_socket.recv_pyobj()
            if ticker.ProdCode.decode() == self._symbol and ticker.DealSrc == 1:
                print(f'data_sub队列数量：{self._data_queue.qsize()}')
                self._data_queue.put(ticker)

    def data_update(self):
        while self.isactive:
            ticker = self._data_queue.get()
            if not self._last_tick:
                self._last_tick = ticker
            self._thread_lock.acquire()
            if (self._last_tick.TickerTime//60)*60 == (ticker.TickerTime//60)*60:
                self._data = self._data.append({'tickertime': ticker.TickerTime,
                                                'price': ticker.Price,
                                                'qty': ticker.Qty}, ignore_index = True)
            else:
                self._ohlc_queue.put_nowait(self.data)
                self._data = pd.DataFrame(columns=['tickertime', 'price', 'qty'])
                self._data = self._data.append({'tickertime': ticker.TickerTime,
                                                'price': ticker.Price,
                                                'qty': ticker.Qty}, ignore_index=True)

            self._last_tick = ticker
            self._thread_lock.release()
            if self._sig:
                self._sig.emit()

    def active(self):
        self.isactive = True
        self._data_sub_thread.start()
        self._data_update_thread.start()

    def inactive(self):
        self.isactive = False
        self._data_sub_thread.join()
        self._data_update_thread.join()

    @property
    def data(self):
        d = {'datetime': datetime.fromtimestamp((self._data.iloc[0].tickertime//60)*60),
             'open': self._data.price.iloc[0],
             'high': self._data.price.max(),
             'low': self._data.price.min(),
             'close': self._data.price.iloc[-1]}
        return pd.DataFrame(d, index=[self._timeindex], columns=['datetime', 'open', 'high', 'low', 'close'])





