import json

# Save data in config.json

def save_data(data):
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)


# Load data from config.json

def load_data():
    try:
        with open("config.json", "r") as f:
            data = json.load(f)
            return data
    except:
        return{}


"""
Methods for reading and writing config.json elements
"""

# _________________________________ GETTERS ________________________________

def get_Symbol():
    config = load_data()
    return config["SYMBOL"]


def get_Position_Size():
    config = load_data()
    return float(config["POSITION_SIZE"])


def get_Num_Buy_Grid_Lines():
    config = load_data()
    return int(config["NUM_BUY_GRID_LINES"])


def get_Num_Sell_Grid_Lines():
    config = load_data()
    return int(config["NUM_SELL_GRID_LINES"])


def get_Grid_Size():
    config = load_data()
    return float(config["GRID_SIZE"])


def get_Check_Frequency():
    config = load_data()
    return float(config["CHECK_FREQUENCY"])


def get_API_key():
    config = load_data()
    return config["API_KEY"]


def get_secret_key():
    config = load_data()
    return config["SECRET_KEY"]


# _________________________________ SETTERS ________________________________

def set_Symbol(new_symbol):
    # Check if symbol is supported
    valid_symbol = False
    with open("supported_symbols.txt") as file:
        for line in file:
            if line.rstrip() == new_symbol:
                valid_symbol = True

    if valid_symbol:
        config = load_data()
        config["SYMBOL"] = new_symbol
        save_data(config)
    else:
        raise ValueError


def set_Position_Size(new_position_size):
    # Throws ValueError if argument is not convertible to float
    float(new_position_size)

    config = load_data()
    config["POSITION_SIZE"] = new_position_size
    save_data(config)


def set_Num_Buy_Grid_Lines(new_num_buy_grid_lines):
    if new_num_buy_grid_lines.isdigit() == False:
        raise ValueError("N. of orders must be an integer")

    config = load_data()
    config["NUM_BUY_GRID_LINES"] = new_num_buy_grid_lines
    save_data(config)


def set_Num_Sell_Grid_Lines(new_num_sell_grid_lines):
    if new_num_sell_grid_lines.isdigit() == False:
        raise ValueError("N. of orders must be an integer")

    config = load_data()
    config["NUM_SELL_GRID_LINES"] = new_num_sell_grid_lines
    save_data(config)


def set_Grid_Size(new_Grid_Size):
    # Throws ValueError if argument is not convertible to float
    float(new_Grid_Size)

    config = load_data()
    config["GRID_SIZE"] = new_Grid_Size
    save_data(config)


def set_Check_Frequency(new_Check_Frequency):
    # Throws ValueError if argument is not convertible to float
    float(new_Check_Frequency)

    config = load_data()
    config["CHECK_FREQUENCY"] = new_Check_Frequency
    save_data(config)


def set_API_key(new_API_key):
    config = load_data()
    config["API_KEY"] = new_API_key
    save_data(config)


def set_secret_key(new_secret_key):
    config = load_data()
    config["SECRET_KEY"] = new_secret_key
    save_data(config)
