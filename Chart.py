import ccxt
import matplotlib
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from datetime import datetime
import config
from DemoBot import get_crypto_price
import json

matplotlib.use("Qt5Agg")


def read_json_buy_lines(filename="buy_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def read_json_sell_lines(filename="sell_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def plot_chart(exchange: ccxt) -> None:

    plt.style.use('seaborn')

    x_vals = []
    y_vals = []

    def animate(i):

        buy_orders = read_json_buy_lines()
        sell_orders = read_json_sell_lines()

        print("SELL ORDERS:")
        for order in sell_orders:
            if order['status'] == 'open':
                print(order['price'])

        print("BUY ORDERS:")
        for order in buy_orders:
            if order['status'] == 'open':
                print(order['price'])

        x_vals.append(datetime.now())
        y_vals.append(get_crypto_price(exchange, config.SYMBOL))

        plt.cla()

        for order in buy_orders:
            if order['status'] == 'open':
                plt.axhline(order['price'], color='red', linewidth=0.5)
        for order in sell_orders:
            if order['status'] == 'open':
                plt.axhline(order['price'], color='green', linewidth=0.5)

        plt.plot(x_vals, y_vals, color='black')

    plt.tight_layout()

    ani = FuncAnimation(plt.gcf(), animate,
                        interval=config.CHECK_FREQUENCY)

    plt.show()
