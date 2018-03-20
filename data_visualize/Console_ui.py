#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/31 0031 15:12
# @Author  : Hadrianl 
# @File    : Console_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pyqtgraph.console
from util import V_logger
from console import *
from PyQt5.Qt import QWidget
# from PyQt5.QtCore.Qt.WindowType import WindowStaysOnTopHint

# class AnalysisConsole(pyqtgraph.console.ConsoleWidget):
#     def __init__(self, namespace):
#         text = f'''实盘分析Console测试（help_doc()调用帮助文档）'''
#         super(AnalysisConsole,self).__init__(namespace=namespace, text=text)
#         self.setWindowTitle(text)
#         V_logger.info(f'初始化console交互界面')
#
#     def focus(self):
#         if self.isHidden():
#             self.show()
#         else:
#             self.focusWidget()


class AnalysisConsole(QWidget, Ui_Console):
    def __init__(self, namespace):
        QWidget.__init__(self)
        Ui_Console.__init__(self)
        help_text = f'''实盘分析Console测试（help_doc()调用帮助文档）'''
        self.setupUi(self)
        self.consolewidget.localNamespace = namespace
        self.consolewidget.output.setPlainText(help_text)

    def focus(self):
        if self.isHidden():
            self.show()
        else:
            self.focusWidget()
            # self.setWindowFlags(WindowStaysOnTopHint)

    def update_daterange(self, start, end):
        self.dateTime_start.setDateTime(start)
        self.dateTime_end.setDateTime(end)
