import json


# _____________________ Methods for writing to json files _____________________

@staticmethod
def write_json_buy_orders(data, filename="buy_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@staticmethod
def write_json_sell_orders(data, filename="sell_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@staticmethod
def write_json_closed_orders(data, filename="closed_orders.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


@staticmethod
def write_json_account_infos(data, filename="account_infos.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
