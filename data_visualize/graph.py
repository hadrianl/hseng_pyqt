#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/10 0010 15:55
# @Author  : Hadrianl 
# @File    : graph.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
from util import V_logger, MA_COLORS
import pandas as pd
import numpy as np
from PyQt5.Qt import  QBrush, QColor
from data_visualize.baseitems import graph_base, TradeDataScatter, TradeDataLinkLine, CandlestickItem
import pyqtgraph as pg
from collections import Iterable

class Graph_OHLC(graph_base):
    def __init__(self, plts:Iterable):
        super(Graph_OHLC, self).__init__(plts, 'OHLC')

    def _init(self, p, ohlc):
        self.ohlc = ohlc
        plt = self.plts[p]
        plt_item = self.plt_items[p]
        plt_item['ohlc'] = CandlestickItem()
        plt_item['tick'] = CandlestickItem()
        plt_item['hline'] = self.plt_items[p]['tick'].hline
        plt_item['tick'].mark_line()
        plt.addItem(plt_item['ohlc'])
        plt.addItem(plt_item['tick'])
        plt.addItem(plt_item['hline'])
        self.add_info_text(p, anchor=(0, 0))

    def _update(self, p, ohlc):
        self.ohlc = ohlc
        item = self.plt_items[p]
        item['ohlc'].setHisData(ohlc)

    def _deinit(self, p):
        item = self.plt_items[p]
        plt = self.plts[p]
        for _, v in item.items():
            plt.removeItem(v)

    def info_text(self, p, *args, **kwargs):
        if 'x_index' in kwargs:
            x_index = kwargs['x_index']
            text_df = self.ohlc.data.iloc[x_index]
            ohlc_text = f"""
                            <span style="color:white;font-size:12px"><span/><span style="color:blue">{str(text_df.name)[8:16].replace(" ", "日")}<span/><br/>
                            <span style="color:white;font-size:12px">开:<span/><span style="color:red">{text_df.open}<span/><br/>
                            <span style="color:white;font-size:12px">高:<span/><span style="color:red">{text_df.high}<span/><br/>
                            <span style="color:white;font-size:12px">低:<span/><span style="color:red">{text_df.low}<span/><br/>
                            <span style="color:white;font-size:12px">收:<span/><span style="color:red">{text_df.close}<span/>
                            """
            return ohlc_text
        else:
            return ''


class Graph_MA(graph_base):
    def __init__(self, plts, colors=None):
        super(Graph_MA, self).__init__(plts, 'MA')
        self.colors = colors if colors else MA_COLORS
        self.plt_texts = {}

    def _init(self, p, ohlc, i_ma):
        plt = self.plts[p]
        item = self.plt_items[p]
        for w in i_ma._windows:
            item[w] = pg.PlotDataItem(pen=pg.mkPen(color=self.colors.get(w, 'w'), width=1))
            plt.addItem(item[w])
        self.add_info_text(p, anchor=(1, 0), pos=(0, 1, 1, 1))

    def _update(self, p, ohlc, i_ma):
        x = ohlc.x
        item = self.plt_items[p]
        for w in item:
            item[w].setData(x, getattr(i_ma, w).values)

    def _deinit(self,p):
        plt = self.plts[p]
        item = self.plt_items[p]
        for _, v in item.items():
            plt.removeItem(v)
        self.del_info_text(p)

    def info_text(self, p, *args, **kwargs):
        if 'x_index' in kwargs:
            x_index = kwargs['x_index']
            item = self.plt_items[p]
            ma_text = [
                f'<span style="color:rgb{MA_COLORS[k]};font-size:12px">MA{k[-2:]}:{round(v.yData[x_index],2)}<span/>'
                for k, v in item.items()]
            return '  '.join(ma_text)
        else:
            return ''


class Graph_MACD(graph_base):
    def __init__(self, plts, macd_colors=('g', 'y', 'b', 'r'), diff_colors='y', dea_colors='w'):
        super(Graph_MACD, self).__init__(plts, 'MACD')
        self.macd_colors_map = {i:v for i,v in enumerate(macd_colors)}
        self.diff_colors = diff_colors
        self.dea_colors = dea_colors

    def _init(self, p, ohlc, i_macd):
        plt = self.plts[p]
        item = self.plt_items[p]
        item['MACD'] = pg.BarGraphItem(x=[0], height=[0], width=0.5)
        item['diff'] = pg.PlotDataItem(pen=self.diff_colors)
        item['dea'] = pg.PlotDataItem(pen=self.dea_colors)
        plt.addItem(item['MACD'])
        plt.addItem(item['diff'])
        plt.addItem(item['dea'])
        self.add_info_text(p, anchor=(0, 0), pos=(0, 0, 1, 1))

    def _update(self, p, ohlc, i_macd):
        x = i_macd.x
        diff = i_macd.diff
        dea = i_macd.dea
        macd = i_macd.macd
        item = self.plt_items[p]
        item['diff'].setData(x, diff.values)
        item['dea'].setData(x, dea.values)
        macd_pens = pd.concat(
            [ohlc.close > ohlc.open, macd > 0], 1).apply(
            lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map(self.macd_colors_map)
        macd_brushes = [None if (macd > macd.shift(1))[i]
                        else v for i, v in macd_pens.iteritems()]
        item['MACD'].setOpts(x=x, height=macd, pens=macd_pens, brushes=macd_brushes)

    def _deinit(self, p):
        plt = self.plts[p]
        item = self.plt_items[p]
        for _, v in item.items():
            plt.removeItem(v)
        self.del_info_text(p)

    def info_text(self, p, *args, **kwargs):
        if 'x_index' in kwargs:
            x_index = kwargs['x_index']
            item = self.plt_items[p]
            macd_text = f'<span style="color:red">MACD:{round(item["MACD"].opts["height"][x_index], 2)}<span/>  ' \
                        f'<span style="color:yellow">DIFF:{round(item["diff"].yData[x_index], 2)}<span/>  ' \
                        f'<span style="color:white">DEA:{round(item["dea"].yData[x_index], 2)}<span/>  '

            return macd_text
        else:
            return ''


class Graph_MACD_HL_MARK(graph_base):
    def __init__(self, plts, high_color='#FF0000', low_color='#7CFC00'):
        super(Graph_MACD_HL_MARK, self).__init__(plts, 'MACD_HL_MARK')
        self.high_color = high_color
        self.low_color = low_color
        self._crosshair_text = False

    def _init(self, p, ohlc, h_macd_hl_mark):
        item = self.plt_items[p]
        item['high_pos'] = []
        item['low_pos'] = []

    def _update(self,p, ohlc, h_macd_hl_mark):
        x = ohlc.x
        plt = self.plts[p]
        item = self.plt_items[p]
        for i in item['high_pos']:
            plt.removeItem(i)
        for i in item['low_pos']:
            plt.removeItem(i)
        item['high_pos'].clear()
        item['low_pos'].clear()
        for k, v in h_macd_hl_mark.high_pos.iteritems():
            textitem = pg.TextItem(html=f'<span style="color:{self.high_color};font-size:11px">{v}<span/>',
                                   border=pg.mkPen({'color': self.high_color, 'width': 1}),
                                   angle=15, anchor=(0, 1))
            textitem.setPos(x[k], v)
            plt.addItem(textitem)
            item['high_pos'].append(textitem)

        for k, v in h_macd_hl_mark.low_pos.iteritems():
            textitem = pg.TextItem(html=f'<span style="color:{self.low_color};font-size:11px">{v}<span/>',
                                   border=pg.mkPen({'color': self.low_color, 'width': 1}),
                                   angle=-15, anchor=(0, 0))
            textitem.setPos(x[k], v)
            plt.addItem(textitem)
            item['low_pos'].append(textitem)

    def _deinit(self, p):
        plt = self.plts[p]
        item = self.plt_items[p]
        for _, v in item.items():
            for i in v:
                plt.removeItem(i)


class Graph_STD(graph_base):
    def __init__(self, plts, inc_colors=('g', 'y', 'l', 'b', 'r'), pos_std_color='r', neg_std_color='g'):
        super(Graph_STD, self).__init__(plts, 'STD')
        self.inc_colors = inc_colors
        self.pos_std_color = pos_std_color
        self.neg_std_color = neg_std_color

    def _init(self,p, ohlc, i_std):
        plt = self.plts[p]
        item = self.plt_items[p]
        item['inc'] = pg.BarGraphItem(x=[0], height=[0], width=0.5)  # 初始化给个0参数，不给不能additem
        item['pos_std'] = pg.PlotDataItem(pen=self.pos_std_color)
        item['neg_std'] = pg.PlotDataItem(pen=self.neg_std_color)
        item['ratio'] = pg.PlotDataItem()
        plt.addItem(item['inc'])
        plt.addItem(item['pos_std'])
        plt.addItem(item['neg_std'])
        self.add_info_text(p, anchor=(0, 0), pos=(0, 0, 1, 1))

    def _update(self, p, ohlc, i_std):
        x = ohlc.x
        inc = i_std.inc
        std = i_std.std
        pos_std = i_std.pos_std
        neg_std = i_std.neg_std
        ratio = i_std.ratio
        item = self.plt_items[p]
        std_inc_pens = pd.cut((inc / std).fillna(0), [-np.inf, -2, -1, 1, 2, np.inf],
                              labels=self.inc_colors)
        inc_gt_std = (inc.abs() / std) > 1
        std_inc_brushes = np.where(inc_gt_std, std_inc_pens, None)
        item['pos_std'].setData(x, pos_std)
        item['neg_std'].setData(x, neg_std)
        item['ratio'].setData(x, ratio)
        item['inc'].setOpts(x=x, height=inc, pens=std_inc_pens, brushes=std_inc_brushes)

    def _deinit(self, p):
        plt = self.plts[p]
        item = self.plt_items[p]
        for _, v in item.items():
            plt.removeItem(v)
        self.del_info_text(p)

    def info_text(self, p, *args, **kwargs):
        if 'x_index' in kwargs:
            x_index = kwargs['x_index']
            item = self.plt_items[p]
            std_text = f'<span style="color:yellow">INC:{round(item["inc"].opts["height"][x_index], 2)}<span/> ' \
                       f'<span style="color:red">POS_STD:{round(item["pos_std"].yData[x_index], 2)}<span/> ' \
                       f'<span style="color:green">NEG_STD:{round(item["neg_std"].yData[x_index], 2)}<span/> ' \
                       f'<span style="color:white">RATIO:{round(item["ratio"].yData[x_index], 2)}<span/> '

            return std_text
        else:
            return ''


class Graph_Trade_Data_Mark(graph_base):
    def __init__(self, plts, long_symbol='t1', short_symbol='t'):
        super(Graph_Trade_Data_Mark, self).__init__(plts, 'Trade_Data')
        self.long_symbol = long_symbol
        self.short_symbol = short_symbol
        self._crosshair_text = False

    def _init(self, p, ohlc, trade_data):
        item = self.plt_items[p]
        plt = self.plts[p]
        item['open'] = TradeDataScatter()
        item['close'] = TradeDataScatter()
        item['link_line'] = TradeDataLinkLine(pen=pg.mkPen('w', width=1))
        plt.addItem(item['open'])
        plt.addItem(item['close'])
        plt.addItem(item['link_line'])
        self.add_info_text(p, anchor=(1, 1), pos=(0, 1, 1, 0))

    # --------------------------------添加交易数据-----------------------------------------------------------------
    def _update(self, p, ohlc, trade_data):
        x = ohlc.x
        U = self.long_symbol
        D = self.short_symbol
        item = self.plt_items[p]
        try:
            item['open'].setData(x=x.reindex(trade_data.open.index.floor(ohlc.ktype)),
                                 y=trade_data['OpenPrice'],
                                 symbol=[U if t == 0 else D for t in trade_data['Type']],
                                 brush=trade_data['Status'].map({2: pg.mkBrush(QBrush(QColor(0, 0, 255))),
                                                                 1: pg.mkBrush(QBrush(QColor(255, 0, 255))),
                                                                 0: pg.mkBrush(QBrush(QColor(255, 255, 255)))}).tolist(),size=5)
        except Exception as e:
            V_logger.error(f'初始化交易数据标记TradeDataScatter-open失败')
        try:
            item['close'].setData(x=x.reindex(trade_data.close.index.floor(ohlc.ktype)),
                                  y=trade_data['ClosePrice'],symbol=[D if t == 0 else U for t in trade_data['Type']],
                                  brush=trade_data['Status'].map({2: pg.mkBrush(QBrush(QColor(255, 255, 0))),
                                                                  1: pg.mkBrush(QBrush(QColor(255, 0, 255))),
                                                                  0: pg.mkBrush(QBrush(QColor(255, 255, 255)))}).tolist(),size=5)
        except Exception as e:
            V_logger.error(f'初始化交易数据标记TradeDataScatter-open失败')

        # -------------------------------------------------------------------------------------------------------------
        def link_line(a, b):
            trade_data = ohlc.Trade_Data
            if a is item['open']:
                for i, d in enumerate(item['open'].data):
                    if b[0].pos().x() == d[0] and b[0].pos().y() == d[1]:
                        index = i
                        break
            elif a is item['close']:
                for i, d in enumerate(item['close'].data):
                    if b[0].pos().x() == d[0] and b[0].pos().y() == d[1]:
                        index = i
                        break

            open_x = item['open'].data[index][0]
            open_y = item['open'].data[index][1]
            open_symbol = item['open'].data[index][3]  # open_symbol来区别开仓平仓
            if trade_data["Status"].iloc[index] == 2:
                close_x = item['close'].data[index][0]
                close_y = item['close'].data[index][1]
            else:
                close_x = item['close'].data[index][0]
                close_y = ohlc._last_tick.Price if ohlc._last_tick else ohlc.data.iloc[-1]['close']
            profit = round(close_y - open_y, 2) if open_symbol == "t1" else round(open_y - close_y, 2)
            pen_color_type = ((open_symbol == 't1') << 1) + (open_y < close_y)
            pen_color_map_dict = {0: 'r', 1: 'g', 2: 'g', 3: 'r'}
            item['link_line'].setData([[open_x, open_y],
                                       [close_x, close_y]],
                                      pen_color_map_dict[pen_color_type])
            self.set_info_text(p, trade_data, open_y, close_y, open_symbol, profit, index)

        item['open'].sigClicked.connect(link_line)
        item['close'].sigClicked.connect(link_line)

    def _deinit(self, p):
        plt = self.plts[p]
        item = self.plt_items[p]
        for _, v in item.items():
            plt.removeItem(v)
        self.del_info_text(p)

    def info_text(self, p, *args,  **kwargs):
        try:
            trade_data, open_y, close_y, open_symbol, profit, index = args
            trade_info = f'<span style="color:white">Account:{trade_data["Account_ID"].iloc[index]}' \
                         f'<span/><br/><span style="color:blue">Open :{open_y}<span/><br/>' \
                         f'<span style="color:yellow">Close:{close_y}<span/><br/>' \
                         f'<span style="color:white">Type  :{"Long" if open_symbol == "t1" else "Short"}<span/><br/>' \
                         f'<span style="color:{"red" if profit >=0 else "green"}">Profit:{profit}<span/><br/>' \
                         f'<span style="color:"white">trader:{trade_data["trader_name"].iloc[index]}<span/>'
            return trade_info
        except Exception as e:
            return ''


class Graph_Slicer(graph_base):
    def __init__(self, plts):
        super(Graph_Slicer, self).__init__(plts, 'Slicer')
        self._crosshair_text = False

    def _init(self, p, ohlc):
        item = self.plt_items[p]
        plt = self.plts[p]
        item['close_curve'] = pg.PlotDataItem()
        item['date_region'] = pg.LinearRegionItem([1, 100])
        plt.addItem(item['close_curve'])
        plt.addItem(item['date_region'])

    def _update(self, p, ohlc):
        item = self.plt_items[p]
        item['close_curve'].setData(ohlc.x, ohlc.close)

    def _deinit(self, p):
        item = self.plt_items[p]
        for _, v in item.items():
            self.plts[p].removeItem(v)

class Graph_BuySell(graph_base):
    def __init__(self, plts, buy_symbol='t1', sell_symbol='t', buy_brush='r', sell_brush='g', size=8):
        super(Graph_BuySell, self).__init__(plts, 'BuySell')
        self.buy_symbol = buy_symbol
        self.sell_symbol = sell_symbol
        self.buy_brush = buy_brush
        self.sell_brush = sell_brush
        self.size = size
        self._crosshair_text = False

    def _init(self, p, ohlc, h_buysell):
        item = self.plt_items[p]
        plt = self.plts[p]
        item['buy'] = pg.ScatterPlotItem()
        item['sell'] = pg.ScatterPlotItem()
        plt.addItem(item['buy'])
        plt.addItem(item['sell'])

    def _update(self, p, ohlc, h_buysell):
        x = ohlc.x
        open = ohlc.open
        buy_index = h_buysell.buy_points.index
        sell_index = h_buysell.sell_points.index
        item = self.plt_items[p]
        item['buy'].setData(x=x[buy_index], y=open[buy_index],
                            symbol=self.buy_symbol, brush=self.buy_brush,
                            size=self.size)
        item['sell'].setData(x=x[sell_index], y=open[sell_index],
                             symbol=self.sell_symbol, brush=self.sell_brush,
                             size=self.size)

    def _deinit(self, p):
        item = self.plt_items[p]
        for _, v in item.items():
            self.plts[p].removeItem(v)


class Graph_COINCIDE(graph_base):
    def __init__(self,plt):
        super(Graph_COINCIDE,self).__init__(plt,'COINCIDE')

    def _init(self, p, ohlc,coincide):
        item = self.plt_items[p]
        plt = self.plts[p]
        item['cd']=TradeDataScatter()
        plt.addItem(item['cd'])

    def _update(self, p, ohlc,coincide):
        item = self.plt_items[p]
        _coincide=coincide.coincide
        _y = ohlc.low[_coincide.keys()]
        _is_du = ['t1' if i > 0 else 't' for i in _coincide.values()]
        _is_bru = [QColor(255, 0, 255) if i % 2 == 1 else QColor(0, 0, 254) for i in _coincide.values()]
        x = ohlc.x[_y.index].values
        y = (_y - 5).values
        item['cd'].setData(x=x, y=y, symbol=_is_du, size=15,
                                                 brush=_is_bru)
    def _deinit(self, p):
        item = self.plt_items[p]
        plt = self.plts[p]
        for _, v in item.items():
            #for i in v:
            plt.removeItem(v)