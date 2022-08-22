import time
from pip import List
import time
import json

import config
import ccxt

"""
Class that simulates a binance limit order
"""
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


"""
Class that starts a bot in demo mode

The demo mode operates on a dummy account with $10000 inside, which is reset every time 
you start the program. The demo mode does not consider commission-free trading pairs and 
applies a 0.2% commission to all of them, therefore earnings obtained with the demo mode 
may differ from the real ones.
"""


class Demo_Bot:

    def __init__(self) -> None:

        exchange = ccxt.binance()
        self.start_demo_bot(exchange)

    def check_orders_validity(self, exchange, current_price):
        """
        Checks that all orders in the grid have a price greater than zero and 
        that their value is greater than the minimum set by binance
        """

        # get price of the lowest order in the grid
        lowest_order_price = current_price - config.get_Num_Buy_Grid_Lines() * \
            config.get_Grid_Size()

        # check that the lowest order has price greater than zero (all orders have price greater than zero)
        if lowest_order_price < 0:
            print("The grid contains orders with negative price, stop bot and retry")
            return False

        # Get the minimum cost that an order on binance can have in the selected market
        market = exchange.load_markets()[config.get_Symbol()]
        min_order = float(market['limits']['cost']['min'])

       # checks that grid orders fulfill binance price requirements
        if lowest_order_price * config.get_Position_Size() < min_order:
            print(
                "Orders do not fulfill binance's minimum price requirements, stop bot and retry")
            return False

        return True

    def check_balance(self, exchange, initial_balance, current_price):
        """
        Check that there are sufficient funds in the account to place the initial order and all future orders.
        Returns false if there are not enough funds, otherwise returns the total amount
        of funds required by the bot (total investment)
        """

        initial_order_amount = float(
            current_price * config.get_Position_Size() * config.get_Num_Sell_Grid_Lines())

        future_buy_amount = 0
        for i in range(config.get_Num_Buy_Grid_Lines()):
            order_price = current_price - (config.get_Grid_Size() * (i+1))
            future_buy_amount += float(order_price *
                                       config.get_Position_Size())

        total_investment = round(
            initial_order_amount + future_buy_amount, 5)

        if initial_balance <= total_investment:
            print("Insufficient balance, stop bot and retry ")
            return False

        return total_investment

    def start_demo_bot(self, exchange):

        INITIAL_BALANCE = 10000.0

        # get current price
        current_price = get_crypto_price(exchange, config.get_Symbol())

        # check the validity of grid orders
        if self.check_orders_validity(exchange, current_price) == False:
            return

        # check balance
        total_investment = self.check_balance(
            exchange, INITIAL_BALANCE, current_price)
        if total_investment == False:
            return

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

        ticker = exchange.fetch_ticker(config.get_Symbol())

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
        print(
            f"Initial cryptocurrecny balance: {account['cryptocurr_balance']}\n")

        # _________________ grid construction __________________

        # create buy orders
        for i in range(config.get_Num_Buy_Grid_Lines()):
            price = ticker['bid'] - config.get_Grid_Size() * (i+1)

            order = Order(config.get_Position_Size(), price, 'buy')
            buy_orders.append(order.toDict())

        # create sell orders
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
        write_json_buy_orders(buy_orders)
        write_json_sell_orders(sell_orders)
        write_json_account_infos(account)

        # ______________________________________________________

        # _____________________ main loop ______________________

        while True:

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
                    new_sell_price = buy_order['price'] + \
                        config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit sell order at {new_sell_price}\n")
                    new_sell_order = Order(
                        config.get_Position_Size(), new_sell_price, 'sell')
                    sell_orders.append(new_sell_order.toDict())

                    # update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
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
                    new_buy_price = sell_order['price'] - \
                        config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit buy order at {new_buy_price}\n")
                    new_buy_order = Order(
                        config.get_Position_Size(), new_buy_price, 'buy')
                    buy_orders.append(new_buy_order.toDict())

                    # update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
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

            # ________ remove closed orders from open orders lists and json files __________

            # list containing the currently open buy orders
            buy_orders = [
                buy_order for buy_order in buy_orders if (buy_order['status'] != 'closed') and (buy_order['side'] == 'buy')]
            # list containing the currently open sell orders
            sell_orders = [
                sell_order for sell_order in sell_orders if (sell_order['status'] != 'closed') and (sell_order['side'] == 'sell')]

            # update json files
            write_json_buy_orders(buy_orders)
            write_json_sell_orders(sell_orders)

            # ________________________________________________________________

            # __________________ All orders closed _________________

            # If all buy or sell orders have been executed the bot continues to work waiting
            # for the price to return to the grid range.
            # You can alternatively set a stop loss or stop the bot as soon as it exits the grid

            # Nothing left to sell
            if len(sell_orders) == 0:
                pass

            # Nothing left to sell
            if len(buy_orders) == 0:
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


@staticmethod
# return the current price of the symbol passed as parameter
def get_crypto_price(exchange, symbol):
    return float(exchange.fetch_ticker(symbol)['last'])


# _____________________ Methods for writing to json files _____________________

@staticmethod
def write_json_buy_orders(data, filename="buy_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@staticmethod
def write_json_sell_orders(data, filename="sell_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@staticmethod
def write_json_closed_orders(data, filename="closed_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@staticmethod
def write_json_account_infos(data, filename="account_infos.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
