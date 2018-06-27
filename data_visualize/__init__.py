#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:02
# @Author  : Hadrianl 
# @File    : __init__.py.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
from PyQt5.Qt import QMainWindow
from PyQt5 import QtGui, QtWidgets
from ui.mainwindow import Ui_MainWindow
from data_visualize.graph import *
from functools import partial
from experimental import normalize_test
from data_visualize.Login_ui import LoginDialog
# from SpInfo_ui import OrderDialog, AccInfoWidget
from data_visualize.OHLC_ui import TrayIcon
from data_fetch.info_data import INFO
# from sp_func.local import *
from util import S_logger
import os


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.init_login_win()
        # self.init_order_dialog()
        self.init_info()
        # self.init_acc_info_widget()

    def init_login_win(self):
        self.login_win = LoginDialog()  # 登录界面
        self.login_win.UserName.setFocus()
        self.login_win.accepted.connect(self.show)
        self.login_win.accepted.connect(self.init_tray)
        # self.login_win.rejected.connect(self.closeAllWindows)

    def init_tray(self):
        self.tray_icon = TrayIcon()
        w_ohlc = self.QWidget_ohlc
        self.tray_icon.activated.connect(lambda r: w_ohlc.susp.setVisible(w_ohlc.susp.isHidden()) if r == 3 else ...)
        self.tray_icon.action_win.triggered.connect(lambda: self.show())
        self.tray_icon.action_susp.triggered.connect(lambda: w_ohlc.susp.show())
        self.tray_icon.action_quit.triggered.connect(lambda: (self.tray_icon.hide(), self.close))
        self.tray_icon.show()
        S_logger.addHandler(self.tray_icon.messager)

    # def init_order_dialog(self):
    #     self.order_dialog = OrderDialog()
    #     self.pushButton_order.released.connect(self.order_dialog.show)

    def init_info(self):
        self.info = INFO()
        self.info.receiver_start()

    # def init_acc_info_widget(self):
    #     self.acc_info_widget = AccInfoWidget()
    #     self.pushButton_acc_info.released.connect(self.acc_info_widget.show)
    #     self.acc_info_widget.tabWidget_acc_info.currentChanged.connect(
    #         lambda n: print(self.info.orders) if n in [0] else ...)
    #     self.acc_info_widget.tabWidget_acc_info.currentChanged.connect(
    #         lambda n: print(self.info.position) if n in [1] else ...)
    #     self.acc_info_widget.tabWidget_acc_info.currentChanged.connect(
    #         lambda n: print(self.info.trades) if n in [2] else ...)
    #     self.acc_info_widget.tabWidget_acc_info.currentChanged.connect(
    #         lambda n: print(self.info.balance) if n in [3] else ...)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        reply = QtWidgets.QMessageBox.question(self, '退出', "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            a0.accept()
            pid = os.getpid()
            os.system(f'taskkill /F /PID {pid}')
        else:
            a0.ignore()

    def init_signal(self):
        w_ohlc = self.QWidget_ohlc
        ohlc = w_ohlc.data['ohlc']
        extra_data = ohlc.extra_data
        self.pushButton_ChangeSymbol.released.connect(lambda: [setattr(extra_data['Trade_Data'], 'symbol', self.lineEdit_TradeSymbol.text()),
                                                               ohlc.change_symbol(self.lineEdit_Symbol.text()),
                                                               ])
        for i, (name, data) in enumerate(extra_data.items()):
            self.comboBox.addQCheckBox(i, name)
            self.comboBox.qCheckBox[i].setChecked(True)
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda data_, x: data_.activate() if x else data_.inactivate(), data))
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda g_name, x: (w_ohlc.init_graph(g_name), w_ohlc.update_graph(g_name)) if x else w_ohlc.deinit_graph(g_name), name))

    def init_test(self):
        ohlc = self.QWidget_ohlc.data['ohlc']
        self.pushButton_TEST.released.connect(lambda: normalize_test(ohlc, self.horizontalSlider_TEST.value()))
