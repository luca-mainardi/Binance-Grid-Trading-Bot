
import json

# _______________ Methods for loading json files ____________________


@ staticmethod
def read_json_buy_orders(filename="buy_orders.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


@ staticmethod
def read_json_sell_orders(filename="sell_orders.json"):
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
