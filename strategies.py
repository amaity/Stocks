import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime as dt
from datetime import timedelta as delta
import seaborn as sb
import os

signals = pd.DataFrame({
    '10_cross_30':[0,0,1,1,1],
    'MACD_Signal_MACD':[1,1,1,0,0],
    'MACD_lim':[0,0,0,1,1],
    'abv_50':[1,1,1,0,0],
    'abv_200':[0,1,0,0,1],
    'strategy': [1,2,3,4,5],
})

"""
https://python.plainenglish.io/generating-buy-sell-trade-signals-in-python-1153b1a543c4

STRATEGY 1 
The 10-day SMA should be below the 30-day SMA.
The MACD value should be above the MACD signal line.
The MACD value should not be above 0.
The 10-day and the 30-day SMA should be above the 50-day SMA.
The 10-day, 30-day, and 50-day SMA should be below the 200-day SMA.
STRATEGY 2
The 10-day SMA should be below the 30-day SMA.
The MACD value should be above the MACD signal line.
The MACD value should not be above 0.
The 10-day and the 30-day SMA should be above the 50-day SMA.
The 10-day, 30-day, and 50-day SMA should be above the 200-day SMA.
STRATEGY 3
The 10-day SMA should be above the 30-day SMA.
The MACD value should be above the MACD signal line.
The MACD value should not be above 0.
The 10-day and the 30-day SMA should be above the 50-day SMA.
The 10-day, 30-day, and 50-day SMA should be below the 200-day SMA.
STRATEGY 4
The 10-day SMA should be above the 30-day SMA.
The MACD value should be below the MACD signal line.
The MACD value should be above 0.
The 10-day and the 30-day SMA should be below the 50-day SMA.
The 10-day, 30-day, and 50-day SMA should be below the 200-day SMA.
STRATEGY 5
The 10-day SMA should be above the 30-day SMA.
The MACD value should be below the MACD signal line.
The MACD value should be above 0.
The 10-day and the 30-day SMA should be below the 50-day SMA.
The 10-day, 30-day, and 50-day SMA should be above the 200-day SMA.
"""

def add_signal_indicators(df):
    df['SMA_10'] = ta.sma(df['Adj Close'],length=10)
    df['SMA_30'] = ta.sma(df['Adj Close'],length=30)
    df['SMA_50'] = ta.sma(df['Adj Close'],length=50)
    df['SMA_200'] = ta.sma(df['Adj Close'],length=200)
    
    macd = ta.macd(df['Adj Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['MACD_hist'] = macd['MACDh_12_26_9']

    df['10_cross_30'] = np.where(df['SMA_10'] > df['SMA_30'], 1, 0)
    
    df['MACD_Signal_MACD'] = np.where(df['MACD_signal'] < df['MACD'], 1, 0)
    
    df['MACD_lim'] = np.where(df['MACD']>0, 1, 0)
    
    df['abv_50'] = np.where((df['SMA_30']>df['SMA_50'])
                            &(df['SMA_10']>df['SMA_50']), 1, 0)
                            
    df['abv_200'] = np.where((df['SMA_30']>df['SMA_200'])
                            &(df['SMA_10']>df['SMA_200'])
                            &(df['SMA_50']>df['SMA_200']), 1, 0)
    
    return df

TRADES = []
trade_in_progress = False
holding_period = 14

def backtest_signals(row):
    global TRADES, trade_in_progress, signals, holding_period
    
    if(trade_in_progress):
        _data = TRADES[-1]
        # time to sell after n holding days
        if(row['index']==_data['sell_index']):
            _data['sell_price'] = round(row['Adj Close'],2)
            _data['sell_date'] = str(pd.to_datetime(row['Date']).date())
            _data['returns'] = round((_data['sell_price']-_data['buy_price'])/_data['buy_price']*100, 3)
            TRADES[-1] = _data
            trade_in_progress = False
            
    else:
        _r = pd.DataFrame([row])
        _r = _r.merge(signals, on=list(signals.columns[:-1]), how='inner')
        strategy = _r.shape[0]
        
        if(strategy>0): 
            trade_in_progress = True
            TRADES.append({
                'strategy': _r['strategy'].values[0],
                'buy_date': str(pd.to_datetime(row['Date']).date()),
                'buy_index': row['index'],
                'sell_date': '',
                'sell_index': row['index'] + holding_period,
                'buy_price': round(row['Adj Close'], 2),
                'sell_price': '',
                'returns': 0,
                'stock': row['stock']
            })
