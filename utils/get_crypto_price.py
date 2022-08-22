
@staticmethod
# return the current price of the symbol passed as parameter
def get_crypto_price(exchange, symbol):
    return float(exchange.fetch_ticker(symbol)['last'])
