import yfinance as yf
import yfinance.shared as shared
from prettytable import PrettyTable
import pandas as pd
import numpy as np
import os.path
import datetime
from myequitylist import myWatchList

equity_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
nifty100_url = "https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv"
currentMonth = datetime.datetime.now().month
currentYear = datetime.datetime.now().year

# def fetchCodes(equity_url):
#     equity_details = pd.read_csv(equity_url)
#     return equity_details.SYMBOL

# def fetchStockData(stocksymbol):
#     equityDetails = pd.read_csv(equity_url)
#     for name in equityDetails.SYMBOL[:15]:
#         if os.path.isfile(f'./Data/{name}.csv'):
#             data = pd.read_csv(f'./Data/{name}.csv')
#             startDate = pd.to_datetime(data['Date'].iloc[-1])
#             endDate = datetime.date.today()
#             if startDate.date() > endDate:
#                 pass
#             else:
#                 newData = yf.download(f'{name}.NS', start=startDate, end=endDate, interval='1d')
#                 data = pd.concat([data,newData])
#                 data = data.dropna(subset=['Date'])
#                 data.to_csv(f'./Data/{name}.csv', index=False)
#         else:
#             try:
#                 data = yf.download(f'{name}.NS')
#                 #data['Name'] = [name for _ in range(len(data))]
#                 data.to_csv(f'./Data/{name}.csv')
#             except Exception as e:
#                 print(f'{name} ==> {e}')
#     data = pd.read_csv(f'./Data/{stocksymbol}.csv')
#     return data


csvFile = "ind_nifty100list.csv"
def fetchStockNames(csvFile=0):
    if csvFile:
        equityDetails = pd.read_csv(csvFile)
        equityDetails.columns = equityDetails.columns.str.lower()
        names = equityDetails['symbol'].to_list()
        names = set(names + myWatchList)
        return names
    else:
        return myWatchList

def fetchStockData(stockNames):
    for name in stockNames:
        try:
            data = yf.download(f'{name}.NS')
            #data['Name'] = [name for _ in range(len(data))]
            data.to_pickle(f'./Data/{name}.pkl')
            print(f'Completed: {name}')
        except Exception as e:
            print(f'{name} ==> {e}')
    print(list(shared._ERRORS.keys()))
    print("Download completed")

def getSpecificStock(stocksymbol):
    data = pd.read_pickle(f'./Data/{stocksymbol}.pkl')
    #print(data.dtypes)
    #data = data.set_index('Date')
    return data

def getSmaSignal(stockList):
    x = PrettyTable(["Name", "DateSMA", "SMA30"])
    x.align = 'r'
    for name in stockList:
        df = getSpecificStock(name)
        if df.empty:
            pass
        else: 
            ##SMA30 crossing detection
            df['SMA30'] = df['Close'].rolling(30).mean()
            condition = (df['SMA30'] > df['Open']) & (df['Close'] > df['SMA30'])
            df['Signal'] = np.where(condition, True, False)
            df = df.loc[(df['Signal'] == True)]
            df=df[(df.index.month==currentMonth) & (df.index.year==currentYear)]
            if df.empty:
                pass
            else:
                x.add_row([name, df.index.date[-1], df.SMA30.iloc[-1].round(2)])
    print(x)


def getGroupTwenty(stockList):
    x = PrettyTable(["Name", "DateGP20", "GP20Pcnt", "CurrentP", "Margin"])
    x.align = 'r'
    for name in stockList:
        df = getSpecificStock(name)
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
            df=df[df.index.year==currentYear]
            if df.empty:
                pass
            else:
                x.add_row([name, df.index.date[-1], df.Percentage.iloc[-1].round(2),
                          currentPrice.round(2), df.Margin.iloc[-1].round(2)])
    print(x)

if __name__ == "__main__":
    csvFile = "ind_nifty100list.csv"
    #csvFile = "EQUITY_L.csv"
    names = fetchStockNames()
    fetchStockData(names)
    #df = getSpecificStock('CAPLIPOINT')
    #getSmaSignal(names)
    getGroupTwenty(names)
    #print(df['2023-11-1':'2023-11-30'])
