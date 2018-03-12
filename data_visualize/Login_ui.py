#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/5 0005 16:15
# @Author  : Hadrianl 
# @File    : Login_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from login import Ui_LoginWindow
from PyQt5.Qt import QDialog, QMessageBox
from Crypto.Hash import SHA256
import pymysql as pm
from data_fetch.util import MYSQL


class LoginDialog(QDialog, Ui_LoginWindow):
    def __init__(self):
        QDialog.__init__(self)
        Ui_LoginWindow.__init__(self)
        self.setupUi(self)
        self.init_login_info()

    def init_login_info(self):
        dbconfig = {'host': MYSQL['host'],
                    'port': MYSQL['port'],
                    'user': MYSQL['user'],
                    'password': MYSQL['password'],
                    'db': MYSQL['db'],
                    'cursorclass': pm.cursors.DictCursor
                    }
        conn = pm.connect(**dbconfig)
        cursor = conn.cursor()
        sql = 'select username, password, account_type from `carry_investment`.`analysis_login_info`'
        cursor.execute(sql)
        conn.commit()
        self.login_info = cursor.fetchall()
        cursor.close()
        conn.close()

    def login_check(self):
        name_hexdigest = SHA256.new(self.UserName.text().encode()).hexdigest()
        password_hexdigest = SHA256.new(self.Password.text().encode()).hexdigest()
        for i in self.login_info:
            if name_hexdigest == i['username']:
                if password_hexdigest == i['password']:
                    self.accept()
                else:
                    QMessageBox.critical(self, '登录异常', '密码错误！')
                break

        else:
            QMessageBox.critical(self, '登录异常', '用户名不存在！')

