import ccxt
from DemoBot import start_demo_bot, Demo_Account, Order

from GUI import GUI


exchange = ccxt.binance()
account = Demo_Account(2000)


def main():

    # bot = Thread(target=start_demo_bot, args=(
    #     exchange, account))
    # bot.start()
    # start_gui(exchange)

    gui = GUI(exchange, account)
    gui.mainloop()


if __name__ == '__main__':
    main()
