import requests
import json
import re
from enum import Enum
from miner_adapter import get_miner_instance, update_unit_and_value
from app.models import Miner, MinerModel
from cached_http_request import CachedHttpRequest

class Coin(Enum):
    Bitcoin = 1,
    BitcoinCash = 2,
    Dash = 3,
    Litecoin = 4

    def get_symbol(self):
        return {
            Coin.Bitcoin: "BTC",
            Coin.BitcoinCash: "BCH",
            Coin.Dash: "DASH",
            Coin.Litecoin: "LTC",
        }[Coin(self.value)]

def get_hashrate_in_smallest(value, unit, target_unit):
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

def fetch_price_for_coin(cached_http_request, coin):
    url = "https://min-api.cryptocompare.com/data/price?fsym={}&tsyms=USD".format(coin.get_symbol())
    data = cached_http_request.get(url)
    if not data is None:
        return json.loads(data)['USD']
    else:
        return 0

class MiningInfo(object):
    def __init__(self, coin, hashrate_value, hashrate_unit, watts, usd_per_kwh, cached_http_request):
        self.coin = coin
        self.hashrate_value = hashrate_value
        self.hashrate_unit = hashrate_unit
        self.watts = watts
        self.usd_per_kwh = usd_per_kwh
        self.cached_http_request = cached_http_request

    def get_target_hashrate_from_coin(self):
        if self.coin == Coin.Bitcoin or self.coin == Coin.BitcoinCash:
            return "GH/s"
        else:
            return "MH/s"

    def extract_dollar(self, value_str):
        matches = re.findall(r'\$([0-9]+)\.*([0-9]*)', value_str)
        assert len(matches) == 1
        assert len(matches[0]) == 2
        return int(matches[0][0]) + int(matches[0][1]) / 100.0

    def fetch(self):
        id_url = 0
        if self.coin == Coin.Dash:
            id_url = 34
        elif self.coin == Coin.Bitcoin:
            id_url = 1
        elif self.coin == Coin.Litecoin:
            id_url = 4
        elif self.coin == Coin.BitcoinCash:
            id_url = 193
        else:
            assert False, "Unsupported coin {}".format(self.coin.name)

        # Perhaps use the model hashrate to get better caching.
        hashrate_api = get_hashrate_in_smallest(
            self.hashrate_value, self.hashrate_unit, self.get_target_hashrate_from_coin())
        url = "http://whattomine.com/coins/{}.json?hr={}&p=800&fee=0.0&cost={}".format(
            id_url, hashrate_api, self.usd_per_kwh)
        data = self.cached_http_request.get(url)
        if not data is None:
            data = json.loads(data)

            network_hash = data['nethash']
            (network_hash_value, network_hash_unit) = update_unit_and_value(
                network_hash / 1000000.0, "MH/s")
            cost_per_day = round((self.usd_per_kwh * self.watts * 24)/1000.0, 2)
            daily_return_in_coins = float(data['estimated_rewards'])
            return {
                'coin': self.coin,
                'daily_return_in_coin': daily_return_in_coins,
                'network_hash_value': network_hash_value,
                'network_hash_unit': network_hash_unit,
                'revenue_per_day': self.extract_dollar(data['revenue']),
                'cost_per_day': cost_per_day,
                'break_even_price': round(cost_per_day / daily_return_in_coins, 2),
                'current_price': fetch_price_for_coin(self.cached_http_request, self.coin)
            }
        else:
            return None


class MinerProfit(object):
    def __init__(self, miner_instance, data):
        self.miner_instance = miner_instance
        self.data = data

    def number_of_devices(self):
        network_hashrate_mhs = get_hashrate_in_smallest(
            self.data['network_hash_value'], self.data['network_hash_unit'], "MH/s")
        device_hashrate_mhs = get_hashrate_in_smallest(
            self.miner_instance.hashrate_value, self.miner_instance.hashrate_unit, "MH/s")
        return "{:,}".format(int(network_hashrate_mhs / device_hashrate_mhs))


def get_coin_from_model(model_str):
    # TODO: For now hardcoding the coin for a given model.
    if model_str == "AV741" or model_str == "AV821" or model_str == "S9" or model_str == "GekkoScience":
        return Coin.Bitcoin
    elif model_str == "D3":
        return Coin.Dash
    elif model_str == "L3+" or model_str == "R1-LTC":
        return Coin.Litecoin
    else:
        assert False, "Unsupported model {}".format(model_str)


def get_miners_profit(usd_per_kwh):
    miners = Miner.query.all()
    result = []
    total_revenue = 0
    total_cost = 0
    total_coins = {}
    # TODO: Potentially reuse this between requests.
    cached_http_request = CachedHttpRequest(entry_expiration_secs=60)

    for miner in miners:
        miner_instance_list = get_miner_instance(miner)
        for miner_instance in miner_instance_list:
            coin = get_coin_from_model(miner_instance.miner.model.model)
            mi = MiningInfo(coin, miner_instance.hashrate_value,
                            miner_instance.hashrate_unit, miner_instance.miner.model.watts, usd_per_kwh, cached_http_request)
            data = mi.fetch()
            if not data is None:
                mp = MinerProfit(miner_instance=miner_instance, data=data)
                total_revenue += data['revenue_per_day']
                total_cost += data['cost_per_day']

                prev_coin_amt = 0
                if coin.name in total_coins:
                    prev_coin_amt = total_coins[coin.name]
                total_coins[coin.name] = prev_coin_amt + data['daily_return_in_coin']
                result.append(mp)
            else:
                print("Error while making the request")

    return {
        "daily_revenue_usd": total_revenue,
        "daily_cost_usd": total_cost,
        "profits": result,
        "total_coins": total_coins
    }
