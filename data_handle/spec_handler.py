#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/22 0022 14:46
# @Author  : Hadrianl 
# @File    : spec_handler.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_handle import handle_base
class spec_handler_base(handle_base):
    def __init__(self, name, **kwargs):
        self.name = name
        super(spec_handler_base, self).__init__('spec_handler', **kwargs)


