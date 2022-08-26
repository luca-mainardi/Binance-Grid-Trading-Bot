import ccxt
import time
from pip import List

from utils.write_json_files import *
from utils.get_crypto_price import *
from utils.bot_precondition_checks import *
import config

"""
Class that simulates a binance limit order
"""
# ____________________ Order Class _____________________

class Order:
    def __init__(self, amount: float, price: float, side):
        self.price = price
        self.amount = amount  # In cryptocurrency
        self.status = "open"  # "open" or "closed"
        self.side = side  # "buy" or "sell"

    def toDict(self):
        return {"price": self.price,
                "amount": self.amount,
                "status": self.status,
                "side": self.side}

# ______________________________________________________


"""
Class that starts a bot in demo mode.

The demo mode operates on a dummy account with $10000 inside, which is reset every time 
you start the program. The demo mode does not consider commission-free trading pairs and 
applies a 0.2% commission to all of them, therefore earnings obtained with the demo mode 
may differ from the real ones.
"""

class DemoBot:

    def __init__(self) -> None:
        exchange = ccxt.binance()
        self.start_demo_bot(exchange)

    def start_demo_bot(self, exchange):

        INITIAL_BALANCE = 10000.0

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

        # Create account infos
        account = {"curr_balance": INITIAL_BALANCE,
                   "cryptocurr_balance": 0.0,
                   "total_investment": 0.0,
                   "total_profit": 0.0,
                   }

        # Counter of order executed
        order_count = 0

        # Lists with open orders
        buy_orders: List[dict] = []
        sell_orders: List[dict] = []

        # List with closed orders
        closed_orders: List[dict] = []
        write_json_closed_orders(closed_orders)

        # ___________________ Initial order ___________________

        ticker = exchange.fetch_ticker(config.get_Symbol())

        # Amount to buy
        first_amount_cryptocurr = config.get_Position_Size() * \
            config.get_Num_Sell_Grid_Lines()
        first_amount_curr = first_amount_cryptocurr * float(ticker["last"])

        fees = first_amount_curr * 0.002

        # Buy initial amount of cryptocurrency
        account["cryptocurr_balance"] += round(first_amount_cryptocurr, 5)
        account["curr_balance"] -= round(first_amount_curr + fees, 5)

        # ______________________________________________________

        # Print initial balance
        print(f"\nInitial currency balance: {account['curr_balance']}")
        print(f"Initial cryptocurrecny balance: {account['cryptocurr_balance']}\n")

        # _________________ Grid construction __________________

        # Create buy orders
        for i in range(config.get_Num_Buy_Grid_Lines()):
            price = ticker["bid"] - config.get_Grid_Size() * (i+1)

            order = Order(config.get_Position_Size(), price, "buy")
            buy_orders.append(order.toDict())

        # Create sell orders
        for i in range(config.get_Num_Sell_Grid_Lines()):
            price = ticker["bid"] + config.get_Grid_Size() * (i+1)

            order = Order(config.get_Position_Size(), price, "sell")
            sell_orders.append(order.toDict())

        # ______________________________________________________

        # Calculate total investment
        future_buy_amount = 0

        for buy_order in buy_orders:
            future_buy_amount += float(buy_order["amount"]) * \
                float(buy_order["price"])

        account["total_investment"] = round(
            first_amount_curr + future_buy_amount, 5)

        print(f"Total Investment: {account['total_investment']}\n")

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

                # Wrong order side (sell order in buy_orders)
                if buy_order["side"] != "buy":
                    raise Exception("Wrong side in buy_orders")

                # Print price of the order
                print(f"\tChecking buy order {buy_order['price']}")

                # Get current price of cryptocurrency
                current_price = get_crypto_price(exchange, config.get_Symbol())
                print(f"\tCurrent price: {current_price}\n")

                # Order can be closed
                if current_price <= buy_order["price"] and (buy_order["status"] == "open"):

                    # Buy cryptocurrency
                    account["cryptocurr_balance"] = round(
                        account["cryptocurr_balance"] + buy_order["amount"], 5)
                    fees = buy_order["amount"] * current_price * 0.002
                    account["curr_balance"] = round(account["curr_balance"]-(buy_order["amount"]
                                                                             * current_price) - fees, 5)

                    # Close order
                    buy_order["status"] = "closed"
                    closed_orders.append(buy_order)

                    print(f"\t\tBuy order executed at {buy_order['price']}")

                    # Create a new sell order above the closed order
                    new_sell_price = buy_order["price"] + \
                        config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit sell order at {new_sell_price}\n")
                    new_sell_order = Order(
                        config.get_Position_Size(), new_sell_price, "sell")
                    sell_orders.append(new_sell_order.toDict())

                    # Update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
                    write_json_closed_orders(closed_orders)

                    # Update order_count
                    order_count += 1

                    # Prints balances after the order
                    print(
                        f"\t\tCurrent currency balance: {account['curr_balance']}")
                    print(
                        f"\t\tCurrent cryptocurrency balance: {account['cryptocurr_balance']}\n")

                # Calculate current profit
                current_balance_in_curr = float(
                    account["curr_balance"]) + (float(account["cryptocurr_balance"]) * current_price)
                account["total_profit"] = round(current_balance_in_curr -
                                                float(INITIAL_BALANCE), 5)
                # Update account_infos.json
                write_json_account_infos(account)

                time.sleep(config.get_Check_Frequency())

            # ______________________________________________________

            # ____________________ Sell orders _____________________
            # Check all the open sell orders (contained in sell_orders list)

            print("Sell Orders:\n")
            for sell_order in sell_orders:

                # Wrong order side (buy order in sell_orders)
                if sell_order["side"] != "sell":
                    raise Exception("Wrong side in sell_orders")

                # Print price of the order
                print(f"\tchecking sell order {sell_order['price']}")

                # Get current price of cryptocurrency
                current_price = get_crypto_price(exchange, config.get_Symbol())
                print(f"\tcurrent price: {current_price}\n")

                # Order can be closed
                if (current_price >= sell_order["price"]) and (sell_order["status"] == "open"):

                    # Sell cryptocurrency
                    account["cryptocurr_balance"] = round(
                        account["cryptocurr_balance"] - sell_order["amount"], 5)
                    fees = sell_order["amount"] * current_price * 0.002
                    account["curr_balance"] = round(
                        account["curr_balance"] + (sell_order["amount"] * current_price) - fees, 5)

                    # Close order
                    sell_order["status"] = "closed"
                    closed_orders.append(sell_order)

                    print(f"\t\tSell order executed at {current_price}")

                    # Create a new buy order below the closed order
                    new_buy_price = sell_order["price"] - \
                        config.get_Grid_Size()
                    print(
                        f"\t\tCreating new limit buy order at {new_buy_price}\n")
                    new_buy_order = Order(
                        config.get_Position_Size(), new_buy_price, "buy")
                    buy_orders.append(new_buy_order.toDict())

                    # Update json files
                    write_json_buy_orders(buy_orders)
                    write_json_sell_orders(sell_orders)
                    write_json_closed_orders(closed_orders)
                    # update order_count
                    order_count += 1

                    # Prints balances after the order
                    print(
                        f"\t\tCurrent currency balance: {account['curr_balance']}")
                    print(
                        f"\t\tCurrent cryptocurrency balance: {account['cryptocurr_balance']}\n")

                # Calculate current profit
                current_balance_in_curr = float(
                    account["curr_balance"]) + (float(account["cryptocurr_balance"]) * current_price)
                account["total_profit"] = round(current_balance_in_curr -
                                                float(INITIAL_BALANCE), 5)
                # Update account_infos.json
                write_json_account_infos(account)

                time.sleep(config.get_Check_Frequency())

            # ______________________________________________________

            # ________ Remove closed orders from open orders lists and json files __________

            # List containing the currently open buy orders
            buy_orders = [
                buy_order for buy_order in buy_orders if (buy_order["status"] != "closed") and (buy_order["side"] == "buy")]
            # List containing the currently open sell orders
            sell_orders = [
                sell_order for sell_order in sell_orders if (sell_order["status"] != "closed") and (sell_order["side"] == "sell")]

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
            print(f"Order count: {order_count}\n")

            print("__________________________________________________________\n")

        # ______________________________________________________
