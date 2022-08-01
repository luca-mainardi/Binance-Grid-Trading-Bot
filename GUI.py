from cmath import exp
import ccxt
import matplotlib
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

from datetime import datetime
import config
from DemoBot import get_crypto_price
import json
import tkinter
import sys

# matplotlib.use("Qt5Agg")


def read_json_buy_lines(filename="buy_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def read_json_sell_lines(filename="sell_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def start_gui(exchange: ccxt) -> None:

    plt.style.use('seaborn')

    window = tkinter.Tk()
    window.wm_title("Grid Bot")

    fig = Figure(figsize=(5, 4), dpi=100)
    a = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    x_vals = []
    y_vals = []

    def animate(i):

        buy_orders = read_json_buy_lines()
        sell_orders = read_json_sell_lines()

        # print("SELL ORDERS:")
        # for order in sell_orders:
        #     if order['status'] == 'open':
        #         print(order['price'])

        # print("BUY ORDERS:")
        # for order in buy_orders:
        #     if order['status'] == 'open':
        #         print(order['price'])

        x_vals.append(datetime.now())
        y_vals.append(get_crypto_price(exchange, config.SYMBOL))

        # plt.cla()
        a.clear()

        for order in buy_orders:
            if order['status'] == 'open':
                a.axhline(order['price'], color='red', linewidth=0.5)
        for order in sell_orders:
            if order['status'] == 'open':
                a.axhline(order['price'], color='green', linewidth=0.5)

        a.plot(x_vals, y_vals, color='black')

    # plt.tight_layout()

    # ani = FuncAnimation(plt.gcf(), animate,
    #                   interval=config.CHECK_FREQUENCY)

    def on_key_press(event):
        key_press_handler(event, canvas, toolbar)

    canvas.mpl_connect("key_press_event", on_key_press)

    def _quit():
        print("_______________________BUTTON___________________________")
        window.quit()     # stops mainloop
        window.destroy()  # this is necessary on Windows to prevent
        # # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    button = tkinter.Button(master=window, text="Quit", command=_quit)
    button.pack(side=tkinter.BOTTOM)

    ani = FuncAnimation(fig, animate, interval=config.CHECK_FREQUENCY)
    tkinter.mainloop()
    # plt.show()
