

from pathlib import Path
from freqtrade.data import history

data=history.load_data(datadir=Path('E:/madii/h_freq/freqtrade-stable/user_data/data/binance'), timeframe='1m', pairs=['SFP/USDT'])

dataframe=data['SFP/USDT'];
dataframe['buy']=0;
dataframe['sell']=0;
dataframe['TGP']=0;
dataframe['TGP']=dataframe['TGP'].astype(float)
dataframe['SL']=0;
dataframe['SL']=dataframe['SL'].astype(float)
trailing_gain_profit_percent=0.05;
stop_loss_percent=0.05;
trailing_gain_profit=None;
stop_loss=None;
dataframe['txt']=None;
hold=False;
count=0;
for i in range(len(dataframe)):
    current_price=dataframe.loc[i]['open'] 
    new_trailing_gain_profit=current_price + float (current_price* abs(trailing_gain_profit_percent))
    if i==0 or trailing_gain_profit is None:
        trailing_gain_profit=new_trailing_gain_profit
    else:
        if new_trailing_gain_profit<trailing_gain_profit:
            trailing_gain_profit=new_trailing_gain_profit;
    if trailing_gain_profit is not None and trailing_gain_profit< current_price:
        if not hold and count<1:
            hold=True;
            dataframe.at[i,'buy']=1
            dataframe.at[i,'TGP']=trailing_gain_profit;
            dataframe.at[i,'txt']="buy"
            count=count+1;
    new_stop_loss=current_price - float (current_price* abs(stop_loss_percent))
    if i==0 or stop_loss is None:
        stop_loss=new_stop_loss
    else:
        if new_stop_loss > stop_loss:
            stop_loss=new_stop_loss
    if stop_loss is not None and stop_loss > current_price:
        if hold and count==1:
            hold=False
            dataframe.at[i,'sell']=1
            dataframe.at[i,'SL']=stop_loss;
            dataframe.at[i,'txt']="sell"
            count=count-1;