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
import os
server_conf = configparser.ConfigParser()
server_conf.read(os.path.join('conf', 'server.conf'))

# 服务器的MYSQL
KAIRUI_MYSQL_HOST = server_conf.get('MYSQL', 'host')
KAIRUI_MYSQL_PORT = server_conf.getint('MYSQL', 'port')
KAIRUI_MYSQL_USER = server_conf.get('MYSQL', 'user')
KAIRUI_MYSQL_PASSWD = server_conf.get('MYSQL', 'password')
KAIRUI_MYSQL_DB = server_conf.get('MYSQL', 'db')

# 订阅数据的host与port
ZMQ_SOCKET_HOST = server_conf.get('ZMQ_SOCKET', 'host')
ZMQ_TICKER_PORT = server_conf.getint('ZMQ_SOCKET', 'ticker_port')
ZMQ_PRICE_PORT = server_conf.getint('ZMQ_SOCKET', 'price_port')
# 日志的配置

logging.config.fileConfig(os.path.join('conf','log.conf'), disable_existing_loggers=False)
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

def help_doc():
    text = f'''主要命名空间：ohlc, tick_datas,trade_datas, win
    ohlc是数据类的历史K线数据；tick_datas是数据类的当前K线数据(包括当前k线内的tick数据）；
    trade_datas是交易数据；win是可视化类的主窗口
    主要用法：
    ohlc.data-历史K线数据
    ohlc.indicator-历史K线指标数据
    ohlc.open-历史K线open
    ohlc.high-历史K线high
    ohlc.low-历史K线low
    ohlc.close-历史K线close
    ohlc.datetime-历史K线时间
    ohlc.timestamp-历史K线时间戳
    ohlc.timeindex-历史k线时间序列
    tick_datas有ohlc以上的所有属性，另外
    tick_datas.ticker-当前K线的ticker数据
    trade_datas.account-交易数据包含的账户
    win.ohlc_plt-主窗口主图
    win.indicator_plt-主窗口指标图
    win.ma_items_dict-主窗口ma
    win.macd_items_dict-主窗口macd
    win.std_plt-主窗口std图
    win.std_items_dict-主窗口std
    win.mouse-主窗口鼠标
    '''
    print(text)
    return