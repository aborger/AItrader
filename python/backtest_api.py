import alpaca_trade_api as tradeapi
from python.user_data.user import User as alpacaUser
import pandas as pd

class api:
	alpacaUser.update_users(is_paper=True, tradeapi=tradeapi)
	_alpacaAPI = alpacaUser.get_api()
	def __init__(self):
		self.clock = Clock()
		self.account = Account()
		
	def get_current(self, symbol):
		barset = self.get_barset(symbol, '1Min', 1)
		bars = barset[symbol]
		price = bars[0].c
		return price
		
	def get_account(self):
		return self.account
	
	def get_clock(self):
		return self.clock
	
	def get_barset(self, symbol, timeframe, limit):
		NY = 'America/New_York'
		start=pd.Timestamp('2019-01-01', tz=NY).isoformat()
		barset = api._alpacaAPI.get_barset(symbol, timeframe, limit=limit, start=start)
		return barset
		
	def list_positions(self):
		return self.account.portfolio
		
	def update_equity(self):
		new_equity = 0
		for position in self.account.portfolio:
			price = self.get_current(position.symbol)
			new_equity += price * position.qty
		self.account.last_equity = self.account.equity
		print('new_equity = ' + str(new_equity))
		self.account.equity = new_equity + self.account.buying_power
			
	def submit_order(self, symbol, qty, side, type, time_in_force):
		# Get price
		price = self.get_current(symbol)
		
		new_position = Position(symbol, qty, price)
		
		if side == 'buy':
			self.account.add_position(new_position)
		elif side == 'sell':
			self.account.remove_position(new_position)
		else:
			print('Not an option')
		

		
class Clock:
	def __init__(self):
		self.is_open = True
		NY = 'America/New_York'
		self.real_time = pd.Timestamp('2019-01-02', tz=NY).isoformat()

		self.timestamp = self.real_time
		#self.timestamp = self.timestamp.replace(month=self.timestamp.month - 1)
		
	def set_time(self, day, month, year, hour, minute, second):
		#self.timestamp = datetime.datetime(year, month, day, hour, minute, second)
		self.timestamp = self.real_time
		
	def next_day(self):
		#self.timestamp = self.timestamp.replace(day=self.timestamp.day + 10)
		self.timestamp = self.real_time
		
	def get_time(self):
		return self.timestamp
		
		
	
class Account:
	def __init__(self):
		self.portfolio = []
		self.equity = 1000
		self.last_equity = 900
		self.buying_power = 1000
		self.status = 'Active'
		
	def add_position(self, position):
		# Add position to portfolio
		exists = False
		for positions in self.portfolio:
			if positions.symbol == position.symbol:
				positions.qty += position.qty
				exists = True
		if not exists:
			self.portfolio.append(position)
			
		# Subtract buying_power
		self.buying_power -= position.qty * position.entry_price
		
	def remove_position(self, position):
		exists = False
		value = position.qty * position.entry_price
		for positions in self.portfolio:
			if positions.symbol == position.symbol:
				positions.qty -= position.qty
				exists = True
				
		self.buying_power += value
		print('Value of ' + str(value))
				
		if not exists:
			print('PositionNotInPortfolio')
		
class Position:
	def __init__(self, symbol, qty, entry_price):
		self.symbol = symbol
		self.qty = qty
		self.entry_price = entry_price

def REST(key_id, secret_key, base_url):
		new_api = api()
		return new_api
		
class rest:
	class APIError(Exception): 
		print('APIError has occured')
		