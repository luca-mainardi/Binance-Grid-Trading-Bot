from cmath import exp
from tkinter import font
import ccxt
import matplotlib
from matplotlib import colors
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler

from datetime import datetime

from pyparsing import col
import config
from DemoBot import get_crypto_price
import json
import tkinter

# matplotlib.use("Qt5Agg")


def read_json_buy_lines(filename="buy_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def read_json_sell_lines(filename="sell_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


def start_gui(exchange: ccxt) -> None:

    plt.style.use('seaborn-deep')

    window = tkinter.Tk()
    window.wm_title("Grid Bot")
    window.configure(bg='#212124')
    window.geometry('1200x700')
    window.resizable(False, False)
    #window.attributes('-fullscreen', False)

    #window.columnconfigure(0, weight=1)
    #window.rowconfigure(0, weight=1)

    fig = Figure(figsize=(8, 6), dpi=100)
    fig.patch.set_facecolor('#212124')
    # fig.suptitle("TITOLO")

    ax = fig.add_subplot(111)
    ax.set_facecolor('#000000')
    ax.spines['top'].set_color('#818181')
    ax.spines['bottom'].set_color('#818181')
    ax.spines['left'].set_color('#818181')
    ax.spines['right'].set_color('#818181')

    ax.tick_params(axis='x', colors='#818181')
    ax.tick_params(axis='y', colors='#818181')

    #plot_frame = tkinter.Frame(window)
    # plot_frame.configure(bg='white')

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    #canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)

    #toolbar = NavigationToolbar2Tk(canvas, plot_frame)
    # toolbar.configure(bg='white')
    # toolbar.update()
    #canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    #plot_frame.grid(row=0, column=0)

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
        ax.clear()

        for order in buy_orders:
            if order['status'] == 'open':
                ax.axhline(order['price'], color='red', linewidth=0.5)
        for order in sell_orders:
            if order['status'] == 'open':
                ax.axhline(order['price'], color='green', linewidth=0.5)

        ax.plot(x_vals, y_vals, color='#818181')

    # plt.tight_layout()

    # ani = FuncAnimation(plt.gcf(), animate,
    #                   interval=config.CHECK_FREQUENCY)

    # def on_key_press(event):
    #     key_press_handler(event, canvas, toolbar)

    # canvas.mpl_connect("key_press_event", on_key_press)

    def _quit():
        print("_______________________BUTTON___________________________")
        window.quit()     # stops mainloop
        window.destroy()  # this is necessary on Windows to prevent
        # # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    # button = tkinter.Button(master=plot_frame, text="Quit", command=_quit)
    # button.pack(side=tkinter.BOTTOM)

    # # ---------------------------------------------------------------
    # left configuration farme
    config_frame_left = tkinter.Frame(master=window)

    label_symbol = tkinter.Label(
        config_frame_left, text="Symbol", fg='#818181')
    label_position_size = tkinter.Label(
        config_frame_left, text="Position Size", fg='#818181')
    label_check_frequency = tkinter.Label(
        config_frame_left, text="Check Frequency", fg='#818181')

    entry_symbol = tkinter.Entry(config_frame_left)
    entry_position_size = tkinter.Entry(config_frame_left)
    entry_check_frequency = tkinter.Entry(config_frame_left)

    # right configuration frame
    config_frame_right = tkinter.Frame(master=window)

    label_num_buy_grid_lines = tkinter.Label(
        config_frame_right, text="Symbol", fg='#818181')
    label_num_buy_sell_lines = tkinter.Label(
        config_frame_right, text="Position Size", fg='#818181')
    label_grid_size = tkinter.Label(
        config_frame_right, text="Check Frequency", fg='#818181')

    entry_num_buy_grid_lines = tkinter.Entry(config_frame_right)
    entry_num_sell_grid_lines = tkinter.Entry(config_frame_right)
    entry_grid_size = tkinter.Entry(config_frame_right)

    # grid configuration frame left
    label_symbol.grid(row=0, column=0)
    label_position_size.grid(row=1, column=0)
    label_check_frequency.grid(row=2, column=0)

    entry_symbol.grid(row=0, column=1)
    entry_position_size.grid(row=1, column=1)
    entry_check_frequency.grid(row=2, column=1)

    label_num_buy_grid_lines.grid(row=0, column=0)
    label_num_buy_sell_lines.grid(row=1, column=0)
    label_grid_size.grid(row=2, column=0)

    entry_num_buy_grid_lines.grid(row=0, column=1)
    entry_num_sell_grid_lines.grid(row=1, column=1)
    entry_grid_size.grid(row=2, column=1)

    config_frame_left.grid(row=1, column=0)
    config_frame_right.grid(row=1, column=1)

    # frame1 = tkinter.Frame(master=frame)
    # frame1.configure(bg='red')
    # frame1.grid(row=0, column=0)

    # frame2 = tkinter.Frame(master=frame)
    # frame2.configure(bg='green')
    # frame2.grid(row=0, column=1)

    # redbutton = tkinter.Button(frame, text="Red", fg="red")
    # redbutton.pack(side=tkinter.LEFT)

    # greenbutton = tkinter.Button(frame, text="Brown", fg="brown")
    # greenbutton.pack(side=tkinter.LEFT)

    # bluebutton = tkinter.Button(frame, text="Blue", fg="blue")
    # bluebutton.pack(side=tkinter.LEFT)

    # blackbutton = tkinter.Button(
    #     canvas.get_tk_widget(), text="Black", fg="black")
    # blackbutton.pack(side=tkinter.BOTTOM)
    # ---------------------------------------------------------------

    ani = FuncAnimation(fig, animate, interval=config.CHECK_FREQUENCY)
    tkinter.mainloop()
    # plt.show()
