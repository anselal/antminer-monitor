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

import time

from miner_adapter import make_miner_instance_bitmain, update_unit_and_value

@app.route('/')
def miners():
    # Init variables
    start = time.clock()
    miners = Miner.query.all()
    models = MinerModel.query.all()
    active_miner_instances = []
    inactive_miners = []
    total_hash_rate_per_model = {"L3+": {"value": 0, "unit": "<EMPTY>" },
                                "S7": {"value": 0, "unit": "<EMPTY>" },
                                "S9": {"value": 0, "unit": "<EMPTY>" },
                                "D3": {"value": 0, "unit": "<EMPTY>" }}
    errors = False

    for miner in miners:
        miner_instance_list = make_miner_instance_bitmain(miner, get_stats(miner.ip), get_pools(miner.ip))

        # if miner not accessible
        if not miner_instance_list:
            errors = True
            inactive_miners.append(miner)
        else:
            for miner_instance in miner_instance_list:
                total_hash_rate_per_model[miner.model.model]["value"] += miner_instance.hashrate_value
                total_hash_rate_per_model[miner.model.model]["unit"] = miner_instance.hashrate_unit
                active_miner_instances.append(miner_instance)

                # Flash error messages
                if miner_instance.defective_chip_count > 0:
                    error_message = "[WARNING] '{}' chips are defective on miner '{}'.".format(miner_instance.defective_chip_count, miner.ip)
                    logger.warning(error_message)
                    flash(error_message, "warning")
                    errors = True
                    miner_instance.errors.append("CHIP_DEFECTIVE")
                if miner_instance.working_chip_count + miner_instance.defective_chip_count < miner_instance.expected_chip_count:
                    error_message = "[ERROR] ASIC chips are missing from miner '{}'. Your Antminer '{}' has '{}/{} chips'." \
                        .format(miner.ip,
                                miner.model.model,
                                miner_instance.working_chip_count + miner_instance.defective_chip_count,
                                miner_instance.expected_chip_count)
                    logger.error(error_message)
                    flash(error_message, "error")
                    errors = True
                    miner_instance.errors.append("CHIP_COUNT")
                if max(miner_instance.temps) >= 70:
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
                           active_miner_instances=active_miner_instances,
                           inactive_miners=inactive_miners,
                           total_hash_rate_per_model=total_hash_rate_per_model_temp,
                           loading_time=loading_time,
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