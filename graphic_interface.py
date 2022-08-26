import ccxt
import platform
import multiprocessing
from datetime import datetime

import tkmacosx
import tkinter

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)


from utils.get_crypto_price import *
from utils.read_json_files import *
from utils.clear_json_files import *
from utils.create_config import create_config

from grid_bot import GridBot
from demo_bot import DemoBot

import config
import color_palette


"""
Graphic User Interface that allows you to view the price chart, 
configure bot parameters, start or stop the bot, and view some
information about the bot and binance account balance 
"""


class GUI(tkinter.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.current_price = 0

        self.bot = None  # Process in which the bot is executed
        self.mode = "demo"
        # Lists of coordinates needed to draw the price chart
        self.x_vals = []
        self.y_vals = []
        # List of entries containing configuration parameters
        self.configuration_entries = {}

        # Reset all json files
        clear_open_orders_json_files()
        clear_closed_orders_json_file()
        reset_account_infos_json_file()

        # Create config.json if it does not exist
        create_config()

        self.initialize_window()
        self.create_configuration_entries()
        self.create_buttons()
        self.create_buttons_switch_mode()
        self.create_label_price()
        self.create_frame_closed_orders()
        self.create_frame_account_infos()
        self.create_frame_login()
        self.create_chart()

    def initialize_window(self):

        self.geometry("1200x720")
        self.wm_title("Grid Bot")
        self.configure(bg=color_palette.BACKGROUND)
        self.resizable(False, False)

    def create_chart(self):
        plt.style.use("seaborn-deep")

        exchange = ccxt.binance()

        fig = Figure(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor(color_palette.BACKGROUND)

        # Chart configuration
        ax = fig.add_subplot(111)
        ax.set_facecolor("black")
        ax.spines["top"].set_color(color_palette.LIGHT_GREY)
        ax.spines["bottom"].set_color(color_palette.LIGHT_GREY)
        ax.spines["left"].set_color(color_palette.LIGHT_GREY)
        ax.spines["right"].set_color(color_palette.LIGHT_GREY)

        ax.tick_params(axis="x", colors=color_palette.LIGHT_GREY)
        ax.tick_params(axis="y", colors=color_palette.LIGHT_GREY)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=0, rowspan=8, column=0, columnspan=2)

        def animate(i):
            try:
                self.current_price = get_crypto_price(
                    exchange, config.get_Symbol())

                buy_orders = read_json_buy_orders()
                sell_orders = read_json_sell_orders()

                self.x_vals.append(datetime.now())
                self.y_vals.append(self.current_price)

                ax.clear()

                # Draw currently open orders
                for order in buy_orders:
                    if order["status"] == "open":
                        ax.axhline(
                            order["price"], color=color_palette.RED, linewidth=0.5)
                for order in sell_orders:
                    if order["status"] == "open":
                        ax.axhline(
                            order["price"], color=color_palette.GREEN, linewidth=0.5)

                # Draw price line
                ax.plot(self.x_vals, self.y_vals,
                        color=color_palette.LIGHT_GREY)
            except Exception as e:
                print(e)
                animate(i=None)  # Try to draw chart again

        ani = FuncAnimation(
            fig, animate, interval=config.get_Check_Frequency())
        self.update()

    def create_configuration_entries(self):

        # _______________ Left configuration frame _______________

        config_frame_left = tkinter.Frame(master=self, bg=color_palette.GREY)
        config_frame_left.grid(row=8, column=0)

        label_symbol = tkinter.Label(
            config_frame_left, text="Symbol", fg=color_palette.LIGHT_GREY, bg=color_palette.GREY)
        label_symbol.grid(row=0, column=0)

        label_position_size = tkinter.Label(
            config_frame_left, text="Position Size", fg=color_palette.LIGHT_GREY, bg=color_palette.GREY)
        label_position_size.grid(row=1, column=0)

        label_check_frequency = tkinter.Label(
            config_frame_left, text="Check Frequency", fg=color_palette.LIGHT_GREY, bg=color_palette.GREY)
        label_check_frequency.grid(row=2, column=0)

        entry_symbol = tkinter.Entry(
            config_frame_left, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, highlightbackground=color_palette.GREY)
        entry_symbol.insert(tkinter.END, config.get_Symbol())
        entry_symbol.grid(row=0, column=1)
        self.configuration_entries["symbol"] = entry_symbol

        entry_position_size = tkinter.Entry(
            config_frame_left, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, highlightbackground=color_palette.GREY)
        entry_position_size.insert(tkinter.END, config.get_Position_Size())
        entry_position_size.grid(row=1, column=1)
        self.configuration_entries["position_size"] = entry_position_size

        entry_check_frequency = tkinter.Entry(
            config_frame_left, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, highlightbackground=color_palette.GREY)
        entry_check_frequency.insert(tkinter.END, config.get_Check_Frequency())
        entry_check_frequency.grid(row=2, column=1)
        self.configuration_entries["check_frequency"] = entry_check_frequency

        # _______________ Right configuration frame _______________

        config_frame_right = tkinter.Frame(master=self, bg=color_palette.GREY)
        config_frame_right.grid(row=8, column=1)

        label_num_buy_grid_lines = tkinter.Label(
            config_frame_right, text="N. buy orders", fg=color_palette.LIGHT_GREY, bg=color_palette.GREY)
        label_num_buy_grid_lines.grid(row=0, column=0)

        label_num_sell_grid_lines = tkinter.Label(
            config_frame_right, text="N. sell orders Size", fg=color_palette.LIGHT_GREY, bg=color_palette.GREY)
        label_num_sell_grid_lines.grid(row=1, column=0)

        label_grid_size = tkinter.Label(
            config_frame_right, text="Grid size", fg=color_palette.LIGHT_GREY, bg=color_palette.GREY)
        label_grid_size.grid(row=2, column=0)

        entry_num_buy_grid_lines = tkinter.Entry(
            config_frame_right, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, highlightbackground=color_palette.GREY)
        entry_num_buy_grid_lines.insert(
            tkinter.END, config.get_Num_Buy_Grid_Lines())
        entry_num_buy_grid_lines.grid(row=0, column=1)
        self.configuration_entries["num_buy_grid_lines"] = entry_num_buy_grid_lines

        entry_num_sell_grid_lines = tkinter.Entry(
            config_frame_right, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, highlightbackground=color_palette.GREY)
        entry_num_sell_grid_lines.insert(
            tkinter.END, config.get_Num_Sell_Grid_Lines())
        entry_num_sell_grid_lines.grid(row=1, column=1)
        self.configuration_entries["num_sell_grid_lines"] = entry_num_sell_grid_lines

        entry_grid_size = tkinter.Entry(
            config_frame_right, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, highlightbackground=color_palette.GREY)
        entry_grid_size.insert(tkinter.END, config.get_Grid_Size())
        entry_grid_size.grid(row=2, column=1)
        self.configuration_entries["grid_size"] = entry_grid_size

    def create_buttons(self):
        buttons_frame = tkinter.Frame(master=self)
        buttons_frame.configure(bg=color_palette.BACKGROUND)
        buttons_frame.grid(row=8, column=2)

        # Buttons for macOS
        if platform.system() == "Darwin":
            button_start_bot = tkmacosx.Button(
                buttons_frame, text="    Start Bot    ", width=350, font=("Calibri", 15), fg="white", bg=color_palette.GREEN, borderless=True, command=self.start_bot, focusthickness=0)
            button_stop_bot = tkmacosx.Button(
                buttons_frame, text="    Stop Bot     ", width=350, font=("Calibri", 15), fg="white", bg=color_palette.RED, borderless=True, command=self.stop_bot, focusthickness=0)
        else:  # Other OS
            button_start_bot = tkinter.Button(
                buttons_frame, text="    Start Bot    ", width=35, height=1, font=("Calibri", 15), fg="white", bg=color_palette.GREEN, command=self.start_bot)
            button_stop_bot = tkinter.Button(
                buttons_frame, text="    Stop Bot     ", width=35, height=1, font=("Calibri", 15), fg="white", bg=color_palette.RED, command=self.stop_bot)

        button_start_bot.grid(row=0, column=0)
        button_stop_bot.grid(row=2, column=0)

        empty_label = tkinter.Label(
            buttons_frame, bg=color_palette.BACKGROUND, font=("Calibri", 6))
        empty_label.grid(row=1, column=0)

    def start_bot(self):
        if self.bot is None:

            # Bot starts only if configuration parameters are valid
            if self.save_configuration_params() == False:
                return

            print("\n_____________________ START BOT _____________________\n")

            # Clear chart
            self.x_vals = []
            self.y_vals = []

            if self.mode == "demo":
                try:
                    self.bot = multiprocessing.Process(
                        target=DemoBot)
                    self.bot.start()
                except Exception as e:  # Error in multiprocessing
                    print(e)
                    self.bot = None

            elif self.mode == "binance":
                try:
                    self.bot = multiprocessing.Process(
                        target=GridBot)
                    self.bot.start()
                except Exception as e:  # Error in multiprocessing
                    print(e)
                    self.bot = None
        else:  # Bot already running
            pass

    def stop_bot(self):
        if self.bot is None:
            pass
        else:
            print("\n_____________________ STOP BOT ______________________\n")

            # Close binance open limit orders
            if self.mode == "binance":
                try:
                    exchange = ccxt.binance(
                        {"apiKey": config.get_API_key(), "secret": config.get_secret_key()})
                    exchange.check_required_credentials()

                    open_orders = exchange.fetch_open_orders(
                        config.get_Symbol())

                    if len(open_orders) != 0:
                        exchange.cancel_all_orders(config.get_Symbol())

                except ccxt.AuthenticationError:  # API key or secret key empty, bot was not running because of a login error
                    pass
                except Exception as e:  # Bot was running and was stopped but it was not possible to close open orders
                    print(
                        "Binance ERROR, unable to access account and close open orders")
                    print(e)

            self.bot.terminate()
            self.bot = None
            clear_open_orders_json_files()

    def save_configuration_params(self):
        # Check if symbol is valid
        try:
            config.set_Symbol(self.configuration_entries["symbol"].get())
        except ValueError:
            print("Invalid symbol")
            return False
        # Check if other parameters are valid
        try:
            config.set_Position_Size(
                self.configuration_entries["position_size"].get())
            config.set_Check_Frequency(
                self.configuration_entries["check_frequency"].get())
            config.set_Num_Buy_Grid_Lines(
                self.configuration_entries["num_buy_grid_lines"].get())
            config.set_Num_Sell_Grid_Lines(
                self.configuration_entries["num_sell_grid_lines"].get())
            config.set_Grid_Size(self.configuration_entries["grid_size"].get())
        except ValueError as error:
            print("Invalid configuration parameters")
            print(error)
            return False

        # Save API keys, Grid_Bot checks whether they are valid
        config.set_API_key(self.configuration_entries["API_key"].get())
        config.set_secret_key(self.configuration_entries["secret_key"].get())
        return True

    def create_label_price(self):

        price_frame = tkinter.Frame(master=self)
        price_frame.grid(row=0, column=2)

        label_symbol = tkinter.Label(master=price_frame, text=f"{config.get_Symbol()}   ", font=(
            "calibri", 30, "bold"), fg=color_palette.LIGHT_GREY, bg=color_palette.BACKGROUND)
        label_symbol.grid(row=0, column=0)

        last_price = self.current_price

        def update_label_price():
            try:
                # Update symbol
                label_symbol.config(text=f"{config.get_Symbol()}   ")

                # Update price
                nonlocal last_price
                if self.current_price >= last_price:
                    label_price.config(fg=color_palette.GREEN)
                else:
                    label_price.config(fg=color_palette.RED)

                label_price.config(text=round(self.current_price, 1))
                last_price = self.current_price
                # Refresh every second
                label_price.after(1000, update_label_price)
            except Exception as e:
                print(e)
                update_label_price()  #  Try again

        label_price = tkinter.Label(master=price_frame, font=(
            "calibri", 30, "bold"), fg=color_palette.LIGHT_GREY, bg=color_palette.BACKGROUND)
        label_price.grid(row=0, column=1)

        update_label_price()

    def create_frame_closed_orders(self):
        closed_orders_frame = tkinter.Frame(
            master=self, bg=color_palette.BACKGROUND)
        closed_orders_frame.grid(row=1, column=2)

        closed_orders_label = tkinter.Label(master=closed_orders_frame, text="Closed Orders",
                                            bg=color_palette.BACKGROUND, fg=color_palette.LIGHT_GREY, width=34)
        closed_orders_label.grid(row=0, column=0)

        # Frame with closed order chronology
        closed_orders_box = tkinter.Frame(
            master=closed_orders_frame, bg="black", highlightbackground=color_palette.LIGHT_GREY, highlightthickness=1)
        closed_orders_box.grid(row=1, column=0, columnspan=2)

        def closed_order_chronology():
            try:
                closed_orders = read_json_closed_orders()

                # There are not closed orders
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
                    if closed_order_1["side"] == "buy":
                        label_order_1.config(fg=color_palette.RED)
                    else:
                        label_order_1.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 2:
                    closed_order_2 = closed_orders[-2]
                    label_order_2.config(text=f"  {closed_order_2['price']}")
                    if closed_order_2["side"] == "buy":
                        label_order_2.config(fg=color_palette.RED)
                    else:
                        label_order_2.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 3:
                    closed_order_3 = closed_orders[-3]
                    label_order_3.config(text=f"  {closed_order_3['price']}")
                    if closed_order_3["side"] == "buy":
                        label_order_3.config(fg=color_palette.RED)
                    else:
                        label_order_3.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 4:
                    closed_order_4 = closed_orders[-4]
                    label_order_4.config(text=f"  {closed_order_4['price']}")
                    if closed_order_4["side"] == "buy":
                        label_order_4.config(fg=color_palette.RED)
                    else:
                        label_order_4.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 5:
                    closed_order_5 = closed_orders[-5]
                    label_order_5.config(text=f"  {closed_order_5['price']}")
                    if closed_order_5["side"] == "buy":
                        label_order_5.config(fg=color_palette.RED)
                    else:
                        label_order_5.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 6:
                    closed_order_6 = closed_orders[-6]
                    label_order_6.config(text=f"  {closed_order_6['price']}")
                    if closed_order_6["side"] == "buy":
                        label_order_6.config(fg=color_palette.RED)
                    else:
                        label_order_6.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 7:
                    closed_order_7 = closed_orders[-7]
                    label_order_7.config(text=f"  {closed_order_7['price']}")
                    if closed_order_7["side"] == "buy":
                        label_order_7.config(fg=color_palette.RED)
                    else:
                        label_order_7.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 8:
                    closed_order_8 = closed_orders[-8]
                    label_order_8.config(text=f"  {closed_order_8['price']}")
                    if closed_order_8["side"] == "buy":
                        label_order_8.config(fg=color_palette.RED)
                    else:
                        label_order_8.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 9:
                    closed_order_9 = closed_orders[-9]
                    label_order_9.config(text=f"  {closed_order_9['price']}")
                    if closed_order_9["side"] == "buy":
                        label_order_9.config(fg=color_palette.RED)
                    else:
                        label_order_9.config(fg=color_palette.GREEN)

                if len(closed_orders) >= 10:
                    closed_order_10 = closed_orders[-10]
                    label_order_10.config(text=f"  {closed_order_10['price']}")
                    if closed_order_10["side"] == "buy":
                        label_order_10.config(fg=color_palette.RED)
                    else:
                        label_order_10.config(fg=color_palette.GREEN)

                # Refresh every second
                closed_orders_box.after(1000, closed_order_chronology)
            except Exception as e:
                print(e)
                closed_order_chronology()  # Try again

        label_order_1 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_1.grid(row=0, column=0)

        label_order_2 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_2.grid(row=1, column=0)

        label_order_3 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_3.grid(row=2, column=0)

        label_order_4 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_4.grid(row=3, column=0)

        label_order_5 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_5.grid(row=4, column=0)

        label_order_6 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_6.grid(row=0, column=1)

        label_order_7 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_7.grid(row=1, column=1)

        label_order_8 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_8.grid(row=2, column=1)

        label_order_9 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_9.grid(row=3, column=1)

        label_order_10 = tkinter.Label(
            master=closed_orders_box, bg="black", width=16, font=(
                "calibri", 15), anchor="w")
        label_order_10.grid(row=4, column=1)

        closed_order_chronology()

    def create_frame_account_infos(self):

        balance_infos_frame = tkinter.Frame(
            master=self, bg=color_palette.BACKGROUND, width=35)
        balance_infos_frame.grid(row=3, column=2)

        grid_bot_label = tkinter.Label(
            master=balance_infos_frame, text="Grid Bot", fg=color_palette.LIGHT_GREY, bg=color_palette.BACKGROUND)
        grid_bot_label.grid(row=0, column=0)

        balance_infos_box = tkinter.Frame(
            master=balance_infos_frame, width=35, bg=color_palette.GREY, highlightbackground=color_palette.LIGHT_GREY, highlightthickness=1)
        balance_infos_box.grid(row=1, column=0)

        crypto_currency = config.get_Symbol().split("/")[0]
        currency = config.get_Symbol().split("/")[1]

        def update_account_infos():
            try:
                nonlocal currency, crypto_currency
                crypto_currency = config.get_Symbol().split("/")[0]
                currency = config.get_Symbol().split("/")[1]

                account_infos = read_json_account_infos()
                currency_balance_label.config(
                    text=f"{currency}:\t\t\t{round(account_infos['curr_balance'],5)}")
                crypto_currency_balance_label.config(
                    text=f"{crypto_currency}:\t\t\t{round(account_infos['cryptocurr_balance'],5)}")
                total_investment_label.config(
                    text=f"Total Investment:\t\t{round(account_infos['total_investment'],5)}")
                total_profit_label.config(
                    text=f"Total Profit:\t\t{round(account_infos['total_profit'],5)}")

                # Refresh every second
                balance_infos_box.after(1000, update_account_infos)
            except Exception as e:
                print(e)
                update_account_infos()  # Try again

        currency_balance_label = tkinter.Label(
            master=balance_infos_box, fg=color_palette.LIGHT_GREY, bg=color_palette.GREY, text=f"{currency} balance: ", anchor="w", width=35, padx=5, pady=3)

        crypto_currency_balance_label = tkinter.Label(
            master=balance_infos_box, fg=color_palette.LIGHT_GREY, bg=color_palette.GREY, text=f"{crypto_currency} balance: ", anchor="w", width=35, padx=5, pady=3)

        total_investment_label = tkinter.Label(
            master=balance_infos_box, fg=color_palette.LIGHT_GREY, bg=color_palette.GREY, text=f"Total Investment: ", anchor="w", width=35, padx=5, pady=3)

        total_profit_label = tkinter.Label(
            master=balance_infos_box, fg=color_palette.LIGHT_GREY, bg=color_palette.GREY, text="Total Profit: ", anchor="w", width=35, padx=5, pady=3)

        currency_balance_label.grid(row=0, column=0)
        crypto_currency_balance_label.grid(row=1, column=0)
        total_investment_label.grid(row=2, column=0)
        total_profit_label.grid(row=3, column=0)

        update_account_infos()

    def create_frame_login(self):

        login_frame = tkinter.Frame(
            master=self, bg=color_palette.GREY, width=35)
        login_frame.grid(row=5, column=2)

        API_key_label = tkinter.Label(
            master=login_frame, text="API Key", fg=color_palette.LIGHT_GREY, width=10, bg=color_palette.GREY)
        API_key_entry = tkinter.Entry(
            master=login_frame, fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, width=25, highlightbackground=color_palette.GREY)
        API_key_entry.insert(tkinter.END, config.get_API_key())
        self.configuration_entries["API_key"] = API_key_entry

        secret_key_label = tkinter.Label(
            master=login_frame, text="Secret Key", fg=color_palette.LIGHT_GREY, width=10, bg=color_palette.GREY)
        secret_key_entry = tkinter.Entry(
            master=login_frame, show="*", fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, width=25, highlightbackground=color_palette.GREY)
        secret_key_entry.insert(tkinter.END, config.get_secret_key())
        self.configuration_entries["secret_key"] = secret_key_entry

        API_key_label.grid(row=0, column=0)
        API_key_entry.grid(row=0, column=1)

        secret_key_label.grid(row=1, column=0)
        secret_key_entry.grid(row=1, column=1)

    def create_buttons_switch_mode(self):

        switch_mode_frame = tkinter.Frame(
            master=self, width=35, bg=color_palette.BACKGROUND)
        switch_mode_frame.grid(row=6, column=2)

        def switch_to_demo_mode():
            if self.mode == "binance":

                print("Switch to Demo Mode")
                self.mode = "demo"

                demo_mode_button.config(font=("Calibri", 23, "bold"))
                API_mode_button.config(font=("Calibri", 18, "bold"))
            self.update()

        def switch_to_API_mode():
            if self.mode == "demo":

                print("Switch to API Mode")
                self.mode = "binance"

                demo_mode_button.config(font=("Calibri", 18, "bold"))
                API_mode_button.config(font=("Calibri", 23, "bold"))
            self.update()

        # Buttons for macOS
        if platform.system() == "Darwin":
            demo_mode_button = tkmacosx.Button(master=switch_mode_frame, command=switch_to_demo_mode, text=" Demo Mode ", font=(
                "Calibri", 23, "bold"), fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, borderless=True, focuscolor=color_palette.BACKGROUND, focusthickness=1)
            API_mode_button = tkmacosx.Button(master=switch_mode_frame, command=switch_to_API_mode, text="  API Mode ", font=(
                "Calibri", 18, "bold"), fg=color_palette.LIGHT_GREY, bg=color_palette.DARK_GREY, borderless=True, focuscolor=color_palette.BACKGROUND, focusthickness=1)

        else:  # Buttons for other OS
            demo_mode_button = tkinter.Button(
                master=switch_mode_frame, command=switch_to_demo_mode, text="  Demo Mode  ", font=("Calibri", 23, "bold"), fg=color_palette.LIGHT_GREY,
                bg=color_palette.DARK_GREY, height=1)

            API_mode_button = tkinter.Button(
                master=switch_mode_frame, command=switch_to_API_mode, text="  API Mode  ", font=("Calibri", 18, "bold"), fg=color_palette.LIGHT_GREY,
                bg=color_palette.DARK_GREY,  height=1)

        demo_mode_button.pack(side=tkinter.LEFT)
        API_mode_button.pack(side=tkinter.RIGHT)
