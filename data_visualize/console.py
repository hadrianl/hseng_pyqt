#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/31 0031 15:12
# @Author  : Hadrianl 
# @File    : console.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pyqtgraph as pg
import pyqtgraph.console


class AnalysisConsole(pyqtgraph.console.ConsoleWidget):
    def __init__(self, namespace):
        text = f'''实盘分析Console测试（help()调用帮助文档）'''
        super(AnalysisConsole,self).__init__(namespace=namespace, text=text)
        self.setWindowTitle(text)
