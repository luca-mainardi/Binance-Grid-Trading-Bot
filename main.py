from tkinter import font
from tkinter import *
import ccxt
from DemoBot import start_demo_bot, Demo_Account
import config

from GUI import GUI
import DemoBot
import multiprocessing


def main():

    gui = GUI()
    gui.mainloop()


if __name__ == '__main__':
    main()
