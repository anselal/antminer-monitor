import concurrent.futures
import re
import sys
import time
from datetime import timedelta

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from antminermonitor.blueprints.asicminer.asic_antminer import ASIC_ANTMINER
from antminermonitor.blueprints.asicminer.models import Miner
from antminermonitor.database import db_session
from config.settings import MODELS, NUM_THREADS
from lib.util_hashrate import update_unit_and_value
from lib.util_notify import notify_telegram

antminer = Blueprint('antminer', __name__, template_folder='../templates')


@antminer.route('/')
@login_required
def miners():
    # Init variables
    start = time.perf_counter()
    miners = Miner.query.all()
    active_miners = []
    inactive_miners = []

    warnings = []
    errors = []
    total_hash_rate_per_model = {}
    miner_objects = []

    # lookup table for total_hash_rate_per_model
    for id, miner in MODELS.items():
        total_hash_rate_per_model[id] = {"value": 0, "unit": miner.get('unit')}

    # create miner objects to pass to executor.map
    for miner in miners:
        module = MODELS[miner.model_id]['model_module']
        cls = MODELS[miner.model_id]['model_classname']
        obj = getattr(sys.modules[module], cls)(miner)
        miner_objects.append(obj)

    # pass this method to executor.map to poll the miner
    def poll(obj):
        obj.poll()
        return obj

    # run with ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=NUM_THREADS) as executor:
        results = executor.map(poll, miner_objects)
        for miner in results:
            if miner is not None:
                if miner.is_inactive:
                    inactive_miners.append(miner)
                else:
                    active_miners.append(miner)

                    for warning in miner.warnings:
                        warnings.append(warning)
                    for error in miner.errors:
                        errors.append(error)
                    total_hash_rate_per_model[
                        miner.model_id]["value"] += miner.hash_rate_ghs5s

    # Flash notifications
    if not miners:
        error_message = ("[INFO] No miners added yet. "
                         "Please add miners using the above form.")
        current_app.logger.info(error_message)
        flash(error_message, "info")
        notify_telegram(error_message)

    elif not errors:
        error_message = ("[INFO] All miners are operating normal. "
                         "No errors found.")
        current_app.logger.info(error_message)
        flash(error_message, "info")
        notify_telegram(error_message)

    for error in errors:
        current_app.logger.error(error)
        flash(error, "error")
        notify_telegram(error)

    for warning in warnings:
        current_app.logger.error(warning)
        flash(warning, "warning")
        notify_telegram(warning)

    # flash("[INFO] Check chips on your miner", "info")
    # flash("[SUCCESS] Miner added successfully", "success")
    # flash("[WARNING] Check temperatures on your miner", "warning")
    # flash("[ERROR] Check board(s) on your miner", "error")

    # Convert the total_hash_rate_per_model into a data structure that the
    # template can consume.
    total_hash_rate_per_model_temp = {}
    for key in total_hash_rate_per_model:
        value, unit = update_unit_and_value(
            total_hash_rate_per_model[key]["value"],
            total_hash_rate_per_model[key]["unit"])
        if value > 0:
            total_hash_rate_per_model_temp[key] = f"{value:3.2f} {unit}"

    end = time.perf_counter()
    loading_time = end - start
    return render_template(
        'asicminer/home.html',
        version=current_app.config['__VERSION__'],
        models=MODELS,
        errors=errors,
        warnings=warnings,
        active_miners=active_miners,
        inactive_miners=inactive_miners,
        loading_time=loading_time,
        total_hash_rate_per_model=total_hash_rate_per_model_temp)


@antminer.route('/add', methods=['POST'])
@login_required
def add_miner():
    miner_ip = request.form['ip']
    miner_model_id = request.form.get('model_id')
    miner_remarks = request.form['remarks']

    # exists = Miner.query.filter_by(ip="").first()
    # if exists:
    #    return "IP Address already added"

    add_miner(miner_ip, miner_model_id, miner_remarks)

    return redirect(url_for('antminer.miners'))


def add_miner(miner_ip, miner_model_id, miner_remarks):
    try:
        miner = Miner(ip=miner_ip,
                      model_id=miner_model_id,
                      remarks=miner_remarks)
        db_session.add(miner)
        db_session.commit()
        current_app.logger.info(
            f"Miner with IP Address {miner.ip} added successfully")
        flash(f"Miner with IP Address {miner.ip} added successfully",
              "success")
    except IntegrityError:
        db_session.rollback()
        current_app.logger.info(f"IP Address {miner.ip} already added")
        flash(f"IP Address {miner.ip} already added", "error")


@antminer.route('/discovery/', methods=['POST'])
@login_required
def miner_discovery():

    subnet = request.form.get('subnet') + "."
    start_ip = request.form.get('start_ip', type=int)
    end_ip = request.form.get('end_ip', type=int)

    if end_ip < start_ip:
        current_app.logger.error(
            f"Start IP ({start_ip}) cannot be smaller than the end IP ({end_ip})"
        )
        flash(
            f"Start IP ({start_ip}) cannot be smaller than the end IP ({end_ip})",
            "error")
        return redirect(url_for('miners'))

    supported_miner = ""
    miner_model_id = ""

    def is_pycgminer(ip):
        from lib.pycgminer import get_stats
        try:
            miner_stats = get_stats(ip)
            if miner_stats['STATUS'][0]['STATUS'] == 'error':
                current_app.logger.error("Error querying IP %s" % ip)
                flash(f"Error querying IP {ip}", "error")
                return False
        except Exception as c:
            return False
        try:
            return miner_stats['STATS'][0]['Type']
        except Exception as c:
            return False

    def add_if_supported(ip, model_id):
        # check if the miner is supported by the software
        try:
            supported_miner = [id for id in MODELS.keys() if id == model_id][0]
            add_miner(ip, supported_miner, "")
            return True
        except IndexError as i:
            return False

    while start_ip <= end_ip:
        ip = subnet + str(start_ip)
        current_app.logger.info("Querying IP %s" % ip)

        # check if is pycgminer
        miner_model_id = is_pycgminer(ip)
        if miner_model_id:
            is_supported = add_if_supported(ip, miner_model_id)
            if is_supported:
                start_ip += 1
                # TODO
                # log message of added supported miner model and IP
                continue

        # miner is not supported by the software
        current_app.logger.error(
            f"Miner with IP {ip} is currently not supported by AntminerMonitor"
        )
        flash(
            f"Miner with IP {ip} is currently not supported by AntminerMonitor",
            "info")

        start_ip += 1

    return redirect(url_for('antminer.miners'))


@antminer.route('/delete/<id>')
@login_required
def delete_miner(id):
    miner = Miner.query.filter_by(id=int(id)).first()
    if miner:
        db_session.delete(miner)
        db_session.commit()
        flash(f"Miner {miner.ip} removed successfully", "info")
    return redirect(url_for('antminer.miners'))
