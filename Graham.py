# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tushare as ts
import pandas as pd
import time
import urllib

#0-初始化参数
fs='E:\\stock\\'

fss='E:\\stock\\report\\'
#报告最新日期为获取当前日期
End_date=time.strftime('%Y%m%d',time.localtime(time.time()))


#0-1初始化Pro
ts.set_token('64bf4e6723f884d0f595bd46c4aca3d35a78af9d584b791be4af9338')
pro = ts.pro_api()

#1-获取股票基本情况表
SZdata_basic = pro.stock_basic(exchange_id='', is_hs='S', fields='ts_code,symbol,name,list_date,list_status')
#SHdata_basic = pro.stock_basic(exchange_id='', is_hs='H', fields='ts_code,symbol,name,list_date,list_status')

data_basic = pro.stock_basic(exchange_id='', fields='ts_code,symbol,name,list_date,list_status')

#data_basic.to_excel(fss+'stock_basic.xls')
#data_basic= pd.read_excel(fss+'stock_basic.xls')
codes= data_basic.ts_code
data_basic=data_basic.set_index(data_basic.ts_code)

bcode='300001.SZ'
code=''
#2-按基本情况表获取财务三大报表
flag=True
while flag:
    try:
        for code in codes:
#            print('正在下载'+code+'利润表')
#            lrb = pro.income(ts_code=code, start_date=str(data_basic.loc[code,'list_date']), end_date=End_date)
#            lrb.to_excel(fss+code+'-lrb.xls')
#            print('完成')
            print('正在下载'+code+'资产负债表')
            fzb = pro.balancesheet(ts_code=code, start_date=str(data_basic.loc[code,'list_date']), end_date=End_date)
            fzb.to_excel(fss+code+'-fzb.xls')
            print('完成')
#            print('正在下载'+code+'现金流量表')
#            llb = pro.cashflow(ts_code=code, start_date=str(data_basic.loc[code,'list_date']), end_date=End_date)
#            llb.to_excel(fss+code+'-llb.xls')
#            print('完成')
            bcode =code
            codes= codes[codes > bcode]
            if len(codes)==0:
                flag =False
        
        
#2-e下载超时的异常处理        
    except urllib.URLError:
        
        codes= codes[codes >= bcode]
        time.sleep(30)
        continue



#3-获取当日K线信息
End_date = '20180823'

print('正在下载'+End_date+'日线信息')
dayK = pro.daily(trade_date=End_date)
dayK.to_excel(fs+End_date+'-dailyK.xls')
print('完成')
        
        
        
#3-替 获取指定股的历史K线信息

for code in codes:
        print('正在下载'+code+'日线信息')
        rx = pro.daily(ts_code=code, start_date=data_basic.loc[code,'list_date'], end_date=End_date)
        rx.to_excel(fs+code+'-rx.xls')
        print('完成')
                
        

#4-清算估值函数
#改进的算法(跟格雷厄姆是一样的，不过更加方便快捷合理)：
def Qingsuan(fss,code):
    data = pd.read_excel(fss+code+'-fzb.xls')
    

    data = data.fillna(0)
#1.最新季度应收账款(包括其他应收款)x0.2
    YS=(data.loc[0,'accounts_receiv'] + data.loc[0,'oth_receiv'] ) * 0.2
#2.最新季度存货x行业前景
    #行业前景： 好=0.2 一般=0.3 差=0.4
    CH=data.loc[0,'inventories']  * 0.3
#3.最新季度固定资产x0.6
    GDZC=data.loc[0,'fix_assets'] * 0.6
    
#4.无形资产x1
    WXZC=data.loc[0,'intan_assets']
#最新季度股东权益(净资产)减去四项的和，得到企业清算价值。
    QS = data.loc[0,'total_hldr_eqy_inc_min_int']-YS-CH-GDZC-WXZC
#每股清算价值=(最新季度股东权益减去四项的和)除以总股本。
    MGQS = QS / data.loc[0,'total_share'] 
    return MGQS    

   
#Qingsuan(fss,code)        
    
results= dayK.iloc[:,:7]

del results['trade_date']
del results['high']
del results['low']


#5-构建清算价格表
QSre = pd.DataFrame(columns=['ts_code','QS'])
for code in dayK.ts_code:
    QSre.loc[code]=code,Qingsuan(fss,code)



#6-合并价格表
HB=pd.merge(results,QSre,on='ts_code')

QSB=HB[HB.close<HB.QS]
QSB['QSCR']=QSB.close/QSB.QS
QSB.to_excel(fs +'QS1111.xls')





