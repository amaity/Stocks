import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

##code ref: https://eodhd.com/financial-academy/stocks-data-analysis-examples/advanced-momentum-trading-techniques-with-volatility-volume-indicators-using-python#:~:text=Building%20a%20Momentum%20Trading%20Model%20in%20Python,-Creating%20a%20momentum&text=We'll%20use%20Python%20to,stock%20data%20in%20previous%20sections.

# Fetching historical stock data
name = "ZYDUSLIFE"
df = yf.download(f'{name}.NS', period='1y', interval='1d')

# Calculating daily returns
df['Daily_Return'] = df['Close'].pct_change()

# Calculating volatility
volatility = df['Daily_Return'].std() * np.sqrt(252)

# Plotting the volatility
# plt.figure(figsize=(10, 6))
# df['Daily_Return'].plot()
# plt.title(f'Volatility of {name}')
# plt.ylabel('Daily Returns')
# plt.xlabel('Date')
# plt.show()

# Calculating the On-Balance Volume (OBV)
obv = [0]
for i in range(1, len(df)):
    if df['Close'][i] > df['Close'][i-1]:
        obv.append(obv[-1] + df['Volume'][i])
    elif df['Close'][i] < df['Close'][i-1]:
        obv.append(obv[-1] - df['Volume'][i])
    else:
        obv.append(obv[-1])

df['OBV'] = obv

# Plotting OBV
# plt.figure(figsize=(10, 6))
# df['OBV'].plot()
# plt.title(f'On-Balance Volume (OBV) of {name}')
# plt.ylabel('OBV')
# plt.xlabel('Date')
# plt.show()

def calculate_momentum(data, period=20):
	return data['Close'].diff(periods=period)

# Adding Momentum to DataFrame
df['Momentum'] = calculate_momentum(df)

def trading_strategy(data):
    buy_signals = []
    sell_signals = []
    
    for i in range(len(data)):
        # Buy if momentum is positive and OBV is increasing
        if data['Momentum'][i] > 0 and data['OBV'][i] > data['OBV'][i-1]:
            buy_signals.append(data['Close'][i])
            sell_signals.append(np.nan)
        # Sell if momentum is negative
        elif data['Momentum'][i] < 0:
            sell_signals.append(data['Close'][i])
            buy_signals.append(np.nan)
        else:
            buy_signals.append(np.nan)
            sell_signals.append(np.nan)

    return buy_signals, sell_signals

df['Buy_Signals'], df['Sell_Signals'] = trading_strategy(df)

plt.figure(figsize=(12,6))
plt.plot(df['Close'], label='Close Price', alpha=0.5)
plt.scatter(df.index, df['Buy_Signals'], label='Buy Signal', marker='^', color='green')
plt.scatter(df.index, df['Sell_Signals'], label='Sell Signal', marker='v', color='red')
plt.title(f'Momentum Trading Signals for {name}')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()