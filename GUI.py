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
from DemoBot import Demo_Bot
import config
import Colours
import ccxt
from GridBot import Grid_Bot


class GUI(tkinter.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.current_price = 0
        self.bot = None
        self.mode = 'demo'
        self.x_vals = []
        self.y_vals = []
        self.exchange = ccxt.binance()
        self.configuration_entries = {}

        clear_open_orders_json_files()
        clear_closed_orders_json_file()
        reset_account_infos_json_file()

        self.initialize_window()
        self.create_configuration_entries()
        self.create_buttons()
        self.create_mode_switch_buttons()
        self.create_label_price()
        self.create_frame_closed_orders()
        self.create_frame_account_infos()
        self.create_frame_login()
        self.create_chart()

    def initialize_window(self):

        self.geometry('1200x720')
        self.wm_title("Grid Bot")
        self.configure(bg=Colours.BACKGROUND)
        self.resizable(False, False)

    def create_chart(self):
        plt.style.use('seaborn-deep')

        fig = Figure(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor(Colours.BACKGROUND)

        ax = fig.add_subplot(111)
        ax.set_facecolor('black')
        ax.spines['top'].set_color(Colours.LIGHT_GREY)
        ax.spines['bottom'].set_color(Colours.LIGHT_GREY)
        ax.spines['left'].set_color(Colours.LIGHT_GREY)
        ax.spines['right'].set_color(Colours.LIGHT_GREY)

        ax.tick_params(axis='x', colors=Colours.LIGHT_GREY)
        ax.tick_params(axis='y', colors=Colours.LIGHT_GREY)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, rowspan=8, column=0, columnspan=2)

        def animate(i):

            try:
                self.current_price = get_crypto_price(
                    self.exchange, config.get_Symbol())

                buy_orders = read_json_buy_lines()
                sell_orders = read_json_sell_lines()

                self.x_vals.append(datetime.now())
                self.y_vals.append(self.current_price)

                ax.clear()

                for order in buy_orders:
                    if order['status'] == 'open':
                        ax.axhline(
                            order['price'], color=Colours.RED, linewidth=0.5)
                for order in sell_orders:
                    if order['status'] == 'open':
                        ax.axhline(
                            order['price'], color=Colours.GREEN, linewidth=0.5)

                ax.plot(self.x_vals, self.y_vals, color=Colours.LIGHT_GREY)
            except Exception as e:
                print(e)
                animate(i=None)

        ani = FuncAnimation(
            fig, animate, interval=config.get_Check_Frequency())
        self.update()

    def create_configuration_entries(self):

        config_frame_left = tkinter.Frame(master=self, bg=Colours.GREY)
        config_frame_left.grid(row=8, column=0)

        label_symbol = tkinter.Label(
            config_frame_left, text="Symbol", fg=Colours.LIGHT_GREY, bg=Colours.GREY)
        label_symbol.grid(row=0, column=0)

        label_position_size = tkinter.Label(
            config_frame_left, text="Position Size", fg=Colours.LIGHT_GREY, bg=Colours.GREY)
        label_position_size.grid(row=1, column=0)

        label_check_frequency = tkinter.Label(
            config_frame_left, text="Check Frequency", fg=Colours.LIGHT_GREY, bg=Colours.GREY)
        label_check_frequency.grid(row=2, column=0)

        entry_symbol = tkinter.Entry(
            config_frame_left, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, highlightbackground=Colours.GREY)
        entry_symbol.insert(tkinter.END, config.get_Symbol())
        entry_symbol.grid(row=0, column=1)
        self.configuration_entries['symbol'] = entry_symbol

        entry_position_size = tkinter.Entry(
            config_frame_left, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, highlightbackground=Colours.GREY)
        entry_position_size.insert(tkinter.END, config.get_Position_Size())
        entry_position_size.grid(row=1, column=1)
        self.configuration_entries['position_size'] = entry_position_size

        entry_check_frequency = tkinter.Entry(
            config_frame_left, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, highlightbackground=Colours.GREY)
        entry_check_frequency.insert(tkinter.END, config.get_Check_Frequency())
        entry_check_frequency.grid(row=2, column=1)
        self.configuration_entries['check_frequency'] = entry_check_frequency

        config_frame_right = tkinter.Frame(master=self, bg=Colours.GREY)
        config_frame_right.grid(row=8, column=1)

        label_num_buy_grid_lines = tkinter.Label(
            config_frame_right, text="N. buy orders", fg=Colours.LIGHT_GREY, bg=Colours.GREY)
        label_num_buy_grid_lines.grid(row=0, column=0)

        label_num_sell_grid_lines = tkinter.Label(
            config_frame_right, text="N. sell orders Size", fg=Colours.LIGHT_GREY, bg=Colours.GREY)
        label_num_sell_grid_lines.grid(row=1, column=0)

        label_grid_size = tkinter.Label(
            config_frame_right, text="Grid size", fg=Colours.LIGHT_GREY, bg=Colours.GREY)
        label_grid_size.grid(row=2, column=0)

        entry_num_buy_grid_lines = tkinter.Entry(
            config_frame_right, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, highlightbackground=Colours.GREY)
        entry_num_buy_grid_lines.insert(
            tkinter.END, config.get_Num_Buy_Grid_Lines())
        entry_num_buy_grid_lines.grid(row=0, column=1)
        self.configuration_entries['num_buy_grid_lines'] = entry_num_buy_grid_lines

        entry_num_sell_grid_lines = tkinter.Entry(
            config_frame_right, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, highlightbackground=Colours.GREY)
        entry_num_sell_grid_lines.insert(
            tkinter.END, config.get_Num_Sell_Grid_Lines())
        entry_num_sell_grid_lines.grid(row=1, column=1)
        self.configuration_entries['num_sell_grid_lines'] = entry_num_sell_grid_lines

        entry_grid_size = tkinter.Entry(
            config_frame_right, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, highlightbackground=Colours.GREY)
        entry_grid_size.insert(tkinter.END, config.get_Grid_Size())
        entry_grid_size.grid(row=2, column=1)
        self.configuration_entries['grid_size'] = entry_grid_size

    def create_buttons(self):
        buttons_frame = tkinter.Frame(master=self)
        buttons_frame.configure(bg=Colours.BACKGROUND)
        buttons_frame.grid(row=8, column=2)

        if platform.system() == 'Darwin':
            button_start_bot = tkmacosx.Button(
                buttons_frame, text="    Start Bot    ", width=350, font=('Calibri', 15), fg='white', bg=Colours.GREEN, borderless=True, command=self.start_bot, focusthickness=0)
            button_stop_bot = tkmacosx.Button(
                buttons_frame, text="    Stop Bot     ", width=350, font=('Calibri', 15), fg='white', bg=Colours.RED, borderless=True, command=self.stop_bot, focusthickness=0)
        else:
            pass  # tkinter buttons

        button_start_bot.grid(row=0, column=0)
        button_stop_bot.grid(row=2, column=0)

        empty_label = tkinter.Label(
            buttons_frame, bg=Colours.BACKGROUND, font=('Calibri', 6))
        empty_label.grid(row=1, column=0)

    def start_bot(self):
        if self.bot is None:

            # save entries content
            if self.save_configuration_params() == False:
                return

            print("\n_____________________ START BOT _____________________\n")

            # clear chart
            self.x_vals = []
            self.y_vals = []

            if self.mode == 'demo':
                try:
                    self.bot = multiprocessing.Process(
                        target=Demo_Bot)
                    self.bot.start()
                except Exception as e:  # error in multiprocessing
                    print(e)
                    self.bot = None

            elif self.mode == 'binance':
                try:
                    self.bot = multiprocessing.Process(
                        target=Grid_Bot)
                    self.bot.start()
                except Exception as e:  # error in multiprocessing
                    print(e)
                    self.bot = None
        else:  # bot already running
            pass

    def stop_bot(self):
        if self.bot is None:
            pass
        else:
            print("\n_____________________ STOP BOT ______________________\n")

            # close binance open limit orders
            if self.mode == 'binance':
                try:
                    exchange = ccxt.binance(
                        {'apiKey': config.get_API_key(), 'secret': config.get_secret_key()})
                    exchange.check_required_credentials()
                    exchange.cancel_all_orders(config.get_Symbol())
                except ccxt.AuthenticationError:  # API key or secret key empty, bot was not running because of a login error
                    pass
                except Exception as e:  # bot was running and was stopped but it was not possible to close open orders
                    print(
                        "Binance ERROR, unable to access account and close open orders")
                    print(e)

            self.bot.terminate()
            self.bot = None
            clear_open_orders_json_files()

    def save_configuration_params(self):
        try:
            config.set_Symbol(self.configuration_entries['symbol'].get())
        except ValueError:
            print("Invalid symbol")
            return False
        try:
            config.set_Position_Size(
                self.configuration_entries['position_size'].get())
            config.set_Check_Frequency(
                self.configuration_entries['check_frequency'].get())
            config.set_Num_Buy_Grid_Lines(
                self.configuration_entries['num_buy_grid_lines'].get())
            config.set_Num_Sell_Grid_Lines(
                self.configuration_entries['num_sell_grid_lines'].get())
            config.set_Grid_Size(self.configuration_entries['grid_size'].get())
        except ValueError as error:
            print("Invalid configuration parameters")
            print(error)
            return False
        config.set_API_key(self.configuration_entries['API_key'].get())
        config.set_secret_key(self.configuration_entries['secret_key'].get())
        return True

    def create_label_price(self):

        price_frame = tkinter.Frame(master=self)
        price_frame.place(x=800, y=30)

        label_symbol = tkinter.Label(master=price_frame, text=f"{config.get_Symbol()}   ", font=(
            'calibri', 35, 'bold'), fg=Colours.LIGHT_GREY, bg=Colours.BACKGROUND)
        label_symbol.grid(row=0, column=0)

        last_price = self.current_price

        def get_current_price():
            try:
                nonlocal last_price
                if self.current_price >= last_price:
                    label_price.config(fg=Colours.GREEN)
                else:
                    label_price.config(fg=Colours.RED)

                label_price.config(text=self.current_price)
                last_price = self.current_price
                label_price.after(1000, get_current_price)
            except Exception as e:
                print(e)
                get_current_price()

        label_price = tkinter.Label(master=price_frame, font=(
            'calibri', 35, 'bold'), fg=Colours.LIGHT_GREY, bg=Colours.BACKGROUND)
        label_price.grid(row=0, column=1)
        get_current_price()

    def create_frame_closed_orders(self):
        closed_orders_frame = tkinter.Frame(master=self, bg=Colours.BACKGROUND)
        closed_orders_frame.grid(row=3, column=2)

        closed_orders_label = tkinter.Label(master=closed_orders_frame, text="Closed Orders",
                                            bg=Colours.BACKGROUND, fg=Colours.LIGHT_GREY, width=34)
        closed_orders_label.grid(row=0, column=0)

        closed_orders_box = tkinter.Frame(
            master=closed_orders_frame, bg='black', highlightbackground=Colours.LIGHT_GREY, highlightthickness=1)
        closed_orders_box.grid(row=1, column=0, columnspan=2)

        def closed_order_chronology():
            try:
                closed_orders = read_json_closed_orders()

                if len(closed_orders) == 0:
                    label_order_1.config(text="")
                    label_order_2.config(text="")
                    label_order_3.config(text="")
                    label_order_4.config(text="")
                    label_order_5.config(text="")
                    label_order_6.config(text="")
                    label_order_7.config(text="")
                    label_order_8.config(text="")
                    label_order_9.config(text="")
                    label_order_10.config(text="")

                if len(closed_orders) >= 1:
                    closed_order_1 = closed_orders[-1]
                    label_order_1.config(text=f"  {closed_order_1['price']}")
                    if closed_order_1['side'] == 'buy':
                        label_order_1.config(fg=Colours.RED)
                    else:
                        label_order_1.config(fg=Colours.GREEN)

                if len(closed_orders) >= 2:
                    closed_order_2 = closed_orders[-2]
                    label_order_2.config(text=f"  {closed_order_2['price']}")
                    if closed_order_2['side'] == 'buy':
                        label_order_2.config(fg=Colours.RED)
                    else:
                        label_order_2.config(fg=Colours.GREEN)

                if len(closed_orders) >= 3:
                    closed_order_3 = closed_orders[-3]
                    label_order_3.config(text=f"  {closed_order_3['price']}")
                    if closed_order_3['side'] == 'buy':
                        label_order_3.config(fg=Colours.RED)
                    else:
                        label_order_3.config(fg=Colours.GREEN)

                if len(closed_orders) >= 4:
                    closed_order_4 = closed_orders[-4]
                    label_order_4.config(text=f"  {closed_order_4['price']}")
                    if closed_order_4['side'] == 'buy':
                        label_order_4.config(fg=Colours.RED)
                    else:
                        label_order_4.config(fg=Colours.GREEN)

                if len(closed_orders) >= 5:
                    closed_order_5 = closed_orders[-5]
                    label_order_5.config(text=f"  {closed_order_5['price']}")
                    if closed_order_5['side'] == 'buy':
                        label_order_5.config(fg=Colours.RED)
                    else:
                        label_order_5.config(fg=Colours.GREEN)

                if len(closed_orders) >= 6:
                    closed_order_6 = closed_orders[-6]
                    label_order_6.config(text=f"  {closed_order_6['price']}")
                    if closed_order_6['side'] == 'buy':
                        label_order_6.config(fg=Colours.RED)
                    else:
                        label_order_6.config(fg=Colours.GREEN)

                if len(closed_orders) >= 7:
                    closed_order_7 = closed_orders[-7]
                    label_order_7.config(text=f"  {closed_order_7['price']}")
                    if closed_order_7['side'] == 'buy':
                        label_order_7.config(fg=Colours.RED)
                    else:
                        label_order_7.config(fg=Colours.GREEN)

                if len(closed_orders) >= 8:
                    closed_order_8 = closed_orders[-8]
                    label_order_8.config(text=f"  {closed_order_8['price']}")
                    if closed_order_8['side'] == 'buy':
                        label_order_8.config(fg=Colours.RED)
                    else:
                        label_order_8.config(fg=Colours.GREEN)

                if len(closed_orders) >= 9:
                    closed_order_9 = closed_orders[-9]
                    label_order_9.config(text=f"  {closed_order_9['price']}")
                    if closed_order_9['side'] == 'buy':
                        label_order_9.config(fg=Colours.RED)
                    else:
                        label_order_9.config(fg=Colours.GREEN)

                if len(closed_orders) >= 10:
                    closed_order_10 = closed_orders[-10]
                    label_order_10.config(text=f"  {closed_order_10['price']}")
                    if closed_order_10['side'] == 'buy':
                        label_order_10.config(fg=Colours.RED)
                    else:
                        label_order_10.config(fg=Colours.GREEN)

                closed_orders_box.after(1000, closed_order_chronology)
            except Exception as e:
                print(e)
                closed_order_chronology()

        label_order_1 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_1.grid(row=0, column=0)

        label_order_2 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_2.grid(row=1, column=0)

        label_order_3 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_3.grid(row=2, column=0)

        label_order_4 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_4.grid(row=3, column=0)

        label_order_5 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_5.grid(row=4, column=0)

        label_order_6 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_6.grid(row=0, column=1)

        label_order_7 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_7.grid(row=1, column=1)

        label_order_8 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_8.grid(row=2, column=1)

        label_order_9 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_9.grid(row=3, column=1)

        label_order_10 = tkinter.Label(
            master=closed_orders_box, bg='black', width=16, font=(
                'calibri', 15), anchor='w')
        label_order_10.grid(row=4, column=1)

        closed_order_chronology()

    def create_frame_account_infos(self):

        balance_infos_frame = tkinter.Frame(master=self, bg=Colours.BACKGROUND)
        balance_infos_frame.grid(row=4, column=2)

        grid_bot_label = tkinter.Label(
            master=balance_infos_frame, text="Grid Bot", fg=Colours.LIGHT_GREY, bg=Colours.BACKGROUND)
        grid_bot_label.grid(row=0, column=0)

        balance_infos_box = tkinter.Frame(
            master=balance_infos_frame, width=35, bg=Colours.GREY, highlightbackground=Colours.LIGHT_GREY, highlightthickness=1)
        balance_infos_box.grid(row=1, column=0)

        crypto_currency = config.get_Symbol().split('/')[0]
        currency = config.get_Symbol().split('/')[1]

        def update_account_infos():

            try:
                nonlocal currency, crypto_currency
                crypto_currency = config.get_Symbol().split('/')[0]
                currency = config.get_Symbol().split('/')[1]

                account_infos = read_json_account_infos()
                currency_balance_label.config(
                    text=f"{currency}:\t\t\t{round(account_infos['curr_balance'],5)}")
                crypto_currency_balance_label.config(
                    text=f"{crypto_currency}:\t\t\t{round(account_infos['cryptocurr_balance'],5)}")
                total_investment_label.config(
                    text=f"Total Investment:\t\t{round(account_infos['total_investment'],5)}")
                total_profit_label.config(
                    text=f"Total Profit:\t\t{round(account_infos['total_profit'],5)}")

                balance_infos_box.after(1000, update_account_infos)
            except Exception as e:
                print(e)
                update_account_infos()

        currency_balance_label = tkinter.Label(
            master=balance_infos_box, fg=Colours.LIGHT_GREY, bg=Colours.GREY, text=f"{currency} balance: ", anchor='w', width=35, padx=5, pady=3)

        crypto_currency_balance_label = tkinter.Label(
            master=balance_infos_box, fg=Colours.LIGHT_GREY, bg=Colours.GREY, text=f"{crypto_currency} balance: ", anchor='w', width=35, padx=5, pady=3)

        total_investment_label = tkinter.Label(
            master=balance_infos_box, fg=Colours.LIGHT_GREY, bg=Colours.GREY, text=f"Total Investment: ", anchor='w', width=35, padx=5, pady=3)

        total_profit_label = tkinter.Label(
            master=balance_infos_box, fg=Colours.LIGHT_GREY, bg=Colours.GREY, text="Total Profit: ", anchor='w', width=35, padx=5, pady=3)

        currency_balance_label.grid(row=0, column=0)
        crypto_currency_balance_label.grid(row=1, column=0)
        total_investment_label.grid(row=2, column=0)
        total_profit_label.grid(row=3, column=0)

        update_account_infos()

    def create_frame_login(self):
        login_frame = tkinter.Frame(master=self, bg=Colours.GREY)
        login_frame.grid(row=6, column=2)

        API_key_label = tkinter.Label(
            master=login_frame, text="API Key", fg=Colours.LIGHT_GREY, width=10, bg=Colours.GREY)
        API_key_entry = tkinter.Entry(
            master=login_frame, fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, width=25, highlightbackground=Colours.GREY)
        API_key_entry.insert(tkinter.END, config.get_API_key())
        self.configuration_entries['API_key'] = API_key_entry

        secret_key_label = tkinter.Label(
            master=login_frame, text="Secret Key", fg=Colours.LIGHT_GREY, width=10, bg=Colours.GREY)
        secret_key_entry = tkinter.Entry(
            master=login_frame, show="*", fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, width=25, highlightbackground=Colours.GREY)
        secret_key_entry.insert(tkinter.END, config.get_secret_key())
        self.configuration_entries['secret_key'] = secret_key_entry

        API_key_label.grid(row=0, column=0)
        API_key_entry.grid(row=0, column=1)

        secret_key_label.grid(row=1, column=0)
        secret_key_entry.grid(row=1, column=1)

    def create_mode_switch_buttons(self):

        switch_mode_frame = tkinter.Frame(
            master=self, width=35, bg=Colours.BACKGROUND)
        switch_mode_frame.grid(row=7, column=2)

        def switch_to_demo_mode():

            if self.mode == 'binance':

                print("Switch to Demo Mode")
                self.mode = 'demo'

                demo_mode_button.config(font=('Calibri', 27, 'bold'))
                API_mode_button.config(font=('Calibri', 20, 'bold'))
            self.update()

        def switch_to_API_mode():
            if self.mode == 'demo':

                print("Switch to API Mode")
                self.mode = 'binance'

                demo_mode_button.config(font=('Calibri', 20, 'bold'))
                API_mode_button.config(font=('Calibri', 27, 'bold'))
            self.update()

        if platform.system() == 'Darwin':
            demo_mode_button = tkmacosx.Button(master=switch_mode_frame, command=switch_to_demo_mode, text=' Demo Mode ', font=(
                'Calibri', 27, 'bold'), fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, borderless=True, focuscolor=Colours.BACKGROUND, focusthickness=1)
            API_mode_button = tkmacosx.Button(master=switch_mode_frame, command=switch_to_API_mode, text='  API Mode ', font=(
                'Calibri', 20, 'bold'), fg=Colours.LIGHT_GREY, bg=Colours.DARK_GREY, borderless=True, focuscolor=Colours.BACKGROUND, focusthickness=1)

        else:
            demo_mode_button = tkinter.Button(
                master=switch_mode_frame, command=switch_to_demo_mode, text='  Demo Mode  ', font=('Calibri', 27, 'bold'), fg=Colours.GREEN)

            API_mode_button = tkinter.Button(
                master=switch_mode_frame, command=switch_to_API_mode, text='  API Mode  ', font=('Calibri', 20, 'bold'), fg=Colours.LIGHT_GREY)

        demo_mode_button.pack(side=tkinter.LEFT)
        API_mode_button.pack(side=tkinter.RIGHT)


@ staticmethod
def read_json_buy_lines(filename="buy_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@ staticmethod
def read_json_sell_lines(filename="sell_lines.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@ staticmethod
def read_json_closed_orders(filename="closed_orders.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@ staticmethod
def read_json_account_infos(filename="account_infos.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@ staticmethod
def clear_open_orders_json_files():
    empty_list = {}
    with open("buy_lines.json", 'w') as f:
        json.dump(empty_list, f, indent=4)
    with open("sell_lines.json", 'w') as f:
        json.dump(empty_list, f, indent=4)


@staticmethod
def clear_closed_orders_json_file():
    empty_list = {}
    with open("closed_orders.json", 'w') as f:
        json.dump(empty_list, f, indent=4)


@staticmethod
def reset_account_infos_json_file():
    initial_infos = {
        "curr_balance": 0.0,
        "cryptocurr_balance": 0.0,
        "total_investment": 0.0,
        "total_profit": 0.0
    }
    with open("account_infos.json", 'w') as f:
        json.dump(initial_infos, f, indent=4)


@staticmethod
# return the current price of the symbol passed as parameter
def get_crypto_price(exchange, symbol):
    return float(exchange.fetch_ticker(symbol)['last'])
