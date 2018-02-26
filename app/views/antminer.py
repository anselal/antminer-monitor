import json
import threading
import time
from functools import wraps

import jinja2
import requests
from flask import (Response, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

import config
from app import (AGENT_INTERVAL_SECS, __version__, app, db, last_run_time,
                 last_status_is_ok, logger)
from app.models import Miner, MinerModel, Settings
from app.pycgminer.pycgminer import CgminerAPI
from app.views.antminer_json import get_pools, get_stats, get_summary
from mail_sender import send_email
from miner_adapter import detect_model, get_miner_status, update_unit_and_value
from miners_profit import get_miners_profit


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return (username == config.BASIC_AUTH_USER and password == config.BASIC_AUTH_PWD)

def auth_enabled():
    return not config.BASIC_AUTH_USER is None


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if auth_enabled():
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
    active_miner_instances = []
    inactive_miners = []
    # map is lazy initialized
    total_hash_rate_per_model = {}
    errors = False

    for miner in miners:
        miner_status = get_miner_status(miner)

        # if miner not accessible
        if not miner_status:
            errors = True
            inactive_miners.append(miner)
        else:
            for miner_instance in miner_status.miner_instance_list:
                if not miner.model.model in total_hash_rate_per_model.keys():
                    total_hash_rate_per_model[miner.model.model] = {
                        "value": 0, "unit": "<EMPTY>"}

                total_hash_rate_per_model[miner.model.model]["value"] += miner_instance.hashrate_value
                total_hash_rate_per_model[miner.model.model]["unit"] = miner_instance.hashrate_unit
                active_miner_instances.append(miner_instance)

            # Log warnings
            for message in miner_status.debugs:
                flash(message, "debug")
            for message in miner_status.warnings:
                logger.warning(message)
                flash(message, "warning")
                errors = True
            for message in miner_status.errors:
                logger.warning(message)
                flash(message, "error")
                errors = True

    # Flash success/info message
    if not miners:
        error_message = "[INFO] No miners added yet. Please add miners using the above form."
        flash(error_message, "info")
    elif not errors:
        error_message = "[INFO] All miners are operating normal. No errors found."
        flash(error_message, "info")

    # Convert the total_hash_rate_per_model into a data structure that the template can
    # consume.
    total_hash_rate_per_model_temp = {}
    for key in total_hash_rate_per_model:
        value, unit = update_unit_and_value(
            total_hash_rate_per_model[key]["value"], total_hash_rate_per_model[key]["unit"])
        total_hash_rate_per_model_temp[key] = "{:3.2f} {}".format(value, unit)

    end = time.clock()
    models = MinerModel.query.all()
    loading_time = end - start
    return render_template('myminers.html',
                           version=__version__,
                           models=models,
                           active_miner_instances=active_miner_instances,
                           inactive_miners=inactive_miners,
                           total_hash_rate_per_model=total_hash_rate_per_model_temp,
                           loading_time=loading_time,
                           is_request=True)


@app.route('/add', methods=['POST'])
@requires_auth
def add_miner():
    miner_ip = request.form['ip']

    model = None
    try:
        model = detect_model(miner_ip)
    except Exception as e:
        flash(e.message, "error")

    if not model is None:
        try:
            miner_remarks = request.form['remarks']
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
    logger.info("Restarted miner: {}".format(str(output)))
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


@app.route('/profits', methods=['GET', 'POST'])
@requires_auth
def profits():
    # Init variables
    usd_per_kwh = float(request.form.get('usd_per_kwh', 0.11))
    start = time.clock()
    miners_profit = get_miners_profit(usd_per_kwh)
    loading_time = time.clock() - start
    return render_template('myprofits.html',
                           version=__version__,
                           data=miners_profit,
                           loading_time=loading_time,
                           usd_per_kwh=usd_per_kwh)


@app.route('/miners_status', methods=['GET'])
@requires_auth
def status():
    global last_run_time
    global last_status_is_ok
    global AGENT_INTERVAL_SECS
    if time.time() - last_run_time >= AGENT_INTERVAL_SECS:
        return abort(500)
    else:
        return jsonify({"last_run_time": last_run_time})

def render_without_request(template_name, **template_vars):
    """
    Usage is the same as flask.render_template:

    render_without_request('my_template.html', var1='foo', var2='bar')
    """
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('app', 'templates')
    )
    template = env.get_template(template_name)
    return template.render(**template_vars)

def try_http_connect(miners, timeout):
    failed_miners = []
    logger.info("Attempting to connect to all miners through HTTP")
    for miner in miners: 
        try:
            url = "http://{}".format(miner.ip)
            r = requests.get(url, timeout=timeout)
            if r.status_code >= 500:
                failed_miners.append(miner)
        except Exception as e:
            logger.error(e)
            failed_miners.append(miner)

    return failed_miners

@app.before_first_request
def activate_job():
    def run_job():
        global last_run_time
        global last_status_is_ok
        global AGENT_INTERVAL_SECS
        lightweight_last_run_time = 0
        lightweight_interval_secs = 15
        while True:
            try:
                active_miner_instances = []
                inactive_miners = []
                messages = []

                # Light check (HTTP connect)
                if last_run_time != 0 and time.time() - lightweight_last_run_time >= lightweight_interval_secs:
                    miners = Miner.query.all()
                    inactive_miners = try_http_connect(miners=miners,timeout=5)
                    if inactive_miners:
                        messages.append(('error', "Some servers cannot be contacted through HTTP connect"))
                        break
                    lightweight_last_run_time = time.time()

                # Expensive check (CGMiner API)
                if not messages and time.time() - last_run_time >= AGENT_INTERVAL_SECS:
                    logger.info("CGMiner API checks in progress...")
                    miners = Miner.query.all()
                    for miner in miners:
                        miner_status = get_miner_status(miner)
                        if not miner_status:
                            inactive_miners.append(miner)
                            messages.append(
                                ('error', "[ERROR] {} not accessible".format(miner.ip)))
                        else:
                            for miner_instance in miner_status.miner_instance_list:
                                active_miner_instances.append(miner_instance)
                            for error in miner_status.errors:
                                messages.append(('error', error))
                            for warning in miner_status.warnings:
                                messages.append(('warning', warning))

                    # Update last run time.
                    lightweight_last_run_time = last_run_time = time.time()

                    # Update status
                    last_status_is_ok = len(messages) == 0
                    if not last_status_is_ok:
                        body_html = (render_without_request("inactive_miners.html", inactive_miners=inactive_miners) +
                            render_without_request("active_miners.html", active_miner_instances=active_miner_instances) +
                            render_without_request("messages.html", messages=messages))
                        body_plain = "Error founds while monitoring. Please go to {}\n".format(
                            config.DOMAIN_ADDR)
                        send_email(config.GMAIL_USER, config.GMAIL_PWD,
                                config.EMAIL_TO, "Monitor Alert", body_html, body_plain)
            except Exception as e:
                logger.error(e)
            time.sleep(lightweight_interval_secs)

    thread = threading.Thread(target=run_job)
    thread.start()
