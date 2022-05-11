# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 18:27:17 2021

@author: harik
"""

from pathlib import Path
from freqtrade.data import history

data=history.load_data(datadir=Path('E:/madii/h_freq/freqtrade-stable/user_data/data/binance'), timeframe='1m', pairs=['XRP/USDT'])

dataframe=data['XRP/USDT'];
dataframe['buy']=0;
dataframe['TGP']=0;
dataframe['TGP']=dataframe['TGP'].astype(float)
trailing_gain_profit_percent=0.05;
trailing_gain_profit=None;
for i in range(len(dataframe)):
    current_price=dataframe.loc[i]['open'] 
    new_trailing_gain_profit=current_price + float (current_price* abs(trailing_gain_profit_percent))
    if i==0 or trailing_gain_profit is None:
        trailing_gain_profit=new_trailing_gain_profit
    else:
        if new_trailing_gain_profit<trailing_gain_profit:
            trailing_gain_profit=new_trailing_gain_profit;
    if trailing_gain_profit is not None and trailing_gain_profit< current_price:
        dataframe.at[i,'buy']=1
        dataframe.at[i,'TGP']=trailing_gain_profit;