#df = pd.DataFrame.from_records([dict(a=1, b=2), dict(a=2, b=3)])
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

cwhList = [
        ["5PAISA", 507.5],
        ["ABBOTINDIA", 30849.85],
        ["CAMS", 3328],
        ["CDSL", 1994],
        ["GLAXO", 2002],
        ["GLENMARK", 1019],
        ["HAVELLS", 1742.8],
        ["HDFCAMC", 4350],
        ["ICICIGI", 1780.5],
        ["JSL", 655.5],
        ["JUBLFOOD", 697],
        ["MASTEK", 3595],
        ["TCS", 4432],
        ["TECHM", 1593],
        ["ZENSARTECH", 956],
        ["ZYDUSLIFE", 1008]
]

today = date.today()
yesterday = today - timedelta(3)

def getCurrentPrice(cwhList):
    for entry in cwhList:
        data = yf.download(f"{entry[0]}.NS", start=yesterday, end=today)
        print(f"Done:{entry[0]}")
        entry.append(data['Close'].iloc[-1])
    return cwhList

data = getCurrentPrice(cwhList)
df = pd.DataFrame(data, columns = ['Name', 'Target', 'Price'])
df['CWHmargin'] = ((df['Target'] - df['Price'])*100/df['Price']).round(2)
print(df)