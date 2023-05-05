#!/usr/bin/python3

import os, time, sys, datetime
import logging
import atexit
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask import Response, redirect, url_for
from flask_socketio import SocketIO, emit
import threading


# create logger
log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# create flask and socket
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

#http = "https://"
http = "http://"
async_mode='eventlet'
socketio = SocketIO(app, async_mode=async_mode)


# data
homescore = 0
awayscore = 0
clock = 0

def getData():
    return { 
        'data' : {
            'home' : homescore,
            'away' : awayscore,
            'clock' : clock,
        }
    }


def timeout():
    log.debug("timeout")

@app.route('/')
def index():
    return render_template('index.html', http=http);

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html', http=http);

@app.route('/adjustScore', methods = ['POST', 'GET'])
def adjustScore():
    global homescore
    global awayscore
    log.debug("adjustScore")
    if request.method == 'GET':
        team = request.args.get('team')
        diff = request.args.get('diff')
        if team == 'home':
            homescore = homescore + int(diff)
        elif team == 'away':
            awayscore = awayscore + int(diff)
        else:
            log.debug("adjustScore ERROR")
        socketio.emit('status', getData(), namespace='/status', broadcast=True)
    else:
        log.debug("adjustScore ERR")
    return "OK"

@socketio.on('connect', namespace='/status')
def connect():
    log.debug("flask client connected")
    # always emit at connect so client can update
    #socketio.emit('status', getStatus(), namespace='/status', broadcast=True)
    return "OK"

@socketio.on('disconnect', namespace='/status')
def test_disconnect():
    log.debug('flask client disconnected')

def loop(socketio):
    while True:
        log.debug("mainloop")
        time.sleep(10)

def cleanup():
    log.debug("cleaning up")

if __name__ == '__main__':
    atexit.register(cleanup)
    t = threading.Thread(target=loop, args=(socketio,))
    t.start()
    log.debug("starting HTTP")

    socketio.run(app,
        debug=True, host='0.0.0.0', port=80, use_reloader=False)
