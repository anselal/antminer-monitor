from flask import jsonify
from app.pycgminer import CgminerAPI
from app import app


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