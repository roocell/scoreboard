#!/usr/bin/python3

import os, time, sys, datetime
import logging
import atexit
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask import Response, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import pygame
import alsaaudio
import os

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
if async_mode == 'eventlet':
    # we want to use eventlet (otherwise https certfile doens't work on socketio)
    # but we're using a python thread - so we have to monkeypatch
    import eventlet
    eventlet.monkey_patch()
socketio = SocketIO(app, async_mode=async_mode)

# data
homescore = 0
awayscore = 0
clock = 20*60
paused = 1
consecutive_pts_home = 0
consecutive_pts_away = 0

def getData():
    return { 
        'data' : {
            'home' : homescore,
            'away' : awayscore,
            'clock' : clock,
            'paused' : paused,
        }
    }


def timeout():
    log.debug("timeout")

@app.route('/')
def index():
    return render_template('index.html', http=http, mode='controller');

@app.route('/scoreboard')
def scoreboard():
    return render_template('index.html', http=http, mode='scoreboard');

@app.route('/adjustScore', methods = ['POST', 'GET'])
def adjustScore():
    global homescore
    global awayscore
    global consecutive_pts_home, consecutive_pts_away
    log.debug("adjustScore")
    diff = int(request.args.get('diff'))
    if request.method == 'GET':
        team = request.args.get('team')
        if team == 'home':
            homescore = homescore + diff
            if (diff == 3):
                consecutive_pts_home += 1
                consecutive_pts_away = 0
        elif team == 'away':
            awayscore = awayscore + diff
            if (diff == 3):
                consecutive_pts_away += 1
                consecutive_pts_home = 0
        else:
            log.debug("adjustScore ERROR")

        socketio.emit('data', getData(), namespace='/status', broadcast=True)
        if (consecutive_pts_home >= 3 or consecutive_pts_away >= 3):
            pygame.mixer.Sound("/home/pi/scoreboard/on-fire.wav").play()
            consecutive_pts_home = 0
            consecutive_pts_away = 0

    else:
        log.debug("adjustScore ERR")
    return "OK"

@app.route('/pauseResume', methods = ['POST', 'GET'])
def pauseResume():
    global paused
    if request.method == 'GET':
        if int(request.args.get('paused')) == 1:
            log.debug("pause")
            paused = 1
        else:
            log.debug("resume")
            paused = 0
    else:
        log.debug("pauseResume ERR")
    # emit pause state to other clients
    socketio.emit('data', getData(), namespace='/status', broadcast=True)
    return "OK"

@app.route('/adjustClock', methods = ['POST', 'GET'])
def adjustClock():
    global clock
    log.debug("adjustClock")
    if request.method == 'GET':
        clock = int(request.args.get('value'))
    else:
        log.debug("adjustClock ERR")
    # emit clock to other clients
    socketio.emit('clock', getData(), namespace='/status', broadcast=True)
    return "OK"

@socketio.on('connect', namespace='/status')
def connect():
    log.debug("flask client connected")
    # always emit at connect so client can update
    socketio.emit('data', getData(), namespace='/status', broadcast=True)
    socketio.emit('clock', getData(), namespace='/status', broadcast=True)
    return "OK"

@socketio.on('disconnect', namespace='/status')
def test_disconnect():
    log.debug('flask client disconnected')

def loop(socketio):
    global clock
    while True:
        #log.debug("mainloop")
        time.sleep(1)
        if paused:
            continue
        if clock > 0:
            clock = clock - 1
            log.debug("sending clock")
            socketio.emit('clock', getData(), namespace='/status', broadcast=True)
            if clock == 0:
                pygame.mixer.Sound("/home/pi/scoreboard/buzzer.wav").play()
            elif clock < 10:
                pygame.mixer.Sound("/home/pi/scoreboard/beep2.wav").play()

def cleanup():
    log.debug("cleaning up")

if __name__ == '__main__':
    atexit.register(cleanup)
    t = threading.Thread(target=loop, args=(socketio,))
    t.start()

    scanCards = alsaaudio.cards()
    log.debug("cards: {}".format(scanCards))
    for card in scanCards:
        scanMixers = alsaaudio.mixers(scanCards.index(card))
        log.debug("mixers: {}".format(scanMixers))

    #m = alsaaudio.Mixer('PCM')
    #m.setvolume(90) # range seems to be non-linear

    pygame.mixer.init(buffer=2048)

    log.debug("restarting kiosk")
    os.system("sudo systemctl restart kiosk.service")
    
    log.debug("starting HTTP")
    socketio.run(app,
        debug=True, host='0.0.0.0', port=80, use_reloader=False)
