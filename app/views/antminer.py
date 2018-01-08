from flask import (jsonify,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   )
from flask.views import MethodView
from app.views.antminer_json import (get_summary,
                                     get_pools,
                                     get_stats,
                                     )
from sqlalchemy.exc import IntegrityError
from app.pycgminer import CgminerAPI
from app import app, db, logger, __version__
from app.models import Miner, MinerModel, Settings
import re
from datetime import timedelta
import time

class BaseMetric(object):
    """
        This class encapsulates a unit and a value.

        The only convenience method it provides is a __str__
    """
    def __init__(self, value, unit, supported_units, format_pattern):
        self.value = value
        self.unit = unit
        self.supported_units = supported_units
        self.format_pattern = format_pattern        
        assert self._validate(), "Invalid BaseMetric"

    def _validate(self):
        return self.value >= 0 and self.unit in self.supported_units

    def __str__(self):
        value_new = self.value
        unit_new = self.unit

        # Update from one unit to the next if the value is greater than 1000.
        # e.g. update_unit_and_value(1000, "GH/s") => (1, "TH/s")
        if value_new > 1000:
                value_new = value_new / 1000
                idx = self.supported_units.index(self.unit)
                assert idx >= 0 and idx < len(self.supported_units) - 1
                unit_new = self.supported_units[idx+1]

        # Formats
        # ( 19250, "MH/s") => "19.25 GH/s"
        return self.format_pattern.format(value_new, unit_new)

HASH_RATE_SUPPORTED_UNITS = ["MH/s", "GH/s", "TH/s"]
class HashRate(BaseMetric):
    def __init__(self, value, unit):
        super(HashRate,self).__init__(value, unit, HASH_RATE_SUPPORTED_UNITS, "{:3.2f} {}")

    def add(self, other):
        """Adds two BasicMetric if they have the same unit.

            Input:
                * other: HashRate object to be added to the current instance.

            Returns: Returns a new instance with the new HashRate.
        """
        if self.unit <> other.unit:
            assert False, "Not supporting adding different units"
            return None
        return HashRate(self.value + other.value, self.unit)

CLOCK_RATE_SUPPORTED_UNITS = ["Mhz", "Ghz"]
class ClockRate(BaseMetric):
    def __init__(self, value, unit):
        super(ClockRate,self).__init__(value, unit, CLOCK_RATE_SUPPORTED_UNITS, "{:3.0f} {}")

class NumberVector(object):
    """
        This class is essentially a way for the template access
        other python methods. This is used for temperatures and
        fan speed.

        For example, if the maximum element of the temperature
        is above certain threshold we want to show a warning.
    """
    def __init__(self, elements):
        self.elements = elements

    def append(self, num):
        """
            Appends 'num' to the end of the list.
        """
        self.elements.append(num)

    def max(self):
        """
            Returns the maximum of the elements.
        """
        return max(self.elements)

    def min(self):
        """
            Returns the minimum of the elements.
        """
        return min(self.elements)

    def __str__(self):
        return str(self.elements)

@app.route('/')
def miners():
    # Init variables
    start = time.clock()
    miners = Miner.query.all()
    models = MinerModel.query.all()
    active_miners = []
    inactive_miners = []
    workers = {}
    miner_chips = {}
    temperatures = {}
    clock_speed = {}
    clock_speed_percentage = {}
    fans = {}
    max_fan_rpm = {}
    hash_rates = {}
    hw_error_rates = {}
    uptimes = {}
    # TODO(sergioclemente): Abstract these configurations in a separate class. 
    mapping_hash_rate = {'L3+': 'MH/s', 'S7': 'GH/s', 'S9': 'GH/s', 'D3': 'MH/s'}
    mapping_default_clockrate = {'L3+': 384.0, 'S7': 1.0, 'S9': 550, 'D3': 487.0}
    mapping_max_fan_rpm = {'L3+': 7125.0, 'S7': 7125.0, 'S9': 7125.0, 'D3': 7125.0}
    total_hash_rate_per_model = {"L3+": HashRate(0, mapping_hash_rate["L3+"]),
                                 "S7": HashRate(0, mapping_hash_rate["S7"]),
                                 "S9": HashRate(0, mapping_hash_rate["S9"]),
                                 "D3": HashRate(0, mapping_hash_rate["D3"])}

    errors = False
    miner_errors = {}

    for miner in miners:
        miner_stats = get_stats(miner.local_ip)
        # if miner not accessible
        if miner_stats['STATUS'][0]['STATUS'] <> 'S':
            errors = True
            inactive_miners.append(miner)
        else:
            # Get worker name
            miner_pools = get_pools(miner.local_ip)
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
            ghs5s = float(str(miner_stats['STATS'][1]['GHS 5s']))
            # Get HW Errors
            hw_error_rate = miner_stats['STATS'][1]['Device Hardware%']
            # Get uptime
            uptime = timedelta(seconds=miner_stats['STATS'][1]['Elapsed'])
            #
            workers.update({miner.local_ip: worker})
            miner_chips.update({miner.local_ip: {'status': {'Os': Os, 'Xs': Xs, '-': _dash_chips},
                                           'total': total_chips,
                                           }
                                })
            clock_rate = int(miner_stats['STATS'][1]['frequency'])
            clock_speed.update({miner.local_ip: ClockRate(clock_rate, "Mhz")})
            clock_speed_percentage.update({miner.local_ip: 100*clock_rate / mapping_default_clockrate[miner.model.model]})
            temperatures.update({miner.local_ip: NumberVector(temps)})
            fans.update({miner.local_ip: {"speeds": NumberVector(fan_speeds)}})
            max_fan_rpm.update({miner.local_ip: mapping_max_fan_rpm[miner.model.model]})
            hash_rate = HashRate(ghs5s, mapping_hash_rate[miner.model.model])
            hash_rates.update({miner.local_ip: hash_rate})
            hw_error_rates.update({miner.local_ip: hw_error_rate})
            uptimes.update({miner.local_ip: uptime})
            total_hash_rate_per_model[miner.model.model] = hash_rate.add(total_hash_rate_per_model[miner.model.model])
            active_miners.append(miner)

            # Flash error messages
            if Xs > 0:
                error_message = "[WARNING] '{}' chips are defective on miner '{}'.".format(Xs, miner.local_ip)
                logger.warning(error_message)
                flash(error_message, "warning")
                errors = True
                miner_errors.update({miner.local_ip: error_message})
            if Os + Xs < total_chips:
                error_message = "[ERROR] ASIC chips are missing from miner '{}'. Your Antminer '{}' has '{}/{} chips'." \
                    .format(miner.local_ip,
                            miner.model.model,
                            Os + Xs,
                            total_chips)
                logger.error(error_message)
                flash(error_message, "error")
                errors = True
                miner_errors.update({miner.local_ip: error_message})
            if max(temps) >= 80:
                error_message = "[WARNING] High temperatures on miner '{}'.".format(miner.local_ip)
                logger.warning(error_message)
                flash(error_message, "warning")

    # Flash success/info message
    if not miners:
        error_message = "[INFO] No miners added yet. Please add miners using the above form."
        logger.info(error_message)
        flash(error_message, "info")
    elif not errors:
        error_message = "[INFO] All miners are operating normal. No errors found."
        logger.info(error_message)
        flash(error_message, "info")

    # flash("INFO !!! Check chips on your miner", "info")
    # flash("SUCCESS !!! Miner added successfully", "success")
    # flash("WARNING !!! Check temperatures on your miner", "warning")
    # flash("ERROR !!!Check board(s) on your miner", "error")

    end = time.clock()
    loading_time = end - start
    return render_template('myminers.html',
                           version=__version__,
                           models=models,
                           active_miners=active_miners,
                           inactive_miners=inactive_miners,
                           workers=workers,
                           miner_chips=miner_chips,
                           clock_speed=clock_speed,
                           clock_speed_percentage=clock_speed_percentage,
                           temperatures=temperatures,
                           fans=fans,
                           max_fan_rpm=max_fan_rpm,
                           hash_rates=hash_rates,
                           hw_error_rates=hw_error_rates,
                           uptimes=uptimes,
                           total_hash_rate_per_model=total_hash_rate_per_model,
                           loading_time=loading_time,
                           miner_errors=miner_errors,
                           )


@app.route('/add', methods=['POST'])
def add_miner():
    local_ip = request.form['local_ip']
    http_admin_host_port = request.form['http_admin_host_port']
    miner_model_id = request.form.get('model_id')
    miner_remarks = request.form['remarks']

    # exists = Miner.query.filter_by(ip="").first()
    # if exists:
    #    return "IP Address already added"

    try:
        miner = Miner(local_ip=local_ip, http_admin_host_port=http_admin_host_port, model_id=miner_model_id, remarks=miner_remarks)
        db.session.add(miner)
        db.session.commit()
        flash("Miner with Local IP Address {} added successfully".format(miner.local_ip), "success")
    except IntegrityError as e:
        db.session.rollback()
        flash("Local IP Address {} already added".format(local_ip), "error")

    return redirect(url_for('miners'))


@app.route('/delete/<id>')
def delete_miner(id):
    miner = Miner.query.filter_by(id=int(id)).first()
    db.session.delete(miner)
    db.session.commit()
    return redirect(url_for('miners'))
