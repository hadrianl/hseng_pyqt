#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:02
# @Author  : Hadrianl 
# @File    : __init__.py.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
from PyQt5.Qt import QMainWindow, QWidget
from PyQt5 import QtGui, QtWidgets
from ui.mainwindow import Ui_MainWindow
from data_visualize.graph import *
from functools import partial
from experimental import normalize_test
from data_visualize.Login_ui import LoginDialog
from order import OrderDialog
from PyQt5.QtCore import QCoreApplication
import sys
import os

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

    def init_login_win(self):
        self.login_win = LoginDialog()  # 登录界面
        self.login_win.UserName.setFocus()
        self.login_win.show()
        self.login_win.accepted.connect(self.show)
        self.login_win.accepted.connect(self.QWidget_ohlc.susp.show)
        self.order_dialog = OrderDialog()
        self.pushButton_order.released.connect(self.order_dialog.show)
        # self.login_win.rejected.connect(self.closeAllWindows)


    def closeEvent(self, a0: QtGui.QCloseEvent):
        reply = QtWidgets.QMessageBox.question(self, '退出',"是否要退出程序？",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                          QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            a0.accept()
            pid = os.getpid()
            os.system(f'taskkill /F /PID {pid}')
        else:
            a0.ignore()

    def init_data_signal(self):
        w_ohlc = self.QWidget_ohlc
        ohlc = w_ohlc.data['ohlc']
        extra_data = ohlc.extra_data
        for i, (name, data) in enumerate(extra_data.items()):
            self.comboBox.addQCheckBox(i, name)
            self.comboBox.qCheckBox[i].setChecked(True)
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda data, x: data.activate() if x else data.inactivate(), data))
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda g_name, x:(w_ohlc.init_graph(g_name), w_ohlc.update_graph(g_name)) if x else w_ohlc.deinit_graph(g_name), name))

    def init_test(self):
        ohlc = self.QWidget_ohlc.data['ohlc']
        self.pushButton_TEST.released.connect(lambda : normalize_test(ohlc, self.horizontalSlider_TEST.value()))
