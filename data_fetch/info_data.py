#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/30 0030 13:25
# @Author  : Hadrianl 
# @File    : info_data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from util import S_logger, F_logger, ZMQ_SOCKET_HOST, ZMQ_INFO_PORT
import zmq
from threading import Thread
from spapi.sp_struct import *
from queue import Queue
import pickle

class INFO():
    def __init__(self):
        self._ctx = zmq.Context()
        self._server_info_socket = self._ctx.socket(zmq.SUB)
        self._server_info_socket.set_string(zmq.SUBSCRIBE, '')
        self._server_info_socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.info_queue = Queue()
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