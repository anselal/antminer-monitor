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
from app import app, db, logger, __version__, last_run_time, last_status_is_ok
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
import jinja2
import json

from miner_adapter import detect_model, get_miner_instance, update_unit_and_value
from mail_sender import send_email
from miners_profit import get_miners_profit

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return (config.BASIC_AUTH_USER is None or
        (username == config.BASIC_AUTH_USER and password == config.BASIC_AUTH_PWD))


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
    usd_per_kwh = float(request.form.get('usd_per_kwh', 0.11))
    # Init variables
    start = time.clock()
    miners_profit = get_miners_profit(usd_per_kwh)
    loading_time = time.clock() - start
    return render_template('myprofits.html',
                           version=__version__,
                           data=miners_profit,
                           loading_time=loading_time,
                           usd_per_kwh=usd_per_kwh)

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

@app.route('/miners_status', methods=['GET', 'POST'])
@requires_auth
def status():
    global index_add_counter
    global last_run_time
    if last_status_is_ok:
        return json.dumps({ "status": "ok", "last_run": int(last_run_time) }), 200
    else:
        return json.dumps({ "error": "error in last validation" }), 500
            
@app.before_first_request
def activate_job():
    def run_job():
        global index_add_counter
        global last_run_time
        while True:
            active_miner_instances = []
            inactive_miners = []
            messages = []
            for miner in Miner.query.all():
                miner_instance_list = get_miner_instance(miner)
                if not miner_instance_list:
                    inactive_miners.append(miner)
                    messages.append(
                        ('error', "[ERROR] {} not accessible".format(miner.ip)))
                else:
                    for miner_instance in miner_instance_list:
                        for error in miner_instance.errors:
                            messages.append(('error', error))
                        for warning in miner_instance.warnings:
                            messages.append(('warning', warning))
                        active_miner_instances.append(miner_instance)
            last_status_is_ok = len(messages) == 0
            last_run_time = time.time()
            if not last_status_is_ok:
                body_html = (render_without_request("inactive_miners.html", inactive_miners=inactive_miners) +
                    render_without_request("active_miners.html", active_miner_instances=active_miner_instances) +
                    render_without_request("messages.html", messages=messages))
                body_plain = "Error founds while monitoring. Please go to {}\n".format(
                    config.DOMAIN_ADDR)
                send_email(config.GMAIL_USER, config.GMAIL_PWD,
                           config.EMAIL_TO, "Antmonitor Alert", body_html, body_plain)
            time.sleep(5 * 60)

    thread = threading.Thread(target=run_job)
    thread.start()
