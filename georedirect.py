#!/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ts=4 sw=4 sts=4 sta tw=80 cc=81:

import time, os
from threading import Timer
import pygeoip, random, json, urllib3
from flask import Flask, render_template, request, Response, redirect
app = Flask(__name__)

CONFIG = {}

def setup():
    random.seed()

    # Load GeoIP object
    GEOIP_FILE = '/usr/share/GeoIP/GeoIP.dat'
    CONFIG['geoip'] = pygeoip.GeoIP(GEOIP_FILE)

    # Create temporary server offline db
    CONFIG['offline'] = []

    # Load configuration
    cfgdir = os.path.dirname(os.path.abspath(__file__))
    with open(cfgdir + '/nexus.opencast.org.json') as f:
        CONFIG['nexi'] = json.load(f)

    # Start status check thread
    statuscheck()


def online(url):
    http = urllib3.PoolManager()
    try:
        r = http.request('GET', url)
    except urllib3.exceptions.MaxRetryError as e:
        return False
    return r.status == 200


def statuscheck():
    t = Timer(60.0, statuscheck)
    t.daemon = True
    t.start()
    offline = []
    for nexus in CONFIG['nexi'].keys():
        if not online(nexus):
            offline.append(nexus)
    CONFIG['offline'] = offline


def shorten_nexus(nexus):
    nexus = nexus.split('//')[-1]
    nexus = nexus.split(':')[0]
    return nexus


def select(addr):
    country = CONFIG['geoip'].country_code_by_addr(addr)
    for server, codes in CONFIG['nexi'].iteritems():
        if server in CONFIG['offline']:
            continue
        if country in codes:
            return True, country, server
    return False, country, random.choice(CONFIG['nexi'].keys())


@app.route("/")
def home():

    geoselect, country, server = select(request.remote_addr)

    return render_template('home.html', country=country, geoselect=geoselect,
            server=server, nexi=CONFIG['nexi'], shorten=shorten_nexus,
            offline=CONFIG['offline'])


@app.route("/nexus/")
@app.route("/nexus/<path:path>")
def nexus(path=''):

    geoselect, country, server = select(request.remote_addr)
    if not server.endswith('/'):
        server += '/'

    return redirect(server + path, code=302)



setup()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
