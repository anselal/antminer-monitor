from flask import (jsonify,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   Response,
                   )
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from app import app, db, logger, __version__
from app.models import Miner, MinerModel, Settings
from app.views.antminer_json import (get_summary,
                                     get_pools,
                                     get_stats,
                                     )
from app.pycgminer.pycgminer import CgminerAPI

import time
import threading
import config
from functools import wraps

from miner_adapter import detect_model, get_miner_instance, update_unit_and_value
from mail_sender import MinerReporter
from miners_profit import get_miners_profit



def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == config.BASIC_AUTH_USER and password == config.BASIC_AUTH_PWD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def miners():
    # Init variables
    start = time.clock()
    miners = Miner.query.all()
    models = MinerModel.query.all()
    active_miner_instances = []
    inactive_miners = []
    # map is lazy initialized
    total_hash_rate_per_model = {}
    errors = False

    for miner in miners:
        miner_instance_list = get_miner_instance(miner)

        # if miner not accessible
        if not miner_instance_list:
            errors = True
            inactive_miners.append(miner)
        else:
            for miner_instance in miner_instance_list:
                if not miner.model.model in total_hash_rate_per_model.keys():
                    total_hash_rate_per_model[miner.model.model] = {
                        "value": 0, "unit": "<EMPTY>"}

                total_hash_rate_per_model[miner.model.model]["value"] += miner_instance.hashrate_value
                total_hash_rate_per_model[miner.model.model]["unit"] = miner_instance.hashrate_unit
                active_miner_instances.append(miner_instance)

                # Log warnings
                for message in miner_instance.verboses:
                    logger.info(message)
                    flash(message, "verbose")
                for message in miner_instance.warnings:
                    logger.warning(message)
                    flash(message, "warning")
                    errors = True
                for message in miner_instance.errors:
                    logger.warning(message)
                    flash(message, "error")
                    errors = True

    # Flash success/info message
    if not miners:
        error_message = "[INFO] No miners added yet. Please add miners using the above form."
        logger.info(error_message)
        flash(error_message, "info")
    elif not errors:
        error_message = "[INFO] All miners are operating normal. No errors found."
        logger.info(error_message)
        flash(error_message, "info")

    # Convert the total_hash_rate_per_model into a data structure that the template can
    # consume.
    total_hash_rate_per_model_temp = {}
    for key in total_hash_rate_per_model:
        value, unit = update_unit_and_value(
            total_hash_rate_per_model[key]["value"], total_hash_rate_per_model[key]["unit"])
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
@requires_auth
def add_miner():
    miner_ip = request.form['ip']

    model_name = detect_model(miner_ip)
    model = MinerModel.query.filter_by(model=model_name).first()
    miner_remarks = request.form['remarks']

    # exists = Miner.query.filter_by(ip="").first()
    # if exists:
    #    return "IP Address already added"

    try:
        miner = Miner(ip=miner_ip, model_id=model.id,
                      remarks=miner_remarks)
        db.session.add(miner)
        db.session.commit()
        flash("Miner with IP Address {} added successfully".format(
            miner.ip), "success")
    except IntegrityError as e:
        db.session.rollback()
        flash("IP Address {} already added".format(miner_ip), "error")

    return redirect(url_for('miners'))


@app.route('/delete/<id>')
@requires_auth
def delete_miner(id):
    miner = Miner.query.filter_by(id=int(id)).first()
    db.session.delete(miner)
    db.session.commit()
    return redirect(url_for('miners'))

@app.route('/restart/<id>')
@requires_auth
def restart_miner(id):
    miner = Miner.query.filter_by(id=int(id)).first()
    cgminer = CgminerAPI(host=miner.ip)
    output = cgminer.restart()
    return redirect(url_for('miners'))

@app.route('/<ip>/summary')
@requires_auth
def summary(ip):
    output = get_summary(ip)
    return jsonify(output)


@app.route('/<ip>/pools')
@requires_auth
def pools(ip):
    output = get_pools(ip)
    return jsonify(output)


@app.route('/<ip>/stats')
@requires_auth
def stats(ip):
    output = get_stats(ip)
    return jsonify(output)

@app.route('/profits')
@requires_auth
def profits():
    # Init variables
    start = time.clock()
    miners_profit = get_miners_profit()
    end = time.clock()
    loading_time = end - start
    return render_template('myprofits.html',
                           version=__version__,
                           miners_profit=miners_profit,
                           loading_time=loading_time,
                           )

@app.before_first_request
def activate_job():
    def run_job():
        watch_dog = MinerReporter()
        while True:
            for miner in Miner.query.all():
                miner_instance_list = get_miner_instance(miner)
                for miner_instance in miner_instance_list:
                    print("Checking instance: {} - {}".format(miner_instance.miner.ip,
                                                              "OK" if watch_dog.check_health(miner_instance) else "ERROR"))
            print("Sleeping for 5min")
            time.sleep(5 * 60)

    thread = threading.Thread(target=run_job)
    thread.start()
