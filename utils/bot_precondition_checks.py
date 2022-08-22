import config


"""
    Checks that all orders in the grid have a price greater than zero and 
    that their value is greater than the minimum set by binance
"""


def check_orders_validity(exchange, current_price):

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


"""
Check that there are sufficient funds in the account to place the initial order and all future orders.
Returns false if there are not enough funds, otherwise returns the total amount
of funds required by the bot (total investment)
"""


def check_balance(exchange, initial_balance, current_price):

    initial_order_amount = float(
        current_price * config.get_Position_Size() * config.get_Num_Sell_Grid_Lines())

    future_buy_amount = 0
    for i in range(config.get_Num_Buy_Grid_Lines()):
        order_price = current_price - (config.get_Grid_Size() * (i+1))
        future_buy_amount += float(order_price * config.get_Position_Size())

    total_investment = round(
        initial_order_amount + future_buy_amount, 5)

    if initial_balance <= total_investment:
        print("Insufficient balance, stop bot and retry ")
        return False

    return total_investment
