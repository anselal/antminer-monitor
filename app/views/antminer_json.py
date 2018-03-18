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
