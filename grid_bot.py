import ccxt
import time
from pip import List


from utils.write_json_files import *
from utils.get_crypto_price import *
from utils.bot_precondition_checks import *
import config


class GridBot:

    def __init__(self) -> None:
        try:
            # Access with API keys
            exchange = ccxt.binance(
                {"apiKey": config.get_API_key(), "secret": config.get_secret_key()})
            # Throws exception if API key or secret key is empty
            exchange.check_required_credentials()
            # Throws exception if API key or secret key is wrong
            exchange.fetch_balance()
        except Exception as e:
            print("Binance login ERROR, stop bot and retry")
            print(e)
            # Reset API keys
            config.set_API_key("")
            config.set_secret_key("")
            return

        self.start_bot(exchange)


    def start_bot(self, exchange):

        # Get name of currency and cryptocurrency
        currency = config.get_Symbol().split("/")[1]
        cryptocurrency = config.get_Symbol().split("/")[0]

        # Get initial currency balance
        INITIAL_BALANCE = exchange.fetchBalance()[currency]["total"]

        # Get current price
        current_price = get_crypto_price(exchange, config.get_Symbol())

        # Check the validity of grid orders
        if check_orders_validity(exchange, current_price) == False:
            return

        # Check balance
        total_investment = check_balance(
            exchange, INITIAL_BALANCE, current_price)
        if total_investment == False:
            return

        # Counter of executed orders
        order_count = 0

        # Lists with open orders
        buy_orders: List[dict] = []
        sell_orders: List[dict] = []

        # List with closed orders
        closed_orders: List[dict] = []
        write_json_closed_orders(closed_orders)


        # ___________________ Initial order ___________________

        initial_order = exchange.create_market_buy_order(
            config.get_Symbol(), config.get_Position_Size() * config.get_Num_Sell_Grid_Lines())

        initial_order_amount = float(
            initial_order["price"]) * float(initial_order["amount"])

        # ______________________________________________________


        # Create account infos
        balance = exchange.fetchBalance()
        account = {"curr_balance": balance[currency]["total"],
                   "cryptocurr_balance": balance[cryptocurrency]["total"],
                   "total_investment": total_investment,
                   "total_profit": 0.0,
                   }

        # Print initial balance
        print(f"\nInitial currency balance: {account['curr_balance']}")
        print(
            f"Initial cryptocurrecny balance: {account['cryptocurr_balance']}\n")
        print(f"Initial order: {initial_order_amount}\n")
        print(f"Total Investment: {account['total_investment']}\n")


        # _________________ Grid construction __________________

        ticker = exchange.fetch_ticker(config.get_Symbol())

        # Create buy orders
        for i in range(config.get_Num_Buy_Grid_Lines()):
            price = ticker["bid"] - config.get_Grid_Size() * (i+1)
            order = exchange.create_limit_buy_order(
                config.get_Symbol(), config.get_Position_Size(), price)
            buy_orders.append(order)

        # Create sell orders
        for i in range(config.get_Num_Sell_Grid_Lines()):
            price = ticker["bid"] + config.get_Grid_Size() * (i+1)
            order = exchange.create_limit_sell_order(
                config.get_Symbol(), config.get_Position_Size(), price)
            sell_orders.append(order)

        # ______________________________________________________

        # Create json files
        write_json_buy_orders(buy_orders)
        write_json_sell_orders(sell_orders)
        write_json_account_infos(account)

        # ______________________________________________________

        
        # _____________________ Main loop ______________________

        while True:

            print("__________________Checking for orders______________________\n")

            # _____________________ Buy orders ______________________
            # Check all the open buy orders (contained in buy_orders list)

            print("Buy Orders:\n")
            for buy_order in buy_orders:

                print(
                    f"\tchecking buy order {buy_order['id']}:  {buy_order['price']}\n")

                try:
                    order = exchange.fetch_order(
                        buy_order["id"], config.get_Symbol())
                except Exception as e:
                    print("Request failed, retrying...")
                    continue

                # Order has been executed
                if order["status"] == "closed":

                    # Set status of the order in the list buy_orders to "closed" so that
                    # the order is no longer shown in the chart of the GUI
                    buy_order["status"] = "closed"
                    closed_orders.append(order)

                    print(f"\t\tBuy order executed at {order['price']}")

                    # Create a new sell order above the closed order
                    new_sell_price = float(
                        order["price"]) + config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit sell order at {new_sell_price}\n")
                    new_sell_order = exchange.create_limit_sell_order(
                        config.get_Symbol(), config.get_Position_Size(), new_sell_price)
                    sell_orders.append(new_sell_order)

                    # Update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
                    write_json_closed_orders(closed_orders)

                    # Update order_count
                    order_count += 1

            # ______________________________________________________

                # Update balance
                balance = exchange.fetchBalance()
                account["curr_balance"] = balance[currency]["total"]
                account["cryptocurr_balance"] = balance[cryptocurrency]["total"]
                # Calculate current profit
                current_balance_in_curr = float(
                    balance[currency]["total"] + (balance[cryptocurrency]["total"] * get_crypto_price(exchange, config.get_Symbol())))
                account["total_profit"] = round(
                    current_balance_in_curr - float(INITIAL_BALANCE), 5)
                # Update account_infos.json
                write_json_account_infos(account)

                time.sleep(config.get_Check_Frequency())

            # ______________________________________________________


            # ____________________ Sell orders _____________________
            # Check all the open sell orders (contained in sell_orders list)

            print("Sell Orders:\n")
            for sell_order in sell_orders:

                print(
                    f"\tchecking sell order {sell_order['id']}:  {sell_order['price']}\n")

                try:
                    order = exchange.fetch_order(
                        sell_order["id"], config.get_Symbol())
                except Exception as e:
                    print("Request failed, retrying...")
                    continue

                if order["status"] == "closed":

                    # Set status of the order in the list sell_orders to "closed" so that
                    # the order is no longer shown in the chart of the GUI
                    sell_order["status"] = "closed"
                    closed_orders.append(order)

                    print(f"\t\tSell order executed at {order['price']}")

                    # Create a new buy order under the closed order
                    new_buy_price = float(
                        order["price"]) - config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit buy order at {new_buy_price}\n")
                    new_buy_order = exchange.create_limit_buy_order(
                        config.get_Symbol(), config.get_Position_Size(), new_buy_price)
                    buy_orders.append(new_buy_order)

                    # Update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
                    write_json_closed_orders(closed_orders)

                    # Update order_count
                    order_count += 1

            # ______________________________________________________

                # Update balance
                balance = exchange.fetchBalance()
                account["curr_balance"] = balance[currency]["total"]
                account["cryptocurr_balance"] = balance[cryptocurrency]["total"]
                # Calculate current profit
                current_balance_in_curr = float(
                    balance[currency]["total"] + (balance[cryptocurrency]["total"] * get_crypto_price(exchange, config.get_Symbol())))
                account["total_profit"] = round(
                    current_balance_in_curr - float(INITIAL_BALANCE), 5)
                # Update account_infos.json
                write_json_account_infos(account)

                time.sleep(config.get_Check_Frequency())

            # ______________________________________________________


            # ________ Remove closed orders from open orders lists and json files __________

            for order in closed_orders:
                # List containing the open buy orders
                buy_orders = [
                    buy_order for buy_order in buy_orders if buy_order["id"] != order["id"]]
                # List containing the open sell orders
                sell_orders = [
                    sell_order for sell_order in sell_orders if sell_order["id"] != order["id"]]

            # Update json files
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

            # Prints balances and profit after checking all orders
            print(f"\nCurrent currency balance: {account['curr_balance']}")
            print(
                f"Current cryptocurrency balance: {account['cryptocurr_balance']}")
            print(f"Total investment: {account['total_investment']}")
            print(f"Total profit: {account['total_profit']}\n")
            print(f"Order count: {order_count}")

            print("__________________________________________________________\n")

        # ______________________________________________________
