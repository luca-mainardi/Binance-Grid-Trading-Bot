from distutils.command.config import config
from threading import Thread
import ccxt

from DemoBot import start_demo_bot, Demo_Account, Order
from GUI import start_gui
import matplotlib
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from datetime import datetime


exchange = ccxt.binance()
account = Demo_Account(2000)

# buy_orders: List[Order] = []
# sell_orders: List[Order] = []


def main():

    bot = Thread(target=start_demo_bot, args=(
        exchange, account))
    bot.start()
    start_gui(exchange)


if __name__ == '__main__':
    main()
