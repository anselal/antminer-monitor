import re
import time
from datetime import timedelta

from antminermonitor.blueprints.asicminer.base_miner import BaseMiner
from config.settings import MODELS
from lib.pycgminer import get_pools, get_stats, get_summary
from lib.util_hashrate import update_unit_and_value


class ASIC_ANTMINER(BaseMiner):
    def __init__(self, miner):
        super(ASIC_ANTMINER, self).__init__(miner)

    def poll(self):
        miner_stats = get_stats(self.ip)
        # if miner not accessible
        if miner_stats['STATUS'][0]['STATUS'] == 'error':
            self.is_inactive = True
            self.errors.append(miner_stats['STATUS'][0]['description'])
        else:
            try:
                # Get worker name
                miner_pools = get_pools(self.ip)
                active_pool = [
                    pool for pool in miner_pools['POOLS'] if pool['Stratum Active']
                ]
            except Exception as k:
                active_pool = []
            try:
                self.worker = active_pool[0]['User']
            except Exception as e:
                self.worker = ""

            # Get miner's ASIC chips
            asic_chains = [
                miner_stats['STATS'][1][chain]
                for chain in miner_stats['STATS'][1].keys()
                if "chain_acs" in chain
            ]

            # count number of working chips
            o = [str(o).count('o') for o in asic_chains]
            Os = sum(o)
            # count number of defective chips
            X = [str(x).count('x') for x in asic_chains]
            C = [str(x).count('C') for x in asic_chains]
            B = [str(x).count('B') for x in asic_chains]
            Xs = sum(X)
            Bs = sum(B)
            Cs = sum(C)
            # get number of in-active chips
            _dash_chips = [str(x).count('-') for x in asic_chains]
            _dash_chips = sum(_dash_chips)
            # Get total number of chips according to miner's model
            # convert miner.model.chips to int list and sum
            chips_list = [
                int(y)
                for y in str(MODELS.get(self.model_id).get('chips')).split(',')
            ]
            total_chips = sum(chips_list)

            self.chips.update({
                'Os': Os,
                'Xs': Xs,
                '-': _dash_chips,
                'total': total_chips
            })

            # Get the temperatures of the miner according to miner's model
            self.temperatures = [
                int(miner_stats['STATS'][1][temp])
                for temp in sorted(miner_stats['STATS'][1].keys(),
                                   key=lambda x: str(x))
                if re.search(
                    MODELS.get(self.model_id).get('temp_keys') + '[0-9]', temp)
                if miner_stats['STATS'][1][temp] != 0
            ]

            # Get fan speeds
            self.fan_speeds = [
                miner_stats['STATS'][1][fan]
                for fan in sorted(miner_stats['STATS'][1].keys(),
                                  key=lambda x: str(x))
                if re.search("fan" + '[0-9]', fan)
                if miner_stats['STATS'][1][fan] != 0
            ]

            # Get GH/S 5s
            try:
                self.hash_rate_ghs5s = float(
                    str(miner_stats['STATS'][1]['GHS 5s']))
            except Exception as e:
                miner_summary = get_summary(self.ip)
                self.hash_rate_ghs5s = float(
                    str(miner_summary['SUMMARY'][0]['GHS 5s']))

            # Normalize hashrate
            new_value, new_unit = update_unit_and_value(
                self.hash_rate_ghs5s, MODELS[self.model_id]['unit'])
            self.normalized_hash_rate = "{:3.2f} {}".format(
                new_value, new_unit)

            # Get HW Errors
            try:
                # Probably the miner is an Antminer E3 or S17
                miner_summary = get_summary(self.ip)
                self.hw_error_rate = miner_summary['SUMMARY'][0]['Device Hardware%']
            except Exception as e:
                # self.hw_error_rate = miner_stats['STATS'][1]['Device Hardware%']
                # this seems to work
                self.hw_error_rate = 0

            # Get uptime
            self.uptime = str(timedelta(seconds=miner_stats['STATS'][1]['Elapsed']))

            # Flash error messages
            if Xs > 0:
                error_message = ("[WARNING] '{}' chips are defective on "
                                 "miner '{}'.").format(Xs, self.ip)
                # current_app.logger.warning(error_message)
                # flash(error_message, "warning")
                self.warnings.append(error_message)
            if Os + Xs < total_chips:
                error_message = (
                    "[ERROR] ASIC chips are missing from miner "
                    "'{}'. Your Antminer '{}' has '{}/{} chips'.").format(
                        self.ip, self.model_id, Os + Xs, total_chips)
                # current_app.logger.error(error_message)
                # flash(error_message, "error")
                self.errors.append(error_message)
            if Bs > 0:
                # flash an info message. Probably the E3 is still warming up
                # error_message = (
                #    "[INFO] Miner '{}' is still warming up").format(self.ip)
                # current_app.logger.error(error_message)
                # flash(error_message, "info")
                pass
            if Cs > 0:
                # flask an info message. Probably the E3 is still warming up
                # error_message = (
                #    "[INFO] Miner '{}' is still warming up").format(self.ip)
                # current_app.logger.error(error_message)
                # flash(error_message, "info")
                pass

            if not self.temperatures:
                error_message = ("[ERROR] Could not retrieve temperatures "
                                 "from miner '{}'.").format(self.ip)
                # current_app.logger.warning(error_message)
                # flash(error_message, "error")
                self.errors.append(error_message)
            else:
                if max(self.temperatures) >= 80:
                    error_message = ("[WARNING] High temperatures on "
                                     "miner '{}'.").format(self.ip)
                    # current_app.logger.warning(error_message)
                    # flash(error_message, "warning")
                    self.warnings.append(error_message)
