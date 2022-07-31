
from itertools import count
import ccxt
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from datetime import datetime

exchange = ccxt.binance({})

cryptocurr = input("Select Cryptocurrency: ")
curr = input("Select Currency: ")
grid_size = int(input("Select grid size: "))
num_grid_lines = int(input(("Select number of grid lines: ")))


def get_crypto_price(cryptocurrency, currency):
    return float(exchange.fetch_ticker(f"{cryptocurrency}/{currency}")['last'])


plt.style.use('seaborn')
#plt.autoscale(enable=True, tight=True)

x_vals = []
y_vals = []

# # set grid
current_price = get_crypto_price(cryptocurr, curr)
buy_lines = []
sell_lines = []

for i in range(int(num_grid_lines)):
    #plt.axhline(current_price + grid_size*(i+1), color='green', linewidth=0.5)
    #plt.axhline(current_price - grid_size*(i+1), color='red', linewidth=0.5)
    buy_lines.append(current_price - grid_size*(i+1))
    sell_lines.append(current_price + grid_size*(i+1))

index = count()


def animate(i):
    x_vals.append(datetime.now())
    y_vals.append(get_crypto_price(cryptocurr, curr))

    plt.cla()

    for line in buy_lines:
        plt.axhline(line, color='red', linewidth=0.5)
    for line in sell_lines:
        plt.axhline(line, color='green', linewidth=0.5)

    plt.plot(x_vals, y_vals, color='black')

    #plt.title(cryptocurr + " Price Live Plotting")
   # plt.gcf().canvas.set_window_title("Live Plotting Cryptocurrency")

    # plt.xlabel("Date")
    # plt.ylabel("Price")

    # plt.plot_date(x_vals, y_vals, linestyle="solid",
    #            ms=0, color='black', linewidth=0.5)

    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.show()