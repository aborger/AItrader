# Dependencies:
# pip3 install alpaca-trade-api
print('Importing dependencies...')
import alpaca_trade_api as tradeapi
from tensorflow import keras
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import time

NUMSTOCKS = 100
NUMBARS = 10

# Login to Alpaca
print('Logging in...')
api = tradeapi.REST(key_id='PKV06MEA5HFSFTMZL7JT',
	secret_key='DLKb18bnhN06evMjVUhMxv0j/8ngKMDupVMjdgNb',
	base_url='https://paper-api.alpaca.markets')

# Load Model
print('Loading AI...')
model = keras.models.load_model('Trade-Model')

# Load S&P500
print('Loading stock list...')
table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
df = table[0]
sp = df['Symbol']

# Predict difference for each stock
def FindDifferences():
  print('Looking at stocks...')
  predicted_differences = []
  for symbol in range(0, NUMSTOCKS):
    # Get bars
    barset = (api.get_barset(sp[symbol],'5Min',limit=10))
    # Get symbol's bars
    symbol_bars = barset[sp[symbol]]
    print(sp[symbol])
    # Convert to list
    dataSet = []
    for barNum in symbol_bars:
      dataSet.append(barNum.o)
    # Convert to numpy array
    npDataSet = np.array(dataSet)
    reshapedSet = np.reshape(npDataSet, (1, NUMBARS, 1))
    # Normalize Data
    sc = MinMaxScaler(feature_range=(0,1))
    normalized = np.empty(shape=(1, NUMBARS, 1)) 
    normalized[0] = sc.fit_transform(reshapedSet[0])
    # Predict Price
    predicted_price = model.predict(normalized)
    # undo normalization
    predicted_price = sc.inverse_transform(predicted_price)
    # add difference to array
    difference = predicted_price[0,0] - reshapedSet[0, NUMBARS - 1, 0]
    percentDifference = difference/reshapedSet[0, NUMBARS - 1, 0]
    predicted_differences.append(percentDifference)
  return predicted_differences

# Buy Stock
def BuyStock(stock):
  print ('Bought ' + stock)
  api.submit_order(
    symbol=stock,
    qty=1,
    side='buy',
    type='market',
    time_in_force='gtc')
	
# Sell Stock
def SellStock(stock):
  print ('Sold ' + stock)
  api.submit_order(
    symbol=stock,
    qty=1,
    side='sell',
    type='market',
    time_in_force='gtc')

# Main
while 1:
	predicted_differences = FindDifferences()
	best_stock = sp[predicted_differences.index(min(predicted_differences))]
	BuyStock(best_stock)
	time.sleep(300)
	SellStock(best_stock)
