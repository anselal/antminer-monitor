from flask import jsonify
from app import app


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