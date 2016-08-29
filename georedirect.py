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

    cfgdir = os.path.dirname(os.path.abspath(__file__))

    # Load GeoIP object
    GEOIP_FILE = cfgdir + '/GeoIP.dat'
    try:
        CONFIG['geoip'] = pygeoip.GeoIP(GEOIP_FILE)
    except IOError:
        GEOIP_FILE = '/usr/share/GeoIP/GeoIP.dat'
        CONFIG['geoip'] = pygeoip.GeoIP(GEOIP_FILE)

    # Create temporary server offline db
    CONFIG['offline'] = []

    # Load configuration
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
    nexi = CONFIG['nexi'].iteritems()
    online_nexi = [n for n in nexi if not n[0] in CONFIG['offline']]
    for server, codes in online_nexi:
        if country in codes:
            return True, country, server
    return False, country, random.choice(online_nexi)[0]


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
