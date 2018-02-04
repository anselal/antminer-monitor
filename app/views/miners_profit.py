import requests
import json
from enum import Enum
from miner_adapter import get_miner_instance, update_unit_and_value
from app.models import Miner, MinerModel

COST_KWH = 0.11

# Make data fetching abstract
# Remove MinerConfig

class Coin(Enum):
    Bitcoin = 1,
    BitcoinCash = 2,
    Dash = 3,
    Litecoin = 4

class MinerConfig(object):
    def __init__(self, model_name, coin, hashrate_value, hashrate_unit, watts):
        self.model_name = model_name
        self.coin_name = coin.name
        self.hashrate_value = hashrate_value
        self.hashrate_unit = hashrate_unit
        self.watts = watts

        id_url = 0
        if coin == Coin.Dash:
            id_url = 34
        elif coin == Coin.Bitcoin:
            id_url = 1
        elif coin == Coin.Litecoin:
            id_url = 4
        self.url = "http://whattomine.com/coins/{}.json?hr={}&p={}&fee=0.0&cost={}".format(id_url, hashrate_value, watts, COST_KWH)

        (self.hashrate_value, self.hashrate_unit) = update_unit_and_value(self.hashrate_value, self.hashrate_unit)
    def hashrate_pretty(self):
        return "{:3.2f} {}".format(self.hashrate_value, self.hashrate_unit)

class MinerProfit(object):
    def __init__(self, config, data):
        self.config = config
        self.name = data['name']
        self.algorithm = data['algorithm']
        self.daily_return_in_coin = data['estimated_rewards']
        self.difficulty = data['difficulty']
        self.network_hash = data['nethash']
        self.revenue_day = data['revenue']
        self.cost_day = data['cost']

    def hashrate_pretty(self):
        (value, unit) = update_unit_and_value(self.network_hash/1000000.0, "MH/s")
        return "{:.1f}{}".format(value, unit)

    def __str__(self):
        (value, unit) = update_unit_and_value(self.network_hash/1000000.0, "MH/s")
        return "{} - {} algo: {} daily_return: {} network_hash:{:.1f}{} revenue_day:{} cost_day:{}".format(self.config.model_name, self.name, self.algorithm, self.daily_return_in_coin, value, unit, self.revenue_day, self.cost_day)

def get_coin_from_model(model_str):
    # TODO: For now hardcoding the coin for a given model.
    if model_str == "A741" or model_str == "S9" or model_str == "GekkoScience":
        return Coin.Bitcoin
    elif model_str == "D3":
        return Coin.Dash
    elif model_str == "L3+":
        return Coin.Litecoin
    else:
        assert False, "Unsupported model {}".format(model_str)

def get_hashrate(value, unit, target_unit):
    while unit <> target_unit:
        value = value * 1000.0
        if unit == 'GH/s':
            unit = 'MH/s'
        elif unit == 'TH/s':
            unit = 'GH/s'
        elif unit == 'PH/s':
            unit = 'TH/s'
        elif unit == 'EH/s':
            unit = 'PH/s'
        else:
            assert False, "Unsupported unit: {}".format(unit)
    return value

def get_target_hashrate_from_coin(coin):
    if coin == Coin.Bitcoin or coin == Coin.BitcoinCash:
        return "GH/s"
    else:
        return "MH/s"

def get_miners_profit():
    miners = Miner.query.all()
    result = []

    for miner in miners:
        miner_instance_list = get_miner_instance(miner)
        for miner_instance in miner_instance_list:
            coin = get_coin_from_model(miner_instance.miner.model.model)
            hashrate_unit = get_target_hashrate_from_coin(coin)
            config = MinerConfig(model_name=miner_instance.miner.model.model,
                coin=coin,
                hashrate_value=get_hashrate(miner_instance.hashrate_value, miner_instance.hashrate_unit, hashrate_unit),
                hashrate_unit=hashrate_unit,
                watts=miner_instance.miner.model.watts)
            r = requests.get(config.url)
            if r.status_code == 200:
                mp = MinerProfit(config=config, data=json.loads(r.text))
                print(mp)
                result.append(mp)
            else:
                print("Error while making the request")
                print(str(r))
    return result