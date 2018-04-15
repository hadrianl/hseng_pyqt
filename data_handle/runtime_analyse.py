#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/13 0013 19:05
# @Author  : Hadrianl 
# @File    : runtime_analyse.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_handle import handle_base


class runtime_analyse_base(handle_base):
    def __init__(self, name, **kwargs):
        self.name = name
        super(runtime_analyse_base, self).__init__('runtime_analyse', **kwargs)

