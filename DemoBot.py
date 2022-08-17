import time
from pip import List
import time
import sys
import json

import config
import ccxt

# __________________ Demo Account Class _________________


class Demo_Account:

    def __init__(self, initial_balance) -> None:
        self.curr_balance = initial_balance
        self.cryptocurr_balance = 0

    def toDict(self):
        return {}

# ______________________________________________________

# ____________________ Order Class _____________________


class Order:
    def __init__(self, amount: float, price: float, side):
        self.price = price
        self.amount = amount  # in cryptocurrency
        self.status = 'open'  # 'open' or 'closed'
        self.side = side  # 'buy' or 'sell'

    def toDict(self):
        return {'price': self.price,
                'amount': self.amount,
                'status': self.status,
                'side': self.side}

# ______________________________________________________


# return the current price of the symbol passed as parameter
def get_crypto_price(exchange, symbol):
    return float(exchange.fetch_ticker(symbol)['last'])


def write_json_buy_lines(data, filename="buy_lines.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_sell_lines(data, filename="sell_lines.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_closed_orders(data, filename="closed_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_account_infos(data, filename="account_infos.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def start_demo_bot():

    print("_____________________ START BOT _____________________\n")

    exchange = ccxt.binance()

    ticker = exchange.fetch_ticker(config.get_Symbol())

    INITIAL_BALANCE = 10000.0

    # create account infos
    account = {'curr_balance': INITIAL_BALANCE,
               'cryptocurr_balance': 0.0,
               'total_investment': 0.0,
               'total_profit': 0.0,
               }

    # counter of order executed
    order_count = 0

    # lists with open orders
    buy_orders: List[dict] = []
    sell_orders: List[dict] = []

    # list with closed orders
    closed_orders: List[dict] = []
    write_json_closed_orders(closed_orders)

    # ___________________ initial order ___________________

    # amount to buy
    first_amount_cryptocurr = config.get_Position_Size() * \
        config.get_Num_Sell_Grid_Lines()
    first_amount_curr = first_amount_cryptocurr * float(ticker['last'])
    fees = first_amount_curr * 0.002

    # buy initial amount of cryptocurrency
    account['cryptocurr_balance'] += round(first_amount_cryptocurr, 5)
    account['curr_balance'] -= round(first_amount_curr + fees, 5)

    # ______________________________________________________

    # print initial balance
    print(f"\nInitial currency balance: {account['curr_balance']}")
    print(f"Initial cryptocurrecny balance: {account['cryptocurr_balance']}\n")

    # _________________ grid construction __________________

    for i in range(config.get_Num_Buy_Grid_Lines()):
        price = ticker['bid'] - config.get_Grid_Size() * (i+1)

        order = Order(config.get_Position_Size(), price, 'buy')
        buy_orders.append(order.toDict())

    for i in range(config.get_Num_Sell_Grid_Lines()):
        price = ticker['bid'] + config.get_Grid_Size() * (i+1)

        order = Order(config.get_Position_Size(), price, 'sell')
        sell_orders.append(order.toDict())

    # ______________________________________________________

    # calculate total investment
    future_buy_amount = 0

    for buy_order in buy_orders:
        future_buy_amount += float(buy_order['amount']) * \
            float(buy_order['price'])

    account['total_investment'] = round(
        first_amount_curr + future_buy_amount, 5)

    print(f"Total Investment: {account['total_investment']}\n")

    # create json files
    write_json_buy_lines(buy_orders)
    write_json_sell_lines(sell_orders)
    write_json_account_infos(account)

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

            # wrong order side (sell order in buy_orders)
            if buy_order['side'] != 'buy':
                raise Exception("Wrong side in buy_orders")

            # print price of the order
            print(f"\tChecking buy order {buy_order['price']}")

            # get current price of cryptocurrency
            current_price = get_crypto_price(exchange, config.get_Symbol())
            print(f"\tCurrent price: {current_price}\n")

            # order can be closed
            if current_price <= buy_order['price'] and (buy_order['status'] == 'open'):

                # buy cryptocurrency
                account['cryptocurr_balance'] = round(
                    account['cryptocurr_balance'] + buy_order['amount'], 5)
                fees = buy_order['amount'] * current_price * 0.002
                account['curr_balance'] = round(account['curr_balance']-(buy_order['amount']
                                                                         * current_price) - fees, 5)

                # close order
                buy_order['status'] = 'closed'
                closed_orders.append(buy_order)

                print(f"\t\tBuy order executed at {buy_order['price']}")

                # create a new sell order above the closed order
                new_sell_price = buy_order['price'] + config.get_Grid_Size()
                print(
                    f"\t\tCreating new limit sell order at {new_sell_price}\n")
                new_sell_order = Order(
                    config.get_Position_Size(), new_sell_price, 'sell')
                sell_orders.append(new_sell_order.toDict())

                # update json files
                write_json_buy_lines(buy_orders)
                write_json_sell_lines(sell_orders)
                write_json_closed_orders(closed_orders)

                # update order_count
                order_count += 1

                # prints balances after the order
                print(
                    f"\t\tCurrent currency balance: {account['curr_balance']}")
                print(
                    f"\t\tCurrent cryptocurrency balance: {account['cryptocurr_balance']}\n")

            # calculate current profit
            current_balance_in_curr = float(
                account['curr_balance']) + (float(account['cryptocurr_balance']) * current_price)
            account['total_profit'] = round(current_balance_in_curr -
                                            float(INITIAL_BALANCE), 5)
            # update account_infos.json
            write_json_account_infos(account)

            time.sleep(config.get_Check_Frequency())

        # ______________________________________________________

        # ____________________ sell orders _____________________
        # check all the open sell orders (contained in sell_orders list)

        print("Sell Orders:\n")
        for sell_order in sell_orders:

            # wrong order side (buy order in sell_orders)
            if sell_order['side'] != 'sell':
                raise Exception("Wrong side in sell_orders")

            # print price of the order
            print(f"\tchecking sell order {sell_order['price']}")

            # get current price of cryptocurrency
            current_price = get_crypto_price(exchange, config.get_Symbol())
            print(f"\tcurrent price: {current_price}\n")

            # order can be closed
            if (current_price >= sell_order['price']) and (sell_order['status'] == 'open'):

                # sell cryptocurrency
                account['cryptocurr_balance'] = round(
                    account['cryptocurr_balance'] - sell_order['amount'], 5)
                fees = sell_order['amount'] * current_price * 0.002
                account['curr_balance'] = round(
                    account['curr_balance'] + (sell_order['amount'] * current_price) - fees, 5)

                # close order
                sell_order['status'] = 'closed'
                closed_orders.append(sell_order)

                print(f"\t\tSell order executed at {current_price}")

                # create a new buy order below the closed order
                new_buy_price = sell_order['price'] - config.get_Grid_Size()
                print(f"\t\tCreating new limit buy order at {new_buy_price}\n")
                new_buy_order = Order(
                    config.get_Position_Size(), new_buy_price, 'buy')
                buy_orders.append(new_buy_order.toDict())

                # update json files
                write_json_buy_lines(buy_orders)
                write_json_sell_lines(sell_orders)
                write_json_closed_orders(closed_orders)
                # update order_count
                order_count += 1

                # prints balances after the order
                print(
                    f"\t\tCurrent currency balance: {account['curr_balance']}")
                print(
                    f"\t\tCurrent cryptocurrency balance: {account['cryptocurr_balance']}\n")

            # calculate current profit
            current_balance_in_curr = float(
                account['curr_balance']) + (float(account['cryptocurr_balance']) * current_price)
            account['total_profit'] = round(current_balance_in_curr -
                                            float(INITIAL_BALANCE), 5)
            # update account_infos.json
            write_json_account_infos(account)

            time.sleep(config.get_Check_Frequency())

        # ______________________________________________________

        # ________________ remove closed orders ________________

        # list containing the currently open buy orders
        buy_orders = [
            buy_order for buy_order in buy_orders if (buy_order['status'] != 'closed') and (buy_order['side'] == 'buy')]
        # list containing the currently open sell orders
        sell_orders = [
            sell_order for sell_order in sell_orders if (sell_order['status'] != 'closed') and (sell_order['side'] == 'sell')]

        # update json files
        write_json_buy_lines(buy_orders)
        write_json_sell_lines(sell_orders)

        # ______________________________________________________

        # __________________ All orders closed _________________

        # the bot stops if the last sell order have been closed
        if len(sell_orders) == 0:
            #sys.exit("Stopping bot, nothing left to sell")
            pass

        # the bot stops if the last buy order have been closed
        if len(buy_orders) == 0:
            #sys.exit("Stopping bot, no money left")
            pass

        # ______________________________________________________

        # prints balances and profit after checking all orders
        print(f"\nCurrent currency balance: {account['curr_balance']}")
        print(
            f"Current cryptocurrency balance: {account['cryptocurr_balance']}")
        print(f"Total investment: {account['total_investment']}")
        print(f"Total profit: {account['total_profit']}\n")
        print(f"Order count: {order_count}\n")

        print("__________________________________________________________\n")

    # ______________________________________________________
