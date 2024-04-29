import numpy as np
import pandas as pd
import yfinance as yf
from prettytable import PrettyTable
from myequitylist import myWatchList

def fetchStockNames(csvFile=0):
    if csvFile:
        equityDetails = pd.read_csv(csvFile)
        equityDetails.columns = equityDetails.columns.str.lower()
        names = equityDetails['symbol'].to_list()
    return names


def getGroupTwenty(stockList):
    x = PrettyTable(["Name", "DateGP20", "GP20Pcnt", "CurrentP", "Margin"])
    x.align = 'r'
    for name in stockList:
        try:
            df = yf.download(f'{name}.NS', period='1y', interval='1d')
            if df.empty:
                pass
            else:
                df.reset_index(inplace=True)
                df['Date'] = df['Date'].apply(pd.to_datetime)
                currentPrice = df['Close'].iloc[-1]
                df['CGTO'] = np.where(df['Close'] > df['Open'], True, False)
                df['Group'] = df['CGTO'].ne(df['CGTO'].shift()).cumsum()
                df.drop(df[df['CGTO'] == False].index, inplace=True)
                dfmin = df.groupby('Group')['Low'].min()
                dfmax = df.groupby('Group')['High'].max()
                dfpct = (dfmax - dfmin)*100/dfmin
                dfmrg = (dfmax - currentPrice)*100/currentPrice
                df = df.merge(dfpct.rename('Percentage'), how='left', on='Group')
                df = df.merge(dfmrg.rename('Margin'), how='left', on='Group')
                df = df[df['Percentage'] >= 20.0]
                df = df.set_index('Date')
                x.add_row([name, df.index.date[-1], df.Percentage.iloc[-1].round(2),
                          currentPrice.round(2), df.Margin.iloc[-1].round(2)])
        except Exception as e:
            print(f'{name} ==> {e}')
    print(x)

if __name__ == "__main__":
    niftyList = myWatchList #fetchStockNames(csvFile="ind_nifty200list.csv")
    getGroupTwenty(niftyList)