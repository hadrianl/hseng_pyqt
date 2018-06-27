#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/30 0030 13:25
# @Author  : Hadrianl 
# @File    : info_data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from util import S_logger, F_logger, ZMQ_SOCKET_HOST, ZMQ_INFO_PORT
import zmq
from threading import Thread
from queue import Queue
import pickle
# from spapi.sub_client import SpFunc


class INFO():
    def __init__(self):
        self._ctx = zmq.Context()
        self._server_info_socket = self._ctx.socket(zmq.SUB)
        self._server_info_socket.set_string(zmq.SUBSCRIBE, '')
        self._server_info_socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.info_queue = Queue()
        # self.spfunc = SpFunc()
        self.__receiver_alive = False
        S_logger.info(f'初始化SERVER信息对接')
        F_logger.info(f'初始化SERVER信息对接')

    def __receiver_run(self):
        self._server_info_socket.connect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_INFO_PORT}')
        while self.__receiver_alive:
            try:
                _type, _info, _obj = self._server_info_socket.recv_multipart()
                S_logger.info(_type.decode() + _info.decode())
                obj = pickle.loads(_obj)
                if obj:
                    self.info_queue.put(obj)
            except zmq.ZMQError as e:
                ...

    def receiver_start(self):
        if not self.__receiver_alive:
            self.__receiver_alive = True
            self.__receiver_thread = Thread(target=self.__receiver_run)
            self.__receiver_thread.start()
            S_logger.info(f'开启SERVER信息对接')
            F_logger.info(f'开启SERVER信息对接')

    def receiver_stop(self):
        if self.__receiver_alive:
            self.__receiver_thread.join()
            self._server_info_socket.disconnect(f'tcp://{ZMQ_SOCKET_HOST}:{ZMQ_INFO_PORT}')
            self.__receiver_alive = False
            S_logger.info(f'关闭SERVER信息对接')
            F_logger.info(f'关闭SERVER信息对接')

    def _get_orders(self):
        self._orders = self.spfunc.get_orders_by_array()
        return self._orders

    def _get_position(self):
        self._position = self.spfunc.get_all_pos_by_array()
        return self._position

    def _get_trades(self):
        self._trades = self.spfunc.get_all_trades_by_array()
        return self._trades

    def _get_balance(self):
        self._balance = self.spfunc.get_all_accbal_by_array()
        return self._balance

    # @property
    # def orders(self):
    #     try:
    #         return self._get_orders()
    #     except Exception as e:
    #         print(e)
    #         return self._orders
    #
    # @property
    # def position(self):
    #     try:
    #         return self._get_position()
    #     except Exception as e:
    #         print(e)
    #         return self._position
    #
    # @property
    # def trades(self):
    #     try:
    #         return self._get_trades()
    #     except Exception as e:
    #         print(e)
    #         return self._trades
    #
    # @property
    # def balance(self):
    #     try:
    #         return self._get_balance()
    #     except Exception as e:
    #         print(e)
    #         return self._balance
