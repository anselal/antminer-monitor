from flask import (jsonify,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   )
from app.lib.pycgminer import (get_summary,
                               get_pools,
                               get_stats,
                               )
from sqlalchemy.exc import IntegrityError
from app import app, db, logger, __version__
from app.models import Miner, MinerModel, Settings
from app.lib.util_hashrate import update_unit_and_value
import re
from datetime import timedelta
import time


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
    fans = {}
    hash_rates = {}
    hw_error_rates = {}
    uptimes = {}
    total_hash_rate_per_model = {"L3+": {"value": 0, "unit": "MH/s" },
                                "S7": {"value": 0, "unit": "GH/s" },
                                "S9": {"value": 0, "unit": "GH/s" },
                                "D3": {"value": 0, "unit": "MH/s" },
                                "T9": {"value": 0, "unit": "TH/s" },
                                "A3": {"value": 0, "unit": "GH/s" },
                                "L3": {"value": 0, "unit": "MH/s" },}
                                
    errors = False
    miner_errors = {}

    for miner in miners:
        miner_stats = get_stats(miner.ip)
        # if miner not accessible
        if miner_stats['STATUS'][0]['STATUS'] == 'error':
            errors = True
            inactive_miners.append(miner)
        else:
            # Get worker name
            miner_pools = get_pools(miner.ip)
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
            workers.update({miner.ip: worker})
            miner_chips.update({miner.ip: {'status': {'Os': Os, 'Xs': Xs, '-': _dash_chips},
                                           'total': total_chips,
                                           }
                                })
            temperatures.update({miner.ip: temps})
            fans.update({miner.ip: {"speeds": fan_speeds}})
            value, unit = update_unit_and_value(ghs5s, total_hash_rate_per_model[miner.model.model]['unit'])
            hash_rates.update({miner.ip: "{:3.2f} {}".format(value, unit)})
            hw_error_rates.update({miner.ip: hw_error_rate})
            uptimes.update({miner.ip: uptime})
            total_hash_rate_per_model[miner.model.model]["value"] += ghs5s
            active_miners.append(miner)

            # Flash error messages
            if Xs > 0:
                error_message = "[WARNING] '{}' chips are defective on miner '{}'.".format(Xs, miner.ip)
                logger.warning(error_message)
                flash(error_message, "warning")
                errors = True
                miner_errors.update({miner.ip: error_message})
            if Os + Xs < total_chips:
                error_message = "[ERROR] ASIC chips are missing from miner '{}'. Your Antminer '{}' has '{}/{} chips'." \
                    .format(miner.ip,
                            miner.model.model,
                            Os + Xs,
                            total_chips)
                logger.error(error_message)
                flash(error_message, "error")
                errors = True
                miner_errors.update({miner.ip: error_message})
            if temps:
                if max(temps) >= 80:
                    error_message = "[WARNING] High temperatures on miner '{}'.".format(miner.ip)
                    logger.warning(error_message)
                    flash(error_message, "warning")
            if not temps:
                temperatures.update({miner.ip: 0})
                error_message = "[ERROR] Could not retrieve temperatures from miner '{}'.".format(miner.ip)
                logger.warning(error_message)
                flash(error_message, "error")

    # Flash success/info message
    if not miners:
        error_message = "[INFO] No miners added yet. Please add miners using the above form."
        logger.info(error_message)
        flash(error_message, "info")
    elif not errors:
        error_message = "[INFO] All miners are operating normal. No errors found."
        logger.info(error_message)
        flash(error_message, "info")

    # flash("[INFO] Check chips on your miner", "info")
    # flash("[SUCCESS] Miner added successfully", "success")
    # flash("[WARNING] Check temperatures on your miner", "warning")
    # flash("[ERROR] Check board(s) on your miner", "error")

    # Convert the total_hash_rate_per_model into a data structure that the template can
    # consume.
    total_hash_rate_per_model_temp = {}
    for key in total_hash_rate_per_model:
        value, unit = update_unit_and_value(total_hash_rate_per_model[key]["value"], total_hash_rate_per_model[key]["unit"])
        if value > 0:
            total_hash_rate_per_model_temp[key] = "{:3.2f} {}".format(value, unit)


    end = time.clock()
    loading_time = end - start
    return render_template('myminers.html',
                           version=__version__,
                           models=models,
                           active_miners=active_miners,
                           inactive_miners=inactive_miners,
                           workers=workers,
                           miner_chips=miner_chips,
                           temperatures=temperatures,
                           fans=fans,
                           hash_rates=hash_rates,
                           hw_error_rates=hw_error_rates,
                           uptimes=uptimes,
                           total_hash_rate_per_model=total_hash_rate_per_model_temp,
                           loading_time=loading_time,
                           miner_errors=miner_errors,
                           )


def detect_model(ip):
    stats = get_stats(ip)

    # Check for connectivity error.
    if stats['STATUS'][0]['STATUS'] == 'error':
        flash("[ERROR] Error while connecting to miner at ip address '{}'.".format(
            ip), "error")
        return None

    # Try identifying the device.
    model_name = None
    if 'Type' in stats['STATS'][0]:
        models = re.findall(r'Antminer (\w*\+?)', stats['STATS'][0]['Type'])
        if len(models) == 1:
            model_name = models[0]
    elif 'ID' in stats['STATS'][0]:
        # ID are used for devices like Avalon.
        model_name = stats['STATS'][0]['ID']

    if not model_name is None:
        model = MinerModel.query.filter_by(model=model_name).first()
        if not model is None:
            return model
    else:
        model_name = "Unknown"

    flash("[ERROR] Miner type '{}' at ip address '{}' is not supported.".format(
        model_name, ip), "error")
    return None

@app.route('/add', methods=['POST'])
def add_miner():
    miner_ip = request.form['ip']
    model = detect_model(miner_ip)
    if not model is None:
        miner_remarks = request.form['remarks']

        try:
            miner = Miner(ip=miner_ip, model_id=model.id, remarks=miner_remarks)
            db.session.add(miner)
            db.session.commit()
            flash("Miner with IP Address {} added successfully".format(miner.ip), "success")
        except IntegrityError as e:
            db.session.rollback()
            flash("IP Address {} already added".format(miner_ip), "error")

    return redirect(url_for('miners'))


@app.route('/delete/<id>')
def delete_miner(id):
    miner = Miner.query.filter_by(id=int(id)).first()
    db.session.delete(miner)
    db.session.commit()
    return redirect(url_for('miners'))
