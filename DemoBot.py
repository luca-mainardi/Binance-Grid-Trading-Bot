from threading import Thread
import ccxt
import time

from pip import List
import config
import time
import sys

import matplotlib
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from datetime import datetime
import json

# __________________ Demo Account Class _________________


class Demo_Account:

    def __init__(self, initial_balance) -> None:
        self.curr_balance = initial_balance
        self.cryptocurr_balance = 0

# ______________________________________________________

# ____________________ Order Class _____________________


class Order:
    def __init__(self, amount: float, price: float, type):
        self.price = price
        self.amount = amount  # in cryptocurrency
        self.status = 'open'  # 'open' or 'closed'
        self.type = type  # 'buy' or 'sell'

    def toDict(self):
        return {'price': self.price,
                'amount': self.amount,
                'status': self.status,
                'type': self.type}

# ______________________________________________________


# return the current price of the symbol passed as parameter
def get_crypto_price(exchange, symbol):
    return float(exchange.fetch_ticker(symbol)['last'])


# exchange = ccxt.binance()
# account = Demo_Account(2000)

def write_json_buy_lines(data, filename="buy_lines.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_sell_lines(data, filename="sell_lines.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def start_demo_bot(exchange, account):

    # counter of order executed
    order_count = 0

    ticker = exchange.fetch_ticker(config.SYMBOL)

    # lists with open orders
    buy_orders: List[dict] = []
    sell_orders: List[dict] = []

    # ___________________ initial order ___________________

    # amount in cryptocurrency
    amount = config.POSITION_SIZE * config.NUM_SELL_GRID_LINES

    account.cryptocurr_balance += amount

    # amount in currency
    account.curr_balance -= amount * float(ticker['last'])

    # print initial balances
    print(f"Initial currency balance: {account.curr_balance}")
    print(f"Initial cryptocurrecny balance: {account.cryptocurr_balance}")

    # ______________________________________________________

    # _________________ grid construction __________________

    for i in range(config.NUM_BUY_GRID_LINES):
        price = ticker['bid'] - config.GRID_SIZE * (i+1)

        order = Order(config.POSITION_SIZE, price, 'buy')
        buy_orders.append(order.toDict())

    for i in range(config.NUM_SELL_GRID_LINES):
        price = ticker['bid'] + config.GRID_SIZE * (i+1)

        order = Order(config.POSITION_SIZE, price, 'sell')
        sell_orders.append(order.toDict())

    # create json files
    write_json_buy_lines(buy_orders)
    write_json_sell_lines(sell_orders)

    # for sell_order in sell_orders:
    #     if sell_order.status == 'open':
    #         print(sell_order.price)

    # ______________________________________________________

    # _____________________ main loop ______________________

    while True:
        # list containing orders that have been closed during this loop
        # (they are removed from the respective open order lists at the end of the loop)
        #closed_orders = []

        print("__________________Checking for orders______________________\n")

        # _____________________ buy orders ______________________
        # check all the open buy orders (contained in buy_orders list)

        print("Buy Orders:\n")
        for buy_order in buy_orders:

            # wrong type order (sell order in buy_orders)
            if buy_order['type'] != 'buy':
                raise Exception("Wrong type in buy_orders")

            # print price of the order
            print(f"Checking buy order {buy_order['price']}")

            # get current price of cryptocurrency
            current_price = get_crypto_price(exchange, config.SYMBOL)
            print(f"Current price: {current_price}\n")

            # order can be closed
            if current_price <= buy_order['price']:

                # buy cryptocurrency
                account.cryptocurr_balance += buy_order['amount']
                fees = buy_order['amount'] * current_price * 0.002
                account.curr_balance -= ((buy_order['amount'] *
                                         current_price) + fees)

                # close order
                buy_order['status'] = 'closed'
                # closed_orders.append(buy_order)

                print(f"\tBuy order executed at {current_price}")

                # create a new sell order above the closed order
                new_sell_price = buy_order['price'] + config.GRID_SIZE
                print(f"\tCreating new limit sell order at {new_sell_price}\n")
                new_sell_order = Order(config.POSITION_SIZE,
                                       new_sell_price, 'sell')
                sell_orders.append(new_sell_order.toDict())

                # update json files
                write_json_buy_lines(buy_orders)
                write_json_sell_lines(sell_orders)

                print("SELL ORDERS:")
                for order in sell_orders:
                    if order['status'] == 'open':
                        print(order['price'])

                print("BUY ORDERS:")
                for order in buy_orders:
                    if order['status'] == 'open':
                        print(order['price'])

                # update order_count
                order_count += 1

                # prints balances after the order
                print(f"\tCurrent currency balance: {account.curr_balance}")
                print(
                    f"\tCurrent cryptocurrency balance: {account.cryptocurr_balance}\n")

            time.sleep(config.CHECK_FREQUENCY)

        # ______________________________________________________

        # ____________________ sell orders _____________________
        # check all the open sell orders (contained in sell_orders list)

        print("Sell Orders:\n")
        for sell_order in sell_orders:

            # wrong type order (buy order in sell_orders)
            if sell_order['type'] != 'sell':
                raise Exception("Wrong type in sell_orders")

            # print price of the order
            print(f"checking sell order {sell_order['price']}")

            # get current price of cryptocurrency
            current_price = get_crypto_price(exchange, config.SYMBOL)
            print(f"current price: {current_price}\n")

            # order can be closed
            if current_price >= sell_order['price']:

                # sell cryptocurrency
                account.cryptocurr_balance -= sell_order['amount']
                fees = sell_order['amount'] * current_price * 0.002
                account.curr_balance += ((sell_order['amount'] *
                                          current_price) - fees)

                # close order
                sell_order['status'] = 'closed'
                # closed_orders.append(sell_order)

                print(f"\tSell order executed at {current_price}")

                # create a new buy order below the closed order
                new_buy_price = sell_order['price'] - config.GRID_SIZE
                print(f"\tCreating new limit buy order at {new_buy_price}\n")
                new_buy_order = Order(config.POSITION_SIZE,
                                      new_buy_price, 'buy')
                buy_orders.append(new_buy_order.toDict())

                # update json files
                write_json_buy_lines(buy_orders)
                write_json_sell_lines(sell_orders)

                print("SELL ORDERS:")
                for order in sell_orders:
                    if order['status'] == 'open':
                        print(order['price'])

                print("BUY ORDERS:")
                for order in buy_orders:
                    if order['status'] == 'open':
                        print(order['price'])

                # update order_count
                order_count += 1

                # prints balances after the order
                print(f"\tCurrent currency balance: {account.curr_balance}")
                print(
                    f"\tCurrent cryptocurrency balance: {account.cryptocurr_balance}\n")

            time.sleep(config.CHECK_FREQUENCY)

        # ______________________________________________________

        # ________________ remove closed orders ________________

        # list containing the currently open buy orders
        buy_orders = [
            buy_order for buy_order in buy_orders if (buy_order['status'] != 'closed') and (buy_order['type'] == 'buy')]
        # list containing the currently open sell orders
        sell_orders = [
            sell_order for sell_order in sell_orders if (sell_order['status'] != 'closed') and (sell_order['type'] == 'sell')]

        # update json files
        write_json_buy_lines(buy_orders)
        write_json_sell_lines(sell_orders)

        # for order in closed_orders:
        #     # list containing the currently open buy orders
        #     buy_orders = [
        #         buy_order for buy_order in buy_orders if (buy_order != order) and (buy_order.type == 'buy')]
        #     # list containing the currently open sell orders
        #     sell_orders = [
        #         sell_order for sell_order in sell_orders if (sell_order != order) and (sell_order.type == 'sell')]

        # ______________________________________________________

        # __________________ All orders closed _________________

        # the bot stops if the last sell order have been closed
        if len(sell_orders) == 0:
            sys.exit("Stopping bot, nothing left to sell")

        # the bot stops if the last buy order have been closed
        if len(buy_orders) == 0:
            sys.exit("Stopping bot, no money left")

        # ______________________________________________________

        # prints balances after checking all orders
        print(f"\nCurrent currency balance: {account.curr_balance}")
        print(
            f"Current cryptocurrency balance: {account.cryptocurr_balance}\n")
        print(f"Order count: {order_count}")

        print("__________________________________________________________\n")

    # ______________________________________________________
