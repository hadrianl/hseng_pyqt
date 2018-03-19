#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:05
# @Author  : Hadrianl 
# @File    : util.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

"""
该文件存储一些基本的数据获取的字段名转换和基本的数据整理函数
"""
import datetime as dt
from dateutil.parser import parse
import configparser
import logging.config

server_conf = configparser.ConfigParser()
server_conf.read(r'conf\server.conf')

# 服务器的MYSQL
KAIRUI_MYSQL_HOST = server_conf.get('MYSQL', 'host')
KAIRUI_MYSQL_PORT = server_conf.getint('MYSQL', 'port')
KAIRUI_MYSQL_USER = server_conf.get('MYSQL', 'user')
KAIRUI_MYSQL_PASSWD = server_conf.get('MYSQL', 'password')
KAIRUI_MYSQL_DB = server_conf.get('MYSQL', 'db')

# 订阅数据的host与port
ZMQ_SOCKET_HOST = server_conf.get('ZMQ_SOCKET', 'host')
ZMQ_TICKER_PORT = server_conf.getint('ZMQ_SOCKET', 'ticker_port')

# 日志的配置
logging.config.fileConfig(r'conf\log.conf')
A_logger = logging.getLogger('root')
F_logger = logging.getLogger('root.data_fetch')
H_logger = logging.getLogger('root.data_handle')
V_logger = logging.getLogger('root.data_visualize')


MA_COLORS = {'_ma10': (255, 255, 255),
             '_ma20': (129, 255, 8),
             '_ma30': (182, 128, 219),
             '_ma60': (255, 0, 0)}

MONTH_LETTER_MAPS = {1: 'F',
                     2: 'G',
                     3: 'H',
                     4: 'J',
                     5: 'K',
                     6: 'M',
                     7: 'N',
                     8: 'Q',
                     9: 'U',
                     10: 'V',
                     11: 'X',
                     12: 'Z'
                     }

MYSQL = {'host': '192.168.2.226',
         'port': 3306,
         'user': 'kairuitouzi',
         'password': 'kairuitouzi',
         'db': 'carry_investment'}

# 确定需要展示的K线范围
def date_range(type, **kwargs):
    """
    初始化展示日期
    :param type: 'present'为当前行情，'history'
    :param args: type为'present'时，bar_num为1min的bar条数
                 type为'history'时，start为开始的分钟，end为结束的分钟,bar_num为偏移的分钟数
    :return: start_time, end_time
    """
    if type == 'present':
        min_bar = kwargs['bar_num']
        start_time = dt.datetime.now() - dt.timedelta(minutes=min_bar)
        end_time = dt.datetime.now() + dt.timedelta(minutes=10)
    elif type == 'history':
        if kwargs.get('bar_num'):
            t_delta = dt.timedelta(minutes=kwargs.get('bar_num'))
            start_time = parse(kwargs['start']) if kwargs.get('start') else parse(kwargs['end']) - t_delta
            end_time = parse(kwargs['end']) if kwargs.get('end') else parse(kwargs['start']) + t_delta
        elif kwargs.get('start', None) and kwargs.get('end', None):
            start_time = parse(kwargs['start'])
            end_time = parse(kwargs['end'])
    else:
        raise ValueError('type 类型错误')
    A_logger.info(f'初始化{type}数据数据范围:<{start_time}>-<{end_time}>')
    return start_time, end_time

def symbol(code_prefix, type='futures', **kwargs):
    if type == 'futures':
        m_code = MONTH_LETTER_MAPS[kwargs.get('month')] if kwargs.get('month') else MONTH_LETTER_MAPS[dt.datetime.now().month]
        y_code = kwargs['year'][-1] if kwargs.get('year') else str(dt.datetime.now().year)[-1]
        Symbol = code_prefix + m_code + y_code  # 根据当前时间生成品种代码
        A_logger.info(f'初始化symbol代码-{Symbol}')
        return Symbol

def print_tick(new_ticker):
    print(f'tickertime: {new_ticker.TickerTime}-price: {new_ticker.Price}-qty: {new_ticker.Qty}')