from flask import (jsonify,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   )
from sqlalchemy.exc import IntegrityError
from app.pycgminer import CgminerAPI
from app import app, db, logger, __version__
from app.models import Miner, MinerModel, Settings
import re
import time


def get_summary(ip):
    cgminer = CgminerAPI(host=ip)
    output = cgminer.summary()
    output.update({"IP": ip})
    return dict(output)


def get_pools(ip):
    cgminer = CgminerAPI(host=ip)
    output = cgminer.pools()
    output.update({"IP": ip})
    return dict(output)


def get_stats(ip):
    cgminer = CgminerAPI(host=ip)
    output = cgminer.stats()
    output.update({"IP": ip})
    return dict(output)


@app.route('/<ip>/summary')
def summary(ip):
    output = get_summary(ip)
    return jsonify(output)


@app.route('/<ip>/pools')
def pools(ip):
    output = get_pools(ip)
    return jsonify(output)


@app.route('/<ip>/stats')
def stats(ip):
    output = get_stats(ip)
    return jsonify(output)


@app.route('/')
def miners():
    # Init variables
    start = time.clock()
    miners = Miner.query.all()
    models = MinerModel.query.all()
    active_miners = []
    inactive_miners = []
    miner_chips = {}
    temperatures = {}
    fans = {}
    hash_rates = {}
    total_hash_rate_per_model = {"L3+": 0,
                                 "S7": 0,
                                 "S9": 0,
                                 "D3": 0}
    errors = False
    miner_errors = {}

    for miner in miners:
        miner_stats = get_stats(miner.ip)
        # if miner not accessible
        if miner_stats['STATUS'][0]['STATUS'] == 'error':
            errors = True
            inactive_miners.append(miner)
        else:
            # Get miner's ASIC chips
            asic_chains = [miner_stats['STATS'][1][chain] for chain in miner_stats['STATS'][1].keys() if
                           "chain_acs" in chain]
            # count number of working chips
            O = [str(o).count('o') for o in asic_chains]
            Os = sum(O)
            # count number of defective chips
            X = [str(x).count('x') for x in asic_chains]
            Xs = sum(X)
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
            ghs5s = miner_stats['STATS'][1]['GHS 5s']
            #
            fans.update({miner.ip: {"speeds": fan_speeds}})
            miner_chips.update({miner.ip: {'status': {'Os': Os, 'Xs': Xs},
                                           'total': total_chips,
                                           }
                                })
            temperatures.update({miner.ip: temps})
            hash_rates.update({miner.ip: ghs5s})
            total_hash_rate_per_model[miner.model.model] += float(str(ghs5s))
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
            if max(temps) >= 80:
                error_message = "[WARNING] High temperatures on miner '{}'.".format(miner.ip)
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
                           miner_chips=miner_chips,
                           temperatures=temperatures,
                           loading_time=loading_time,
                           fans=fans,
                           hash_rates=hash_rates,
                           total_hash_rate_per_model=total_hash_rate_per_model,
                           miner_errors=miner_errors,
                           )


@app.route('/add', methods=['POST'])
def add_miner():
    miner_ip = request.form['ip']
    miner_model_id = request.form.get('model_id')
    miner_remarks = request.form['remarks']

    # exists = Miner.query.filter_by(ip="").first()
    # if exists:
    #    return "IP Address already added"

    try:
        miner = Miner(ip=miner_ip, model_id=miner_model_id, remarks=miner_remarks)
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
