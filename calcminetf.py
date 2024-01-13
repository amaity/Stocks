import numpy as np
import pandas as pd
import yfinance as yf
from collections import defaultdict
from myetflist import etfList

def calcMinEtf(stockList):
    dd = defaultdict(list)
    for name in stockList:
        try:
            df = yf.download(f'{name}.NS', period='3mo', interval='1d')
            ##SMA20 
            df['SMA20'] = df['Close'].rolling(20).mean()
            df['Diff'] = df['Close'] - df['SMA20']
            df['PcntChange'] = df['Diff']*100/df['SMA20']
            if df.empty:
                pass
            else:
                dd[f'{name}.NS'] = df.iloc[-1].to_list()
        except Exception as e:
            print(f'{name} ==> {e}')
    df_ = pd.DataFrame.from_dict(dd, orient='index', 
        columns=['Open', 'High', 'Low', 'Close',  'Adj Close', 'Volume',  'SMA20',  'Diff',  'PcntChange'])
    df_.sort_values(by=['PcntChange'], inplace=True)
    return df_


if __name__ == "__main__":
    out = calcMinEtf(etfList)
    print(out.head(3))
            
