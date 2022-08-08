import platform
import multiprocessing
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from datetime import datetime
import tkmacosx
import json
import tkinter

import DemoBot
import config


class GUI(tkinter.Tk):

    def __init__(self, exchange, account) -> None:
        super().__init__()
        self.bot = None
        self.mode = 'demo'
        self.x_vals = []
        self.y_vals = []
        self.exchange = exchange
        self.account = account
        self.configuration_entries = {}

        self.initialize_window()
        self.create_configuration_entries()
        self.create_buttons()
        self.create_chart()

    def initialize_window(self):

        self.geometry('1200x750')
        self.wm_title("Grid Bot")
        self.configure(bg='#212124')
        self.resizable(False, False)

    def create_chart(self):
        plt.style.use('seaborn-deep')

        fig = Figure(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('#212124')

        ax = fig.add_subplot(111)
        ax.set_facecolor('#000000')
        ax.spines['top'].set_color('#818181')
        ax.spines['bottom'].set_color('#818181')
        ax.spines['left'].set_color('#818181')
        ax.spines['right'].set_color('#818181')

        ax.tick_params(axis='x', colors='#818181')
        ax.tick_params(axis='y', colors='#818181')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)

        clear_grid()

        def animate(i):

            buy_orders = read_json_buy_lines()
            sell_orders = read_json_sell_lines()

            self.x_vals.append(datetime.now())
            self.y_vals.append(DemoBot.get_crypto_price(
                self.exchange, config.get_Symbol()))

            ax.clear()

            for order in buy_orders:
                if order['status'] == 'open':
                    ax.axhline(
                        order['price'], color='#FF605C', linewidth=0.5)
            for order in sell_orders:
                if order['status'] == 'open':
                    ax.axhline(
                        order['price'], color='#00Ca4E', linewidth=0.5)

            ax.plot(self.x_vals, self.y_vals, color='#818181')

        ani = FuncAnimation(
            fig, animate, interval=config.get_Check_Frequency())
        self.update()

    def create_configuration_entries(self):

        config_frame_left = tkinter.Frame(master=self)
        config_frame_left.grid(row=1, column=0)

        label_symbol = tkinter.Label(
            config_frame_left, text="Symbol", fg='#818181')
        label_symbol.grid(row=0, column=0)

        label_position_size = tkinter.Label(
            config_frame_left, text="Position Size", fg='#818181')
        label_position_size.grid(row=1, column=0)

        label_check_frequency = tkinter.Label(
            config_frame_left, text="Check Frequency", fg='#818181')
        label_check_frequency.grid(row=2, column=0)

        entry_symbol = tkinter.Entry(config_frame_left, fg='#818181')
        entry_symbol.grid(row=0, column=1)
        self.configuration_entries['symbol'] = entry_symbol

        entry_position_size = tkinter.Entry(config_frame_left)
        entry_position_size.grid(row=1, column=1)
        self.configuration_entries['position_size'] = entry_position_size

        entry_check_frequency = tkinter.Entry(config_frame_left)
        entry_check_frequency.grid(row=2, column=1)
        self.configuration_entries['check_frequency'] = entry_check_frequency

        config_frame_right = tkinter.Frame(master=self)
        config_frame_right.grid(row=1, column=1)

        label_num_buy_grid_lines = tkinter.Label(
            config_frame_right, text="N. buy orders", fg='#818181')
        label_num_buy_grid_lines.grid(row=0, column=0)

        label_num_sell_grid_lines = tkinter.Label(
            config_frame_right, text="N. sell orders Size", fg='#818181')
        label_num_sell_grid_lines.grid(row=1, column=0)

        label_grid_size = tkinter.Label(
            config_frame_right, text="Grid size", fg='#818181')
        label_grid_size.grid(row=2, column=0)

        entry_num_buy_grid_lines = tkinter.Entry(config_frame_right)
        entry_num_buy_grid_lines.grid(row=0, column=1)
        self.configuration_entries['num_buy_grid_lines'] = entry_num_buy_grid_lines

        entry_num_sell_grid_lines = tkinter.Entry(config_frame_right)
        entry_num_sell_grid_lines.grid(row=1, column=1)
        self.configuration_entries['num_sell_grid_lines'] = entry_num_sell_grid_lines

        entry_grid_size = tkinter.Entry(config_frame_right)
        entry_grid_size.grid(row=2, column=1)
        self.configuration_entries['grid_size'] = entry_grid_size

    def create_buttons(self):
        buttons_frame = tkinter.Frame(master=self)
        buttons_frame.configure(bg='#212124')
        buttons_frame.grid(row=1, column=2)

        if platform.system() == 'Darwin':
            button_start_bot = tkmacosx.Button(
                buttons_frame, text="    Start Bot    ", width=300, fg='white', bg='#00Ca4E', borderless=True, command=self.start_bot)
            button_stop_bot = tkmacosx.Button(
                buttons_frame, text="    Stop Bot     ", width=300, fg='white', bg='#FF605C', borderless=True, command=self.stop_bot)
        else:
            pass  # tkinter buttons

        button_start_bot.grid(row=0, column=0)
        button_stop_bot.grid(row=2, column=0)

        empty_label = tkinter.Label(buttons_frame, bg='#212124')
        empty_label.grid(row=1, column=0)

    def start_bot(self):
        if self.bot is None:
            self.save_configuration_params()

            # ani.event_source.stop()
            # ax.clear()
            self.x_vals = []
            self.y_vals = []
            # ani.event_source.start()

            self.bot = multiprocessing.Process(
                target=DemoBot.start_demo_bot, args=(self.exchange, self.account))
            self.bot.start()
        else:
            pass

    def stop_bot(self):
        if self.bot is None:
            pass
        else:
            self.bot.terminate()
            self.bot = None
            clear_grid()

    def save_configuration_params(self):
        pass
        config.set_Symbol(self.configuration_entries['symbol'].get())
        config.set_Position_Size(
            self.configuration_entries['position_size'].get())
        config.set_Check_Frequency(
            self.configuration_entries['check_frequency'].get())
        config.set_Num_Buy_Grid_Lines(
            self.configuration_entries['num_buy_grid_lines'].get())
        config.set_Num_Sell_Grid_Lines(
            self.configuration_entries['num_sell_grid_lines'].get())
        config.set_Grid_Size(self.configuration_entries['grid_size'].get())


@staticmethod
def read_json_buy_lines(filename="buy_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@staticmethod
def read_json_sell_lines(filename="sell_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@staticmethod
def clear_grid():
    empty_list = {}
    with open("buy_lines.json", 'w') as f:
        json.dump(empty_list, f, indent=4)
    with open("sell_lines.json", 'w') as f:
        json.dump(empty_list, f, indent=4)
