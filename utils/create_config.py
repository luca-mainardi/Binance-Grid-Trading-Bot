import json

@staticmethod
def create_config():
    try:
        with open("config.json", 'r') as f:
            return json.load(f)
    except Exception:
        config = {
            "API_KEY":"",
            "SECRET_KEY":"",
            "SYMBOL":"BTC/BUSD",
            "POSITION_SIZE":0.001,
            "NUM_BUY_GRID_LINES":5,
            "NUM_SELL_GRID_LINES":5,
            "GRID_SIZE":10,
            "CHECK_FREQUENCY":2
            }
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=4)