import ccxt
import time
import config
import time
import json
from pip import List


class Grid_Bot:

    def __init__(self) -> None:
        try:
            # Access with API keys
            exchange = ccxt.binance(
                {'apiKey': config.get_API_key(), 'secret': config.get_secret_key()})
            # throws exception if API key or secret key is empty
            exchange.check_required_credentials()
            # throws exception if API key or secret key is wrong
            exchange.fetch_balance()
        except Exception as e:
            print("Binance login ERROR, stop bot and retry")
            print(e)
            # reset API keys
            config.set_API_key("")
            config.set_secret_key("")
            return

        self.start_bot(exchange)

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

    def start_bot(self, exchange):

        # get name of currency and cryptocurrency
        currency = config.get_Symbol().split('/')[1]
        cryptocurrency = config.get_Symbol().split('/')[0]

        # get initial currency balance
        INITIAL_BALANCE = exchange.fetchBalance()[currency]['total']

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

        # counter of executed orders
        order_count = 0

        # lists with open orders
        buy_orders: List[dict] = []
        sell_orders: List[dict] = []

        # list with closed orders
        closed_orders: List[dict] = []
        write_json_closed_orders(closed_orders)

        # ___________________ initial order ___________________

        initial_order = exchange.create_market_buy_order(
            config.get_Symbol(), config.get_Position_Size() * config.get_Num_Sell_Grid_Lines())

        initial_order_amount = float(
            initial_order['price']) * float(initial_order['amount'])

        # ______________________________________________________

        # create account infos
        balance = exchange.fetchBalance()
        account = {'curr_balance': balance[currency]['total'],
                   'cryptocurr_balance': balance[cryptocurrency]['total'],
                   'total_investment': total_investment,
                   'total_profit': 0.0,
                   }

        # print initial balance
        print(f"\nInitial currency balance: {account['curr_balance']}")
        print(
            f"Initial cryptocurrecny balance: {account['cryptocurr_balance']}\n")
        print(f"Initial order: {initial_order_amount}\n")
        print(f"Total Investment: {account['total_investment']}\n")

        # _________________ grid construction __________________

        ticker = exchange.fetch_ticker(config.get_Symbol())

        # create buy orders
        for i in range(config.get_Num_Buy_Grid_Lines()):
            price = ticker['bid'] - config.get_Grid_Size() * (i+1)
            order = exchange.create_limit_buy_order(
                config.get_Symbol(), config.get_Position_Size(), price)
            buy_orders.append(order)

        # create sell orders
        for i in range(config.get_Num_Sell_Grid_Lines()):
            price = ticker['bid'] + config.get_Grid_Size() * (i+1)
            order = exchange.create_limit_sell_order(
                config.get_Symbol(), config.get_Position_Size(), price)
            sell_orders.append(order)

        # ______________________________________________________

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

                print(
                    f"\tchecking buy order {buy_order['id']}:  {buy_order['price']}\n")

                try:
                    order = exchange.fetch_order(
                        buy_order['id'], config.get_Symbol())
                except Exception as e:
                    print("Request failed, retrying...")
                    continue

                # order has been executed
                if order['status'] == 'closed':

                    # set status of the order in the list buy_orders to 'closed' so that
                    # the order is no longer shown in the chart of the GUI
                    buy_order['status'] = 'closed'
                    closed_orders.append(order)

                    print(f"\t\tBuy order executed at {order['price']}")

                    # create a new sell order above the closed order
                    new_sell_price = float(
                        order['price']) + config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit sell order at {new_sell_price}\n")
                    new_sell_order = exchange.create_limit_sell_order(
                        config.get_Symbol(), config.get_Position_Size(), new_sell_price)
                    sell_orders.append(new_sell_order)

                    # update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
                    write_json_closed_orders(closed_orders)

                    # update order_count
                    order_count += 1

            # ______________________________________________________

                # update balance
                balance = exchange.fetchBalance()
                account['curr_balance'] = balance[currency]['total']
                account['cryptocurr_balance'] = balance[cryptocurrency]['total']
                # calculate current profit
                current_balance_in_curr = float(
                    balance[currency]['total'] + (balance[cryptocurrency]['total'] * get_crypto_price(exchange, config.get_Symbol())))
                account['total_profit'] = round(
                    current_balance_in_curr - float(INITIAL_BALANCE), 5)
                # update account_infos.json
                write_json_account_infos(account)

                time.sleep(config.get_Check_Frequency())

            # ______________________________________________________

            # ____________________ sell orders _____________________
            # check all the open sell orders (contained in sell_orders list)

            print("Sell Orders:\n")
            for sell_order in sell_orders:

                print(
                    f"\tchecking sell order {sell_order['id']}:  {sell_order['price']}\n")

                try:
                    order = exchange.fetch_order(
                        sell_order['id'], config.get_Symbol())
                except Exception as e:
                    print("Request failed, retrying...")
                    continue

                if order['status'] == 'closed':

                    # set status of the order in the list sell_orders to 'closed' so that
                    # the order is no longer shown in the chart of the GUI
                    sell_order['status'] = 'closed'
                    closed_orders.append(order)

                    print(f"\t\tSell order executed at {order['price']}")

                    # create a new buy order under the closed order
                    new_buy_price = float(
                        order['price']) - config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit buy order at {new_buy_price}\n")
                    new_buy_order = exchange.create_limit_buy_order(
                        config.get_Symbol(), config.get_Position_Size(), new_buy_price)
                    buy_orders.append(new_buy_order)

                    # update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
                    write_json_closed_orders(closed_orders)

                    # update order_count
                    order_count += 1

            # ______________________________________________________

                # update balance
                balance = exchange.fetchBalance()
                account['curr_balance'] = balance[currency]['total']
                account['cryptocurr_balance'] = balance[cryptocurrency]['total']
                # calculate current profit
                current_balance_in_curr = float(
                    balance[currency]['total'] + (balance[cryptocurrency]['total'] * get_crypto_price(exchange, config.get_Symbol())))
                account['total_profit'] = round(
                    current_balance_in_curr - float(INITIAL_BALANCE), 5)
                # update account_infos.json
                write_json_account_infos(account)

                time.sleep(config.get_Check_Frequency())

            # ______________________________________________________

            # ________ remove closed orders from open orders lists and json files __________

            for order in closed_orders:
                # list containing the open buy orders
                buy_orders = [
                    buy_order for buy_order in buy_orders if buy_order['id'] != order['id']]
                # list containing the open sell orders
                sell_orders = [
                    sell_order for sell_order in sell_orders if sell_order['id'] != order['id']]

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
            print(f"Order count: {order_count}")

            print("__________________________________________________________\n")

        # ______________________________________________________


# return the current price of the symbol passed as parameter
@staticmethod
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
