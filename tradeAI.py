# This file manages the other files

# Number of bars to predict on
# Ex: If NUMBARS=4 use monday-thursday to predict friday 
NUMBARS = 10

def train():
    from python.train_rnn import prepare
    from python.train_rnn import train_network
    from python.train_rnn import test_results
    import keras

    x_train, y_train = prepare(args.trainset, NUMBARS)
    model = train_network(x_train, y_train, args.epochs)

    print('Saving model...')
    model.save('data/Trade-Model.h5')

    test_results(args.trainset, args.testset, model, NUMBARS)
    
def test():
    from python.train_rnn import test_results
    import keras.models as model
    model = model.load_model(args.model)
    test_results(args.trainset, args.testset, model, NUMBARS)
    
def trade(is_test, time_period):
    from python.stock import Stock
    from python.PYkeys import Keys
    import alpaca_trade_api as tradeapi
    import pandas as pd
    print('Logging in...')
    keys = Keys()
    api = tradeapi.REST(key_id = keys.get_key_id(),
                    secret_key = keys.get_secret_key(),
                    base_url = keys.get_base_url())
    
    # Load S&P500
    print('Loading stock list...')
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    sp = df['Symbol']
    
    if is_test:
        sp = sp[0:10]

    print('Loading AI...')
    from tensorflow import keras
    model = keras.models.load_model('data/Trade-Model.h5')
    Stock.setup(NUMBARS, model, api)
    for symbol in sp:
        this_stock = Stock(symbol)

    while True:
        best_stocks = Stock.highest_gain(time_period)
        for stock in best_stocks:
            print('Stock: ' + stock.symbol)
            print('Gain = ' + str(stock.return_gain(time_period))+ '%')
            stock.buy()
            print('-------------------------------')
        while len(Stock.owned) > 0:
            for stock in Stock.owned:
                if stock.get_gain(time_period) < 0:
                    stock.sell()
        
    
#############################################
# Command Line
#############################################

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Control Trading AI')
    parser.add_argument("command", metavar="<command>",
                        help="'train', 'trade', 'test'")
    parser.add_argument("--trainset", default='data/dataset.csv',
                        metavar="path/to/training/dataset",
                        help="Path to training dataset")
    parser.add_argument("--testset", default='data/ZION5Min.csv',
                        metavar="path/to/test/dataset",
                        help="Path to test dataset")
    parser.add_argument("--model", default='data/Trade-Model.h5',
                        metavar="path/to/model",
                        help="Path to model")
    parser.add_argument("--epochs", default=100, type=int,
                        help="Number of epochs to use in training")
    # New Data
    parser.add_argument("-d", action='store_true', required=False,
                        help="Include -d if you want to include new data")
    # Test
    parser.add_argument("-t", action='store_true', required=False,
                        help='Include -t if this is a shortened test')
    parser.add_argument("--time", default='1D',
                        help = "Time period to buy and sell on")
    args = parser.parse_args()

    
    # Run based on arguments
    if args.d == True:
        import os
        os.system("sudo python3 python/collect_data.py")
    elif args.command == 'train':
        train()

    elif args.command == 'test':
        test()

    elif args.command == 'trade':
        trade(args.t, args.time)
        
    else:
        raise InputError("Command must be either 'train', 'run', or 'view'")

