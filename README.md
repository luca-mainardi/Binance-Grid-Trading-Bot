# Binance-Grid-Trading-Bot

> A grid trading bot that uses the Binance API. It also provides a demo mode that operates on a demo account.

## The Grid Bot Strategy

The Grid strategy is one of the simpliest strategies in crypto trading. It works with postponed limit buy and sell orders in predefined price intervals.
You choose the price range between each order and the number of buy and sell orders; in this way a grid of orders is created that operates within a price range.
According to this strategy, the bot keep generating profits from any market movement, buying at low prices and selling at high prices.
All the grid lines are interchangeable, for every completed buy order, the bot will create a new sell order above the executed price, and vice versa.

## Tips

- The bot may not be profitable during bearish market phases, so it is necessary to understand when it is appropriate to create or stop the bot.
- Usually the strategy is implemented on cryptocurrency/stablecoin pairs. It is also possible to use it on cryptocurrency pairs but due to their high
  volatility the bot may not be profitable.
- Currently binance offers some trading pairs with zero commissions (e.g. BUSD pairs),so it is highly recommended to have the bot operate on these
  pairs to increase profits. On the other hand, if you decide to use trading pairs with commissions, you should pay close attention to the bot's parameters,
  as grids with orders that are too close or too small can almost totally reduce profits and even lead to losses.

## Binance Setup

- Create a [Binance account](https://www.binance.com/en/activity/referral-entry/CPA?fromActivityPage=true&ref=CPA_00CHWETX1U).
- Enable Two-factor Authentication.
- Create a new API key (copy the secret key because you will no longer be able to see it).

## Demo Mode

The demo mode operates on a dummy account with 10000 (in $ or other quote currency ) inside, which is reset every time you start the program.
The demo mode does not consider commission-free trading pairs and applies a 0.2% commission to all of them, therefore earnings obtained with
the demo mode may differ from the real ones.

## Bot

The bot after buying an initial amount of cryptocurrency needed to execute future sell orders and after creating the order grid, periodically
checks each order (the frequency is chosen by the user) to check whether it has been executed. Because of this, there may be a delay between the
instant the order is executed and the instant a new order is created to reform the grid. For the same reason, the GUI may also show delayed execution and creation of orders.

## Warnings

- When the bot is stopped all open orders are cancelled but the bought cryptocurrencies are not sold. If you want to take profit you must sell cryptocurrencies through Binance.
- A program exit before stopping the bot or an unexpected termination does not effect the cancellation of open orders. it is therefore necessary to close them trough Binance.
