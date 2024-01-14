import yfinance as yf
import yfinance.shared as shared
import pandas as pd
import numpy as np
import datetime
from collections import defaultdict

nifty200_url = "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv"

def runStockScreener(csvFile=0):
    dd = defaultdict(list)
    if csvFile:
        equityDetails = pd.read_csv(csvFile)
        equityDetails.columns = equityDetails.columns.str.lower()
        names = equityDetails['symbol'].to_list()
        for name in names:
            try:
                df = yf.download(f'{name}.NS', period='1y', interval='1d')
                df['PrevClose'] = df['Close'].shift(periods=1)
                df['SMA100'] = df['Close'].rolling(100).mean()
                df['Min60D'] = df['Close'].rolling(60).min()
                condition = (df['Close'] > df['SMA100']) & (df['Close'] > df['PrevClose']) \
                                & (df['PrevClose'] < df['Min60D'])
                df['Signal'] = np.where(condition, True, False)
                #df = df.loc[(df['Signal'] == True)]
                if df.empty:
                    pass
                else:
                    df.reset_index(inplace=True)
                    df.drop('Volume', axis=1, inplace=True)
                    dd[f'{name}.NS'] = df.iloc[-1].to_list()
            except Exception as e:
                print(f'{name} ==> {e}')
    df_ = pd.DataFrame.from_dict(dd, orient='index', 
        columns=['Date', 'Open', 'High', 'Low', 'Close',  'Adj Close', 'PrevClose', 'SMA100',  'Min60D',  'Signal'])
    #df_ = df_.loc[(df_['Signal'] == True)]
    return df_

if __name__ == "__main__":
    out = runStockScreener(csvFile="ind_niftynext50list.csv")
    print(out)