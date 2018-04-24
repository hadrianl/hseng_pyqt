import pandas as pd


class ZB(object):
    fa_doc = {
        '1': "出现三次以上(收盘价小于60均线，价差除以标准差<-1.5）)则做多；若出现macd>0与收盘价大于60均线，或亏损大于止损价，则平仓。反之亦然。",
        '2': "若出现前阴价差除以标准差<-1.5与后阳价差除以标准差>1.5重合，则做多；若出现前阳价差除以标准差>1.5与后阴价差除以标准差<-1.5倍重合，则平仓。反之亦然。",
        '3': "收盘价小于60均线 与 价差除以标准差>1.5，则做多；若前阳价差除以标准差>1.5倍 与 后阴价差除以标准差<-1.5倍重合，则平仓。反之亦然。",
        '4': "收盘价小于60均线 与 价差除以标准差<-1.5,则做多；若macd<0 与 收盘价大于60均线,则平仓；反之亦然；",
        '5': "两个阳线出现大于1.5倍并重合，并且一阴一阳重合大于一阳一阴重合的次数，则做多；",
        "6": "",
        "z": "注：价差：收盘价与开盘价的差；",
    }
    def __init__(self):
        #self.da = [(d[0], d[1], d[2], d[3], d[4]) for d in df.values]
        self.xzfa = {'1': self.fa1, '2': self.fa2, '3': self.fa3, '4': self.fa4,'5':self.fa5,'6':self.fa6}  # 执行方案

    @property
    def zdata(self):
        return self._data

    @zdata.setter
    def zdata(self,ds):
        if isinstance(ds,pd.DataFrame):
            self._data = [(d[0], d[1], d[2], d[3], d[4]) for d in ds.values]
        elif isinstance(ds,list) or isinstance(ds,tuple):
            self._data = ds
        else:
            raise ValueError("zdata set ds,ds is not list or tuple or DataFrame! ")

    def get_doc(self,fa):
        return self.fa_doc.get(fa)

    def is_date(self,datetimes):
        ''' 是否已经或即将进入晚盘 '''
        h=datetimes.hour
        return (h==16 and datetimes.minute>=28) or h>16 or h<9

    def time_pd(self,dt1,dt2,fd=1):
        ''' 时间长度 '''
        dt1 = int(str(dt1)[11:16].replace(':',''))
        dt2 = int(dt2[11:16].replace(':',''))
        return dt1-dt2>fd

    def dt_kc(self,datetimes):
        ''' 开仓时间 '''
        h = datetimes.hour
        return (16 > h >= 9) or (h == 16 and datetimes.minute < 8)

    def sendNone(self,s):
        try:
            s.send(None)
        except:
            pass

    def vis(self,da,ma=60,short=12,long=26,phyd=9):
        ''' 各种指标初始化计算，动态计算 '''
        # da格式：((datetime.datetime(2018, 3, 19, 9, 22),31329.0,31343.0,31328.0,31331.0,249)...)
        dc=[]
        co=0
        cds=1
        def body_k(o, h, l, c):
            if abs(h - l) > 0:
                return abs(o - c) / abs(h - l) > 0.6
            else:
                return False
        for i in range(len(da)):
            dc.append({'ema_short':0,'ema_long':0,'diff':0,'dea':0,'macd':0,'ma':0,'var':0,'std':0,'reg':0,'mul':0,'datetimes':da[i][0],'open':da[i][1],'high':da[i][2],'low':da[i][3],'close':da[i][4],'cd':0,'maidian':0})
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
                dc[i]['std']=float(dc[i]['var']**0.5) # 标准差

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
                if abs(dc[i]['mul']) > 1.5 and body_k(o1, h1, l1, c1):
                    for j in range(i - 2, i - 15, -1):
                        o2 = dc[j]['open']
                        h2 = dc[j]['high']
                        l2 = dc[j]['low']
                        c2 = dc[j]['close']
                        try:
                            if abs(dc[j]['mul']) > 1.5 and ((o1 > c1 and o2 > c2) or (o1 < c1 and o2 < c2)) and body_k(o2, h2, l2, c2):
                                if o1 < c1:
                                    if dc[j]['cd'] == 0 and (c2 - o1) / (c1 - o2) > 0.4 and o2 < o1 < c2 < c1:
                                        dc[i]['cd'] = cds
                                        cds += 1
                                        break
                                elif o1 > c1:
                                    if dc[j]['cd'] == 0 and (o1 - c2) / (o2 - c1) > 0.4 and c1 < c2 < o1 < o2:
                                        dc[i]['cd'] = -cds
                                        cds += 1
                                        break

                            elif abs(dc[j]['mul']) > 1.5 and (o1 > c1 and o2 < c2 and (h1 <= h2 and l1 <= l2 or c1 <= o2)):  # and body_k(o2, h2, l2,c2):
                                if (o1 - o2) / (c2 - c1) > 0.4:
                                    dc[i]['maidian'] = -cds
                                    break

                            elif abs(dc[j]['mul']) > 1.5 and (o1 < c1 and o2 > c2) and (h1 >= h2 and l1 >= l2 or c1 >= o2):  # and body_k(o2, h2, l2,c2):
                                if (o2 - o1) / (c1 - c2) > 0.4:
                                    dc[i]['maidian'] = cds
                                    break
                        except:
                            continue

        data=1 # data future is list
        while data:
            data=yield dc
            ind=len(dc)
            if isinstance(data,tuple) or isinstance(data,list):
                dc.append({'ema_short':0,'ema_long':0,'diff':0,'dea':0,'macd':0,'ma':0,'var':0,'std':0,'reg':0,'mul':0,'datetimes':data[0],'open':data[1],'high':data[2],'low':data[3],'close':data[4],'cd':0,'maidian':0})
                try:
                    dc[ind]['ema_short'] = dc[ind-1]['ema_short'] * (short-2) / short + dc[ind]['close'] * 2 / short  # 当日EMA(12)
                    dc[ind]['ema_long'] = dc[ind-1]['ema_long'] * (long-2) / long + dc[ind]['close'] * 2 / long  # 当日EMA(26)
                    dc[ind]['diff'] = dc[ind]['ema_short'] - dc[ind]['ema_long']
                    dc[ind]['dea'] = dc[ind-1]['dea'] * (phyd-2) / phyd + dc[ind]['diff'] * 2 / phyd
                    dc[ind]['macd'] = 2 * (dc[ind]['diff'] - dc[ind]['dea'])

                    dc[ind]['ma']=sum(dc[ind-j]['close'] for j in range(ma))/ma # 移动平均值
                    std_pj=sum(dc[ind-j]['close']-dc[ind-j]['open']  for j in range(ma))/ma
                    dc[ind]['var']=sum((dc[ind-j]['close']-dc[ind-j]['open']-std_pj)**2 for j in range(ma))/ma # 方差
                    dc[ind]['std']=float(dc[ind]['var']**0.5) # 标准差
                except Exception as exc:
                    print(exc)

                if dc[ind]['macd']>=0 and dc[ind-1]['macd']<0:
                    co+=1
                elif dc[ind]['macd']<0 and dc[ind-1]['macd']>=0:
                    co+=1
                dc[ind]['reg']=co
                price=dc[ind]['close']-dc[ind]['open']
                std=dc[ind]['std']
                if std:
                    dc[ind]['mul']=round(price/std,2)

                o1 = dc[ind]['open']
                h1 = dc[ind]['high']
                l1 = dc[ind]['low']
                c1 = dc[ind]['close']
                if abs(dc[ind]['mul']) > 1.5 and body_k(o1, h1, l1, c1):
                    for j in range(ind - 1, ind - 12, -1):
                        o2 = dc[j]['open']
                        h2 = dc[j]['high']
                        l2 = dc[j]['low']
                        c2 = dc[j]['close']
                        try:
                            mul_15 = abs(dc[j]['mul'])
                            if mul_15 > 1.5 and ((o1 > c1 and o2 > c2) or (o1 < c1 and o2 < c2)) and body_k(
                                    o2, h2, l2, c2):
                                if o1 < c1:
                                    if dc[j]['cd'] == 0 and (c2 - o1) / (c1 - o2) > 0.4:
                                        dc[ind]['cd'] = cds
                                        cds += 1
                                        break
                                elif o1 > c1:
                                    if dc[j]['cd'] == 0 and (o1 - c2) / (o2 - c1) > 0.4:
                                        dc[ind]['cd'] = -cds
                                        cds += 1
                                        break
                            elif mul_15 > 1.5 and (o1 > c1 and o2 < c2 and (h1 <= h2 and l1 <= l2 or c1 <= o2)):  # and body_k(o2, h2, l2,c2):
                                if (o1 - o2) / (c2 - c1) > 0.4:
                                    dc[ind]['maidian'] = -cds
                                    break

                            elif mul_15 > 1.5 and (o1 < c1 and o2 > c2) and (h1 >= h2 and l1 >= l2 or c1 >= o2):  # and body_k(o2, h2, l2,c2):
                                if (o2 - o1) / (c1 - c2) > 0.4:
                                    dc[ind]['maidian'] = cds
                                    break
                        except Exception as exc:
                            continue
            else:
                print('data不是tuple',type(data),data)

    def dynamic_index(self,data,_ma=60,zsjg=-100):
        ''' 动态交易指标 '''
        res={}
        is_d=0
        is_k=0
        #conn=get_conn('carry_investment')
        #sql='SELECT a.datetime,a.open,a.high,a.low,a.close FROM futures_min a INNER JOIN (SELECT DATETIME FROM futures_min ORDER BY DATETIME DESC LIMIT 0,{})b ON a.datetime=b.datetime'.format(_ma)
        #data=getSqlData(conn,sql)
        data2=self.vis(da=data,ma=_ma)
        dt2=data2.send(None)
        data=1
        while data:
            data=yield res
            dates=data[0]
            res[dates]={'duo':0,'kong':0,'mony':0,'datetimes':[],'dy':0,'xy':0}
            #str_time1=None if is_d==0 else str_time1
            #str_time2=None if is_k==0 else str_time2
            jg_d=0 if is_d==0 else jg_d
            jg_k=0 if is_k==0 else jg_k
            is_dk = not (is_k or is_d)
            # data格式：(datetime.datetime(2018, 3, 26, 20, 19), 30606.0, 30610.0, 30592.0, 30597.0)
            dt2=data2.send(data)[-1:][0]

            datetimes,clo,macd,mas,std,reg,mul=dt2['datetimes'],dt2['close'],dt2['macd'],dt2['ma'],dt2['std'],dt2['reg'],dt2['mul']
            # if mul>1.5:
            #     res[dates]['dy']+=1
            # if mul<-1.5:
            #     res[dates]['xy']+=1
            if clo < mas and mul < -1.5 and is_dk and self.dt_kc(datetimes):
                jg_d=clo
                str_time1 = str(datetimes)
                res[dates]['datetimes'].append([str_time1,1])
                is_d=1
            elif clo > mas and mul > 1.5 and is_dk and self.dt_kc(datetimes):
                jg_k=clo
                str_time2 = str(datetimes)
                res[dates]['datetimes'].append([str_time2,-1])
                is_k=-1
            if is_d==1 and ((macd<0 and clo>mas) or clo-jg_d<zsjg or self.is_date(datetimes)):
                if self.time_pd(str(datetimes),str_time1,3):
                    res[dates]['duo']+=1
                    res[dates]['mony']+=(clo-jg_d)
                    res[dates]['datetimes'].append([str(datetimes),2])
                    is_d=0
            elif is_k == -1 and ((macd > 0 and clo < mas) or jg_k - clo < zsjg or self.is_date(datetimes)):
                if self.time_pd(str(datetimes), str_time2, 3):
                    res[dates]['kong']+=1
                    res[dates]['mony']+=(jg_k-clo)
                    res[dates]['datetimes'].append([str(datetimes),-2])
                    is_k=0
        self.sendNone(data2)

    def fa1(self,cqdc=6):
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        tj_d=0
        tj_k=0
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high,low = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            if clo<mas and mul<-1.5 and is_dk and 9<datetimes.hour<16:
                tj_d+=1
                if tj_d>3:
                    jg_d=clo
                    startMony_d=clo
                    str_time1=str(datetimes)
                    is_d=1
                    first_time = [str_time1,'多']
            elif clo>mas and mul>1.5 and is_dk and 9<datetimes.hour<16:
                tj_k+=1
                if tj_k>3:
                    jg_k=clo
                    startMony_k=clo
                    str_time2=str(datetimes)
                    is_k=-1
                    first_time = [str_time2, '空']
            if is_d==1 and ((macd>0 and clo>mas) or self.is_date(datetimes) or clo - startMony_d<-80):
                # if clo - jg_d < 50 or self.is_date(datetimes):
                res[dates]['duo'] += 1
                res[dates]['mony'] += (clo - jg_d-cqdc)
                res[dates]['datetimes'].append([str_time1, str(datetimes), '多', clo - startMony_d-cqdc])
                is_d = 0
                first_time = []
                tj_d=0
                # elif clo - jg_d > 60:
                #     res[dates]['mony'] += (clo - jg_d)
                #     jg_d = clo
            elif is_k==-1 and ((macd<0 and clo<mas) or self.is_date(datetimes) or startMony_k - clo<-80):
                #if jg_k - clo < 50 or self.is_date(datetimes):
                res[dates]['kong'] += 1
                res[dates]['mony'] += (jg_k - clo-cqdc)
                res[dates]['datetimes'].append([str_time2, str(datetimes), '空', startMony_k - clo-cqdc])
                is_k = 0
                first_time = []
                tj_k=0
                # elif jg_k - clo > 60:
                #     res[dates]['mony'] += (jg_k - clo)
                #     jg_k = clo

    def fa2(self,cqdc=6):
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, maidian = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['maidian']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            if maidian > 0 and is_dk and self.dt_kc(datetimes):
                res[dates]['duo'] += 1
                jg_d = clo
                startMony_d=clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str_time1, '多']
            elif maidian < 0 and is_dk and self.dt_kc(datetimes):
                res[dates]['kong'] += 1
                jg_k = clo
                startMony_k=clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str_time2, '空']
            if is_d == 1 and (maidian<0 or self.is_date(datetimes) or clo - startMony_d<-80):
                res[dates]['mony'] += (clo - startMony_d-cqdc)
                res[dates]['datetimes'].append([str_time1, str(datetimes), '多', clo - startMony_d-cqdc])
                is_d = 0
                first_time = []
            elif is_k == -1 and (maidian>0 or self.is_date(datetimes) or startMony_k-clo<-80):
                res[dates]['mony'] += (startMony_k - clo-cqdc)
                res[dates]['datetimes'].append([str_time2, str(datetimes), '空', startMony_k - clo-cqdc])
                is_k = 0
                first_time = []

    def fa3(self,cqdc=6,zsjg=-60):
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, maidian = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['maidian']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            if clo<mas and mul>1.5 and is_dk and self.dt_kc(datetimes):
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1, '多']
            elif clo>mas and mul<-1.5 and is_dk and self.dt_kc(datetimes):
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空']
            if is_d==1 and (maidian>0 or self.is_date(datetimes) or clo-startMony_d<zsjg):  # macd<dt3[-2]['macd']
                #if clo-jg_d<0:
                if self.time_pd(datetimes,str_time1,2):
                    res[dates]['duo']+=1
                    res[dates]['mony']+=(clo-jg_d-cqdc)
                    res[dates]['datetimes'].append([str_time1, str(datetimes),'多',clo-startMony_d-cqdc])
                    is_d=0
                    first_time = []

            elif is_k==-1 and (maidian<0 or self.is_date(datetimes) or startMony_k-clo<zsjg): # macd>dt3[-2]['macd']
                #if jg_k-clo<0:
                if self.time_pd(datetimes,str_time2,2):
                    res[dates]['kong']+=1
                    res[dates]['mony']+=(jg_k-clo-cqdc)
                    res[dates]['datetimes'].append([str_time2,str(datetimes),'空',startMony_k-clo-cqdc])
                    is_k=0
                    first_time = []

    def fa4(self,cqdc=6,zsjg=-100):
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0
            if clo<mas and mul<-1.5 and is_dk and self.dt_kc(datetimes):
                res[dates]['duo'] += 1
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1, '多']
            elif clo>mas and mul>1.5 and is_dk and self.dt_kc(datetimes):
                res[dates]['kong'] += 1
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空']
            if is_d==1 and ((macd<0 and clo>mas) or clo-startMony_d<zsjg or self.is_date(datetimes)):
                if self.time_pd(str(datetimes),str_time1,3):
                    res[dates]['mony']+=(clo-jg_d-cqdc)
                    res[dates]['datetimes'].append([str_time1,str(datetimes),'多',clo-startMony_d-cqdc])
                    is_d=0
                    first_time = []

            elif is_k==-1 and ((macd>0 and clo<mas) or startMony_k-clo<zsjg or self.is_date(datetimes)):
                if self.time_pd(str(datetimes), str_time2, 3):
                    res[dates]['mony']+=(jg_k-clo-cqdc)
                    res[dates]['datetimes'].append([str_time2,str(datetimes),'空',startMony_k-clo-cqdc])
                    is_k=0
                    first_time = []

    def fa5(self,cqdc=6,zsjg=-80):
        up_c,down_c=0,0
        startMony_d,startMony_k=0,0
        str_time1,str_time2='',''
        is_d,is_k=0,0
        res={}
        first_time=[]
        _high=None
        _low=None
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd ,maidian,high,low= dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['maidian'],dt2['high'],dt2['low']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0
            up_c += 1 if (cd > 0 or maidian > 0) else 0 # 上涨提示次数
            down_c += 1 if (cd < 0 or maidian < 0) else 0 # 下跌提示次数

            judge_d=(up_c>down_c and up_c>2) # 做多与平多仓的判断
            judge_k=(down_c>up_c and down_c>2) # 做空与平空仓的判断
            if cd > 0 and is_dk and judge_d and self.dt_kc(datetimes):
                jg_d = clo
                startMony_d=clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time=[str(datetimes), '多']
                _high = high

            elif cd < 0 and is_dk and judge_k and self.dt_kc(datetimes):
                jg_k = clo
                startMony_k=clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str(datetimes), '空']
                _low = low

            if is_d == 1 and ( maidian<0 or self.is_date(datetimes) or clo - startMony_d-cqdc<zsjg):
                # res[dates]['mony'] += (clo - startMony_d)
                # res[dates]['datetimes'].append([str_time1, str(datetimes), '多', clo - startMony_d])
                # is_d = 0
                # up_c = 0
                # down_c = 0
                #if clo - jg_d < 50 or self.is_date(datetimes):
                res[dates]['duo'] += 1
                res[dates]['mony'] += (clo - jg_d-cqdc)
                res[dates]['datetimes'].append([str_time1, str(datetimes), '多', clo - startMony_d-cqdc])
                is_d = 0
                up_c = 0
                down_c = 0
                first_time = []
                # elif clo - jg_d > 60:
                #     res[dates]['mony'] += (clo - jg_d)
                #     jg_d = clo

            elif is_k == -1 and (maidian>0 or self.is_date(datetimes) or startMony_k - clo<zsjg):
                # res[dates]['mony'] += (startMony_k - clo)
                # res[dates]['datetimes'].append([str_time2, str(datetimes), '空', startMony_k - clo])
                # is_k = 0
                # up_c = 0
                # down_c = 0
                #if jg_k - clo < 50 or self.is_date(datetimes):
                res[dates]['kong'] += 1
                res[dates]['mony'] += (jg_k - clo-cqdc)
                res[dates]['datetimes'].append([str_time2, str(datetimes), '空', startMony_k - clo-cqdc])
                is_k = 0
                up_c = 0
                down_c = 0
                first_time = []
                # elif jg_k - clo > 60:
                #     res[dates]['mony'] += (jg_k - clo)
                #     jg_k = clo

    def fa6(self,cqdc=6,zsjg=60):
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            judge_d = clo<mas and mul<-1.5  # 做多与平空仓的判断
            judge_k = clo>mas and mul>1.5  # 做空与平多仓的判断
            if judge_d and is_dk and 9<datetimes.hour<16:
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1,'多']
            if judge_k and is_dk and 9<datetimes.hour<16:
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空']

            if is_d==1 and ((macd>0 and clo>mas) or self.is_date(datetimes) or judge_k):
                if clo - jg_d < zsjg and self.time_pd(datetimes,str_time1,1) or self.is_date(datetimes):
                    res[dates]['duo'] += 1
                    res[dates]['mony'] += (clo - jg_d-cqdc)
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', clo - startMony_d-cqdc])
                    is_d = 0
                    first_time = []
                elif clo - jg_d > zsjg:
                    res[dates]['mony'] += (clo - jg_d)
                    jg_d = clo
            if is_k==-1 and ((macd<0 and clo<mas) or self.is_date(datetimes) or judge_d):
                if jg_k - clo < zsjg and self.time_pd(datetimes,str_time2,1) or self.is_date(datetimes):
                    res[dates]['kong'] += 1
                    res[dates]['mony'] += (jg_k - clo-cqdc)
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', startMony_k - clo-cqdc])
                    is_k = 0
                    first_time = []
                elif jg_k - clo > zsjg:
                    res[dates]['mony'] += (jg_k - clo)
                    jg_k = clo

    def trd(self,_fa,_ma=60):
        ''' 交易记录 '''
        res={}
        da = self.zdata
        if len(da)>_ma:
            data2=self.vis(da=da[:_ma],ma=_ma)
            data2.send(None)
            da=da[_ma:]
            fa = self.xzfa[_fa]()
            fa.send(None)
        else:
            return
        for df2 in da:
            # df2格式：(Timestamp('2018-03-16 09:22:00') 31304.0 31319.0 31295.0 31316.0 275)
            dates=str(df2[0])[:10]
            if dates not in res:
                res[dates] = {'duo': 0, 'kong': 0, 'mony': 0, 'datetimes': [], 'dy': 0, 'xy': 0, 'ch': 0}
            dt3=data2.send(df2)
            datetimes=dt3[-1]['datetimes']
            if ((datetimes.hour==16 and datetimes.minute>30) or datetimes.hour>16 or datetimes.hour<9):
                continue
            res,first_time=fa.send((True,res,dt3,dates))

        #self.sendNone(data2)
        #self.sendNone(fa)
        return res,first_time
