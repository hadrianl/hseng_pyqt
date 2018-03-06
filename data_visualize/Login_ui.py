#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/5 0005 16:15
# @Author  : Hadrianl 
# @File    : Login_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from login import Ui_LoginWindow
from PyQt5.Qt import QDialog, QMessageBox

class LoginDialog(QDialog, Ui_LoginWindow):
    def __init__(self):
        QDialog.__init__(self)
        Ui_LoginWindow.__init__(self)
        self.setupUi(self)

    def login_check(self):
        # if self.ui.UserName.text() == 'hadrianl' and self.ui.Password.text() == '666666':
        if True:
            self.accept()
        else:
            QMessageBox.critical(self, '错误', '用户名或密码不匹配')