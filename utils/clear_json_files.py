import json


# _______________ Methods for resetting json files ____________________

@ staticmethod
def clear_open_orders_json_files():
    empty_list = {}
    with open("buy_orders.json", 'w') as f:
        json.dump(empty_list, f, indent=4)
    with open("sell_orders.json", 'w') as f:
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
