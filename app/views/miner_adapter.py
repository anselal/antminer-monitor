import re
from sets import Set
from datetime import timedelta


class miner_instance(object):
    def __init__(self, worker, working_chip_count, defective_chip_count, inactive_chip_count, expected_chip_count, hashrate_value, hashrate_unit, temps, fan_speeds, hw_error_rate_pct, uptime_secs, errors, miner):
        self.worker = worker
        self.working_chip_count = working_chip_count
        self.defective_chip_count = defective_chip_count
        self.inactive_chip_count = inactive_chip_count
        self.expected_chip_count = expected_chip_count
        self.hashrate_value = hashrate_value
        self.hashrate_unit = hashrate_unit
        self.temps = temps
        self.fan_speeds = fan_speeds
        self.hw_error_rate_pct = hw_error_rate_pct
        self.uptime = timedelta(seconds=uptime_secs)
        self.errors = errors
        self.miner = miner

    def hashrate_pretty(self):
        return "{:3.2f} {}".format(self.hashrate_value, self.hashrate_unit)

    def __str__(self):
        return "worker:{} working_chip_count:{} defective_chip_count:{} inactive_chip_count:{} expected_chip_count:{} hashrate_value:{} hashrate_unit:{} temps:{} fan_speeds:{} hw_error_rate_pct:{} uptime:{} errors:{}".format(self.worker, self.working_chip_count, self.inactive_chip_count, self.defective_chip_count, self.expected_chip_count, self.hashrate_value, self.hashrate_unit, self.temps, self.fan_speeds, self.hw_error_rate_pct, self.uptime, self.errors)

# Update from one unit to the next if the value is greater than 1024.
# e.g. update_unit_and_value(1024, "GH/s") => (1, "TH/s")
def update_unit_and_value(value, unit):
    while value > 1024:
        value = value / 1024.0
        if unit == 'MH/s':
            unit = 'GH/s'
        elif unit == 'GH/s':
            unit = 'TH/s'
        else:
            assert False, "Unsupported unit: {}".format(unit)
    return (value, unit)


def make_miner_instance_bitmain(miner, miner_stats, miner_pools):
    # if miner not accessible
    if miner_stats['STATUS'][0]['STATUS'] == 'error':
        return []

    hashrate_unit_map = {"L3+": "MH/s",
                         "S7": "GH/s",
                         "S9": "GH/s",
                         "D3": "MH/s"}

    # Get worker name
    worker = miner_pools['POOLS'][0]['User']
    # Get miner's ASIC chips
    asic_chains = [miner_stats['STATS'][1][chain] for chain in miner_stats['STATS'][1].keys() if
                   "chain_acs" in chain]
    # count number of working chips
    O = [str(o).count('o') for o in asic_chains]
    Os = sum(O)
    # count number of defective chips
    X = [str(x).count('x') for x in asic_chains]
    Xs = sum(X)
    # get number of in-active chips
    _dash_chips = [str(x).count('-') for x in asic_chains]
    _dash_chips = sum(_dash_chips)
    # Get total number of chips according to miner's model
    # convert miner.model.chips to int list and sum
    chips_list = [int(y) for y in str(miner.model.chips).split(',')]
    total_chips = sum(chips_list)

    # Get the temperatures of the miner according to miner's model
    temps = [int(miner_stats['STATS'][1][temp]) for temp in
             sorted(miner_stats['STATS'][1].keys(), key=lambda x: str(x)) if
             re.search(miner.model.temp_keys + '[0-9]', temp) if miner_stats['STATS'][1][temp] != 0]
    # Get fan speeds
    fan_speeds = [miner_stats['STATS'][1][fan] for fan in
                  sorted(miner_stats['STATS'][1].keys(), key=lambda x: str(x)) if
                  re.search("fan" + '[0-9]', fan) if miner_stats['STATS'][1][fan] != 0]
    # Get GH/S 5s
    hashrate_value = float(str(miner_stats['STATS'][1]['GHS 5s']))
    hashrate_unit = hashrate_unit_map[miner.model.model]
    hashrate_value, hashrate_unit = update_unit_and_value(
        hashrate_value, hashrate_unit)

    # Get HW Errors
    hw_error_rate = miner_stats['STATS'][1]['Device Hardware%']
    # Get uptime
    uptime = seconds = miner_stats['STATS'][1]['Elapsed']

    return [miner_instance(worker=worker,
                           working_chip_count=Os,
                           defective_chip_count=Xs,
                           inactive_chip_count=_dash_chips,
                           expected_chip_count=total_chips,
                           hashrate_value=hashrate_value,
                           hashrate_unit=hashrate_unit,
                           temps=temps,
                           fan_speeds=fan_speeds,
                           hw_error_rate_pct=hw_error_rate,
                           uptime_secs=uptime,
                           errors=[],
                           miner=miner)]
