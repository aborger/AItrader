import pathos
from python.Level1.Level2.predict import find_gain

BACKTEST = 'data/backTest/'
ACTUALLY_TRADE = False
USE_MULTIPROCESSING = False

class Stock():
	_NUMBARS = None
	_time_frame = None
	_loss_percent = .01
	_stocks = []
	_main_api = None

	#-----------------------------------------------------------------------#
	#								Initializing							#
	#-----------------------------------------------------------------------#
	def __init__(self, ticker):
		self.gain = None
		if isinstance(ticker, str): # its a regular string
			self.symbol = ticker
			Stock._stocks.append(self)
		else: # create a stock object from position object
			self.symbol = ticker.symbol


	@classmethod
	def setup(cls, NUMBARS, model, time_frame, main_api):
		cls._NUMBARS = NUMBARS
		cls._model = model
		cls._time_frame = time_frame
		cls._main_api = main_api
		


	#-----------------------------------------------------------------------#
	#								Individual								#
	#-----------------------------------------------------------------------#
		
	def find_current_price(self):
		barset = (Stock._main_api.get_barset(self.symbol,'1Min',limit=1))
		symbol_bars = barset[self.symbol]
		current_price = symbol_bars[0].c
		return current_price

	
	def set_gain(self, gain):
		self.gain = gain

	
	#-----------------------------------------------------------------------#
	#									Trading								#
	#-----------------------------------------------------------------------#
	
	

	def buy(self, api, quantity):
		print ('Buying ' + self.symbol + ' QTY: ' + str(quantity))
		if ACTUALLY_TRADE:
			api.submit_order(
				symbol=self.symbol,
				qty=quantity,
				side='buy',
				type='market',
				time_in_force='gtc')
		else:
			print('WARNING, ACTUALLY TRADE = FALSE')

	def sell(self, api, quantity):
		print ('Sold ' + self.symbol)
		if ACTUALLY_TRADE:
			api.submit_order(
				symbol=self.symbol,
				qty=quantity,
				side='sell',
				type='market',
				time_in_force='gtc')
		else:
			print('WARNING, ACTUALLY TRADE = FALSE')
		
	def trailing_stop(self, api, quantity, percent):
		print('Applying trailing stop for ' + self.symbol)
		if ACTUALLY_TRADE:
			api.submit_order(
				symbol=self.symbol,
				qty=quantity,
				side='sell',
				type='trailing_stop',
				time_in_force='gtc',
				trail_percent=percent)
		else:
			print('WARNING, ACTUALLY TRADE = FALSE')
		
	#-----------------------------------------------------------------------#
	#								Calculations							#
	#-----------------------------------------------------------------------#
	
	# Main function used by tradeAI
	# Returns two items: diversified_stocks and second_best_stocks
	# diversified_stocks is dict with best stocks and their buy ratio
	# second_best_stocks is num_best_stocks next best stocks
	@classmethod
	def find_diversity(cls, num_best_stocks):
		best_stocks, all_best_stocks = Stock._find_best(num_best_stocks)
		gain_sum = 0
		for stock in best_stocks:
			gain_sum += stock.gain
		if gain_sum == 0:
			value_per_gain = 0
		else:
			value_per_gain = 100/gain_sum
		diversified_stocks = []
		for stock in best_stocks:
			this_buy_ratio = stock.gain * value_per_gain
			this_stock = dict(stock_object = stock, buy_ratio = this_buy_ratio/100)
			diversified_stocks.append(this_stock)
		return diversified_stocks, all_best_stocks
	

		
	# returns tuple of two lists
	# list[0] = num_best_stocks of the highest gains. If num_best_stocks is 5, list[0] is the top 5 stocks
	# list[1] = next numb_best_stocks of the next highest gains. If num_best_stocks is 5, list[1] is the next top 5 stocks
	@classmethod
	def _find_best(cls, num_best_stocks): 
				
		def get_gain(stock):
				return stock.gain
		
		# find gain for every stock

		if USE_MULTIPROCESSING:
			# use multiprocessing to speed up
			pool = pathos.helpers.mp.Pool(pathos.helpers.mp.cpu_count())
			stocks_with_gains = pool.starmap(find_gain, [(stock, cls._main_api, cls._time_frame, cls._NUMBARS) for stock in cls.get_stock_list()])
			pool.close()
	
		else:
			stocks_with_gains = []
			for stock in cls.get_stock_list():
				stocks_with_gains.append(find_gain(stock)) 



		# Add best gains to max_stocks
		max_stocks = []
		for stock in stocks_with_gains:
				if len(max_stocks) < num_best_stocks * 2:
					max_stocks.append(stock)
				elif stock.gain > max_stocks[-1].gain:
					max_stocks.pop()
					max_stocks.append(stock)
				
		# sort list so lowest gain is at the end
		max_stocks.sort(reverse=True, key=get_gain)
		best = max_stocks[0:num_best_stocks]
		return best, max_stocks

	#-----------------------------------------------------------------------#
	#									Getters								#
	#-----------------------------------------------------------------------#

	@classmethod
	def get_stock_list(cls):
		return cls._stocks



		



	
