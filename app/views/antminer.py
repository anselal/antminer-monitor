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
from app.models import Miner, MinerModel, MinerEvent
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
                           generated_time=time.strftime(
                               "%d/%b %H:%M:%S", time.localtime()),
                           is_request=True)


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
@requires_auth
def add_miner():
    miner_ip = request.form['ip']

    model = None
    try:
        model = detect_model(miner_ip)
    except Exception as e:
        logger.error(
            "Error while detecting miner. message: {}".format(e.message))
        flash(message=e.message, category="error")

    if not model is None:
        try:
            miner_remarks = request.form['remarks']
            miner = Miner(ip=miner_ip, model_id=model.id,
                          remarks=miner_remarks, count=1)
            db.session.add(miner)
            db.session.commit()
            flash("Miner with IP Address {} added successfully".format(
                miner.ip), "info")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(
                "Error while adding miner. Message: {}".format(e.message))
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
    status = cgminer.restart()
    if status['STATUS'] == "RESTART":
        flash("Miner {} restarted successfully".format(miner.ip), "warning")
    else:
        flash("Error while restarting {} - {}".format(miner.ip, json.dumps(status)))
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
    usd_per_kwh = float(request.form.get('usd_per_kwh', 0.09))
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
    # Add 10s for slack.
    if time.time() - last_run_time >= AGENT_INTERVAL_SECS + 10 or not last_status_is_ok:
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
    for miner in miners:
        try:
            url = "http://{}".format(miner.ip)
            r = requests.get(url, timeout=timeout)
            if r.status_code >= 500:
                failed_miners.append(miner)
        except Exception as e:
            logger.warning("Error while connecting to {}".format(e.message))
            failed_miners.append(miner)

    return failed_miners


def log_miner_event(miner, event_type, message):
    try:
        logger.debug("Miner:{} type:{} message:{}".format(miner.ip, event_type, message))
        miner_event = MinerEvent(
            miner_id=miner.id, event_type=event_type, message=message)
        db.session.add(miner_event)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logger.error("Error while logging event. Message:{}".format(e.message))


@app.before_first_request
def activate_job():
    def run_job():
        global last_run_time
        global last_status_is_ok
        global AGENT_INTERVAL_SECS
        lightweight_last_run_time = 0
        lightweight_interval_secs = 5
        last_email_message = None
        while True:
            try:
                messages = []
                # Light check (HTTP connect)
                miners = Miner.query.all()
                if last_run_time != 0 and time.time() - lightweight_last_run_time >= lightweight_interval_secs:
                    logger.debug("Lightweight HTTP checks in progress...")
                    inactive_miners = try_http_connect(
                        miners=miners, timeout=5)
                    for inactive_miner in inactive_miners:
                        msg = "Miner {} not accessible".format(
                            inactive_miner.ip)
                        messages.append(("error", msg))
                        log_miner_event(inactive_miner, "error", msg)
                    lightweight_last_run_time = time.time()

                # Expensive check (CGMiner API)
                active_miner_instances = []
                if len(messages) == 0 and time.time() - last_run_time >= AGENT_INTERVAL_SECS:
                    logger.info("CGMiner API checks in progress...")
                    for miner in miners:
                        miner_status = get_miner_status(miner)
                        if not miner_status:
                            # Log event
                            messages.append(
                                ("error", "Miner {} not accessible".format(miner.ip)))
                            log_miner_event(
                                miner, "error", "Miner not accessible")
                        else:
                            for miner_instance in miner_status.miner_instance_list:
                                active_miner_instances.append(miner_instance)
                            for message in miner_status.errors:
                                messages.append(("error", message))
                                log_miner_event(miner, "error", message)
                            for message in miner_status.warnings:
                                messages.append(('warning', message))
                                log_miner_event(miner, "error", message)

                    # Update last run time.
                    last_run_time = time.time()

                # Update status
                last_status_is_ok = len(messages) == 0
                if not last_status_is_ok:
                    body_html = (render_without_request("active_miners.html", active_miner_instances=active_miner_instances) +
                                 render_without_request("messages.html", messages=messages))
                    body_plain = "Error founds while monitoring. Please go to {}\n".format(
                        config.DOMAIN_ADDR)
                    # Just send the error email if it changed
                    if last_email_message <> body_html:
                        for i in range(0, 10):
                            if send_email(config.GMAIL_USER, config.GMAIL_PWD, config.EMAIL_TO, "Monitor Alert", body_html, body_plain):
                                last_email_message = body_html
                                break
                            logger.warn(
                                "Failure sending email, retrying... #{}".format(i))
                    else:
                        logger.debug("Email the same as previous... skipping...")
                else:
                    last_email_message = None
            except Exception as e:
                logger.error("Error. Message:{}", e.message)
                last_status_is_ok = False
            time.sleep(lightweight_interval_secs)

    thread = threading.Thread(target=run_job)
    thread.start()
