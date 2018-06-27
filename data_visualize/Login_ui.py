#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/5 0005 16:15
# @Author  : Hadrianl 
# @File    : Login_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from ui.login import Ui_LoginWindow
from PyQt5.Qt import QDialog
from Crypto.Hash import SHA256
import pymysql as pm
from util import *


class LoginDialog(QDialog, Ui_LoginWindow):
    def __init__(self):
        QDialog.__init__(self)
        Ui_LoginWindow.__init__(self)
        self.setupUi(self)
        self.init_login_info()
        V_logger.info(f'初始化登录界面')

    def init_login_info(self):
        dbconfig = {'host': KAIRUI_MYSQL_HOST,
                    'port': KAIRUI_MYSQL_PORT,
                    'user': KAIRUI_MYSQL_USER,
                    'password': KAIRUI_MYSQL_PASSWD,
                    'db': KAIRUI_MYSQL_DB,
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
        # for i in self.login_info:
        #     if name_hexdigest == i['username']:
        #         if password_hexdigest == i['password']:
        #             self.accept()
        #             H_logger.info(f'帐号:{self.UserName.text()}登入成功！')
        #         else:
        #             QMessageBox.critical(self, '登录异常', '密码错误！')
        #             H_logger.info(f'帐号:{self.UserName.text()}登入,密码错误！')
        #         break
        #
        # else:
        #     QMessageBox.critical(self, '登录异常', '用户名不存在！')
        #     H_logger.info(f'帐号:{self.UserName.text()}登入失败, 帐号不存在')
        self.accept()
