#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:01
# @Author  : Hadrianl 
# @File    : __init__.py.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from util import H_logger
from abc import ABC, abstractmethod

class handle_base(ABC):
    def __init__(self, type, **kwargs):
        self.type = type
        for k, v in kwargs.items():
            setattr(self, '_' + k, v)
        H_logger.info(f'D+初始化{self.type}-{self.name if hasattr(self, "name") else ""}数据-{[k + "=" + str(v) for k, v in kwargs.items()]}')

    @abstractmethod
    def calc(self): ...

    def __call__(self, ohlc):
        self.update(ohlc)
        return self

    def __repr__(self):
        return self._data.__repr__()

    def update(self, new_data):
        self.ohlc = new_data
        self.x = self.ohlc.x
        self.calc()
        H_logger.info(f'D↑更新{self.type}-{self.name if hasattr(self, "name") else ""}数据')

    @property
    @abstractmethod
    def _data(self): ...

