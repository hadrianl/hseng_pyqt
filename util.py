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
import numpy as np
from pandas import Timestamp
import configparser
import logging.config
import os
import datetime

from DataIndex import ZB

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
ZMQ_INFO_PORT = server_conf.getint('ZMQ_SOCKET', 'info_port')
# 日志的配置

logging.config.fileConfig(os.path.join('conf','log.conf'), disable_existing_loggers=False)
A_logger = logging.getLogger('root')
F_logger = logging.getLogger('root.data_fetch')
H_logger = logging.getLogger('root.data_handle')
V_logger = logging.getLogger('root.data_visualize')
S_logger = logging.getLogger('server_info')


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

def coincide(df,ma=60):
    da=[[d[0],d[1],d[2],d[3],d[4]] for d in df.values]
    def macd2(da,ma=60,short=12,long=26,phyd=9):
        # da格式：((datetime.datetime(2018, 3, 19, 9, 22),31329.0,31343.0,31328.0,31331.0,249)...)
        dc=[] # 存储元数据字典的列表
        co=0  # macd区域分割的数字
        cds=1 # 区别一些指标的数字
        cd={} # 存储买点卖点指标的字典
        #maidian={} # 存储将要上涨或下跌数据的字典，以做买卖点参考
        def body_k(o, h, l, c):
            if abs(h - l) > 0:
                return abs(o - c) / abs(h - l) > 0.6
            else:
                return False
        is_kc=0 # 是否开仓
        is_d=0 # 上涨次数
        is_k=0 # 下跌次数
        for i in range(len(da)):
            dc.append({'ema_short':0,'ema_long':0,'diff':0,'dea':0,'macd':0,'ma':0,'var':0,'std':0,'reg':0,'mul':0,'datetimes':da[i][0],'open':da[i][1],'high':da[i][2],'low':da[i][3],'close':da[i][4]}) #'cd':0
            if i == long-1:
                ac = da[i - 1][4]
                this_c = da[i][4]
                dc[i]['ema_short'] = ac + (this_c - ac) * 2 / short
                dc[i]['ema_long'] = ac + (this_c - ac) * 2 / long
                #dc[i]['ema_short'] = sum([(short-j)*da[i-j][4] for j in range(short)])/(3*short)
                #dc[i]['ema_long'] = sum([(long-j)*da[i-j][4] for j in range(long)])/(3*long)
                dc[i]['diff'] = dc[i]['ema_short'] - dc[i]['ema_long']
                dc[i]['dea'] = dc[i]['diff'] * 2 / phyd
                dc[i]['macd'] = 2 * (dc[i]['diff'] - dc[i]['dea'])
                co=1 if dc[i]['macd']>=0 else 0
            elif i>long-1:
                n_c = da[i][4]
                dc[i]['ema_short'] = dc[i-1]['ema_short'] * (short-2) / short + n_c * 2 / short
                dc[i]['ema_long'] = dc[i-1]['ema_long'] * (long-2) / long + n_c * 2 / long
                dc[i]['diff'] = dc[i]['ema_short'] - dc[i]['ema_long']
                dc[i]['dea'] = dc[i-1]['dea'] * (phyd-2) / phyd + dc[i]['diff'] * 2 / phyd
                dc[i]['macd'] = 2 * (dc[i]['diff'] - dc[i]['dea'])

            if i>=ma-1:
                dc[i]['ma']=sum(da[i-j][4] for j in range(ma))/ma # 移动平均值 i-ma+1,i+1
                std_pj=sum(da[i-j][4]-da[i-j][1] for j in range(ma))/ma
                dc[i]['var']=sum((da[i-j][4]-da[i-j][1]-std_pj)**2 for j in range(ma))/ma  # 方差 i-ma+1,i+1
                dc[i]['std']=float(np.sqrt(dc[i]['var'])) # 标准差

            if i>=ma-1:
                if dc[i]['macd']>=0 and dc[i-1]['macd']<0:
                    co+=1
                elif dc[i]['macd']<0 and dc[i-1]['macd']>=0:
                    co+=1
                dc[i]['reg']=co
                price=dc[i]['close']-dc[i]['open']
                std=dc[i]['std']
                if std:
                    dc[i]['mul']=round(price/std,2)

                o1 = dc[i]['open']
                h1 = dc[i]['high']
                l1 = dc[i]['low']
                c1 = dc[i]['close']
                datetimes=dc[i]['datetimes']
                is_date=(datetimes.hour==16 and datetimes.minute>=29) or datetimes.hour>16
                if abs(dc[i]['mul']) > 1.5 and body_k(o1, h1, l1, c1):  # and is_m==0:if abs(dc[i]['mul']) > 1.5 and body_k(o1, h1, l1, c1)
                    for j in range(i - 2, i - 15, -1):
                        o2 = dc[j]['open']
                        h2 = dc[j]['high']
                        l2 = dc[j]['low']
                        c2 = dc[j]['close']
                        try:
                            if abs(dc[j]['mul']) > 1.5 and (
                                    (o1 > c1 and o2 > c2) or (o1 < c1 and o2 < c2)) and body_k(o2,
                                                                                               h2,
                                                                                               l2,
                                                                                               c2):
                                # cd=[df.ix[i,'open']-df.ix[j,'open'],df.ix[i,'high']-df.ix[j,'high'],df.ix[i,'low']-df.ix[j,'low'],df.ix[i,'close']-df.ix[j,'close']]
                                if o1 < c1 and (c2 - o1) / (c1 - o2) > 0.4:# and o2 < o1 < c2 < c1:  # and o1<o2<c1 and c2>c1  or (c1 - o2) / (c2 - o1) < -0.5)
                                    if is_kc==0:
                                        is_kc=1
                                        is_d+=1
                                        cd[dc[i]['datetimes']]=cds
                                        #cds += 1
                                        break
                                elif o1 > c1 and (o1 - c2) / (o2 - c1) > 0.4:# and c1 < c2 < o1 < o2: #  or (o2 - c1) / (o1 - c2) < -0.5)
                                    if is_kc==0:
                                        is_kc=-1
                                        is_k+=1
                                        cd[dc[i]['datetimes']] = -cds
                                        #cds += 1
                                        break
                            is_kpd=(abs(dc[j]['mul']) > 1.4 and (o1 > c1 and o2 < c2 and (h1 <= h2 and l1 <= l2 or c1 <= o2)) and (o1 - o2) / (c2 - c1) > 0.4)
                            is_dpd=(abs(dc[j]['mul']) > 1.4 and (o1 < c1 and o2 > c2) and (h1 >= h2 and l1 >= l2 or c1 >= o2) and (o2 - o1) / (c1 - c2) > 0.4)
                            if is_kpd:
                                is_k += 1
                            if is_dpd:
                                is_d +=1
                            if is_date or is_kpd:
                                if is_kc>0 and ((is_k>is_d and is_k>2) or is_date):
                                    #maidian[dc[i]['datetimes']] = -cds
                                    cd[dc[i]['datetimes']] = -2
                                    is_kc=0
                                    is_k=0
                                    is_d=0
                                    break

                            if is_date or is_dpd:
                                if is_kc<0 and (( is_d>is_k and is_d>2) or is_date):
                                    #maidian[dc[i]['datetimes']] = cds
                                    cd[dc[i]['datetimes']] = 2
                                    is_kc = 0
                                    is_k = 0
                                    is_d = 0
                                    break
                        except:
                            continue
        return cd
    return macd2(da)


class Zbjs(ZB):
    def __init__(self,df):
        super(Zbjs, self).__init__()
        self.zdata = [(d[0], d[1], d[2], d[3], d[4]) for d in df.values]

    def get_doc(self,fa):
        return self.fa_doc.get(fa)

    def is_date(self,datetimes):
        ''' 是否已经或即将进入晚盘 '''
        h=datetimes.hour
        return (h==16 and datetimes.minute>=29) or h>16 or h<9

    def main2(self,_fa,_ma=60):
        res,first_time = self.trd(_fa=_fa,_ma=_ma)
        res2 = [res[i]['datetimes'] for i in res]
        buysell = {}
        for day in res2:
            for i in day:
                if i:
                    buysell[Timestamp(i[0])] = 1 if i[2] == '多' else -1
                    buysell[Timestamp(i[1])] = 2 if i[2] == '空' else -2
        return buysell

