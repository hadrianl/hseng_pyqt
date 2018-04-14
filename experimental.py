#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/13 0013 13:14
# @Author  : Hadrianl 
# @File    : experimental.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import numpy as np
import matplotlib.pyplot as plt
from util import S_logger

def normalize_test(ohlc, b):
    increase = (ohlc.close - ohlc.open).rename('increase')
    Count = increase.count()
    Mean = increase.mean()
    Std = increase.std()
    Skew = increase.skew()
    Kurt = increase.kurt()
    Max = increase.max()
    IdxMax = increase.idxmax()
    Min = increase.min()
    IdxMin = increase.idxmin()

    S_logger.info(f'\n'
                  f'#-----描述统计--------#\n'
                  f'<{increase.index[0]}>至<{increase.index[-1]}>\n'
                  f'K线数量:{Count}\n'
                  f'均值:{Mean:.2f}\n'
                  f'标准差:{Std:.2f}\n'
                  f'偏度:{Skew:.2f}\n'
                  f'峰度:{Kurt:.2f}\n'
                  f'最大值:{Max}@<{IdxMax}>\n'
                  f'最小值:{Min}@<{IdxMin}>\n'
                  f'#---------------------#')
    plt.hist(increase, bins=b, normed=True)
    plt.show()