from flask import Blueprint, jsonify
from lib.pycgminer import (get_summary,
                           get_pools,
                           get_stats,
                           )

antminer_json = Blueprint('antminer_json',
                          __name__,
                          template_folder='../templates',
                          )


@antminer_json.route('/<ip>/summary')
def summary(ip):
    output = get_summary(ip)
    return jsonify(output)


@antminer_json.route('/<ip>/pools')
def pools(ip):
    output = get_pools(ip)
    return jsonify(output)


@antminer_json.route('/<ip>/stats')
def stats(ip):
    output = get_stats(ip)
    return jsonify(output)
