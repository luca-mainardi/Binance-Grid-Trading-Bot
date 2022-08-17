import ccxt
import time
import config
import time
import sys
import json
from pip import List


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


def start_bot(exchange):

    print("_____________________ START BOT _____________________\n")

    # get name of currency and cryptocurrency
    currency = config.get_Symbol().split('/')[1]
    cryptocurrency = config.get_Symbol().split('/')[1]
    # get initial currency balance
    INITIAL_BALANCE = exchange.fetchBalance()[currency]['total']

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

    # ______________________________________________________

    # create account infos
    balance = exchange.fetchBalance()
    account = {'curr_balance': balance[currency]['total'],
               'cryptocurr_balance': balance[cryptocurrency]['total'],
               'total_investment': 0.0,
               'total_profit': 0.0,
               }

    # print initial balance
    print(f"\nInitial currency balance: {account['curr_balance']}")
    print(f"Initial cryptocurrecny balance: {account['cryptocurr_balance']}")

    # _________________ grid construction __________________

    ticker = exchange.fetch_ticker(config.get_Symbol())

    for i in range(config.get_Num_Buy_Grid_Lines()):
        price = ticker['bid'] - config.get_Grid_Size() * (i+1)
        order = exchange.create_limit_buy_order(
            config.get_Symbol(), config.get_Position_Size(), price)
        buy_orders.append(order['info'])

    for i in range(config.get_Num_Sell_Grid_Lines()):
        price = ticker['bid'] + config.get_Grid_Size() * (i+1)
        order = exchange.create_limit_sell_order(
            config.get_Symbol(), config.get_Position_Size(), price)
        sell_orders.append(order['info'])

    # ______________________________________________________

    # calculate total investment
    initial_order_amount = initial_order['price'] * initial_order['amount']
    future_buy_amount = 0

    for buy_order in buy_orders:
        future_buy_amount += float(buy_order['amount']) * \
            float(buy_order['price'])

    account['total_investment'] = round(
        initial_order_amount + future_buy_amount, 2)

    print(f"Total Investment: {account['total_investment']}\n")

    # create json files
    write_json_buy_lines(buy_orders)
    write_json_sell_lines(sell_orders)
    write_json_account_infos(account)

    # ______________________________________________________

    # _____________________ main loop ______________________

    while True:
        #closed_order_ids = []

        print("__________________Checking for orders______________________\n")

        # _____________________ buy orders ______________________
        # check all the open buy orders (contained in buy_orders list)

        print("Buy Orders:\n")
        for buy_order in buy_orders:

            # print price of the order
            print(
                f"checking buy order {buy_order['id']}:  {buy_order['price']}")

            try:
                order = exchange.fetch_order(buy_order['id'])
            except Exception as e:
                print("Request failed, retrying...")
                continue

            order_info = order['info']

            # order has been executed
            if order_info['status'] == 'closed':

                # set status to 'closed' so that the order is no longer shown in the chart of the GUI
                buy_order['status'] = 'closed'
                closed_orders.append(order_info)

                print(f"\tBuy order executed at {order_info['price']}")

                # create a new sell order above the closed order
                new_sell_price = float(
                    order_info['price']) + config.get_Grid_Size()
                print(f"\tCreating new limit sell order at {new_sell_price}")
                new_sell_order = exchange.create_limit_sell_order(
                    config.get_Symbol(), config.get_Position_Size(), new_sell_price)
                sell_orders.append(new_sell_order['info'])

                # update json files
                write_json_buy_lines(buy_orders)
                write_json_sell_lines(sell_orders)
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
                current_balance_in_curr - float(INITIAL_BALANCE), 2)
            # update account_infos.json
            write_json_account_infos(account)

            print(f"\t\t\tCurrent currency balance: {account['curr_balance']}")
            print(
                f"\t\t\tCurrent cryptocurrency balance: {account['cryptocurr_balance']}\n")

            time.sleep(config.get_Check_Frequency())

        # ______________________________________________________

        # ____________________ sell orders _____________________
        # check all the open sell orders (contained in sell_orders list)

        print("Sell Orders:\n")
        for sell_order in sell_orders:

            # print price of the order
            print(
                f"checking sell order {sell_order['id']}:  {sell_order['price']}")

            try:
                order = exchange.fetch_order(sell_order['id'])
            except Exception as e:
                print("Request failed, retrying...")
                continue

            order_info = order['info']

            if order_info['status'] == 'closed':

                # set status to 'closed' so that the order is no longer shown in the chart of the GUI
                buy_order['status'] = 'closed'
                closed_orders.append(order_info)

                print(f"\tSell order executed at {order_info['price']}")

                # create a new buy order under the closed order
                new_buy_price = float(
                    order_info['price']) - config.get_Grid_Size()
                print(f"\tCreating new limit buy order at {new_buy_price}")
                new_buy_order = exchange.create_limit_buy_order(
                    config.get_Symbol(), config.get_Position_Size(), new_buy_price)
                buy_orders.append(new_buy_order['info'])

                # update json files
                write_json_buy_lines(buy_orders)
                write_json_sell_lines(sell_orders)
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
                current_balance_in_curr - float(INITIAL_BALANCE), 2)
            # update account_infos.json
            write_json_account_infos(account)

            print(f"\t\t\tCurrent currency balance: {account['curr_balance']}")
            print(
                f"\t\t\tCurrent cryptocurrency balance: {account['cryptocurr_balance']}\n")

            time.sleep(config.get_Check_Frequency())

        # ______________________________________________________

        # ________________ remove closed orders ________________

        for order in closed_orders:
            # list containing the open buy orders
            buy_orders = [
                buy_order for buy_order in buy_orders if buy_order['id'] != order['id']]
            # list containing the open sell orders
            sell_orders = [
                sell_order for sell_order in sell_orders if sell_order['id'] != order['id']]

        # update json files
        write_json_buy_lines(buy_orders)
        write_json_sell_lines(sell_orders)

        # ______________________________________________________

        # __________________ All orders closed _________________

        # the bot stops if the last sell order have been closed
        if len(sell_orders) == 0:
            sys.exit("Stopping bot, nothing left to sell")

        # the bot stops if the last buy order have been closed
        if len(buy_orders) == 0:
            sys.exit("Stopping bot, no money left")

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
