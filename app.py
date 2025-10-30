#!/usr/bin/python3

import os, time, sys, datetime
from logger import log as log
import atexit
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask import Response, redirect, url_for
from flask_socketio import SocketIO, emit
import threading
import pygame
import alsaaudio

import board
import neopixel
import neo7seg
import asyncio

backupfile = '/home/pi/scoreboard/data.txt'

# data
homescore = 0
awayscore = 0
clock = 20*60
paused = 1
consecutive_pts_home = 0
consecutive_pts_away = 0

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB
num_pixels = 7*10*4
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=ORDER)
digit = neo7seg.Neo7Seg(pixels, 0, [10,10,10,10]) # 4 digits, 4 with 10-led segments
digit.set(0,"----")

def replace_leading_zero(source, char=" "):
    stripped = source.lstrip('0')
    result = char * (len(source) - len(stripped)) + stripped
    if result.isspace():
        result = " 0"  # assume 2 digit number
    return result

def getData():
    return { 
        'data' : {
            'home' : homescore,
            'away' : awayscore,
            'clock' : clock,
            'paused' : paused,
        }
    }

def handle_exception(exc_type, exc_value, exc_traceback):
    global clock, homescore, awayscore, paused
    log.debug(exc_value)
    log.debug(exc_traceback)
    # we're crashing - store the score and time to disk
    # so it comes back up with the same data
    with open(backupfile, 'w') as f:
        log.debug("backing up data")
        f.write("clock:" + str(clock) + "\n")
        f.write("homescore:" + str(homescore) + "\n")
        f.write("awayscore:" + str(awayscore) + "\n")
        f.write("paused:" + str(paused) + "\n")
    exit(-1)

def handle_thread_exception(args):
    handle_exception(args.exc_type, args.exc_value, args.exc_traceback)

def load_saved_data():
    global clock, homescore, awayscore, paused
    try:
        with open(backupfile, 'r') as f:
            log.debug("retrieving backup data")
            for line in f:
                print(line)
                key, value = line.strip().split(':')
                if (key == "clock"):
                    clock = int(value)
                    log.debug("restored clock is: {}".format(clock))
                if (key == "homescore"): homescore = int(value)
                if (key == "awayscore"): awayscore = int(value)
                if (key == "paused"): paused = int(value)
        # remove file so we do this only if it crashed
        if os.path.exists(backupfile):
            os.remove(backupfile)
    except FileNotFoundError:
        log.debug("backupfile not found.")

# Set up the global exception handler
sys.excepthook = handle_exception
threading.excepthook = handle_thread_exception

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

def timeout():
    log.debug("timeout")

@app.route('/')
def index():
    return render_template('index.html', http=http, mode='controller');

@app.route('/scoreboard')
def scoreboard():
    return render_template('index.html', http=http, mode='scoreboard');

def setScore():
    homescorestr = str(min(homescore, 99)).zfill(2)
    awayscorestr = str(min(awayscore, 99)).zfill(2)
    homescorestr = replace_leading_zero(homescorestr)
    awayscorestr = replace_leading_zero(awayscorestr)
    digit.set(0, homescorestr, neo7seg.red)
    digit.set(2, awayscorestr, neo7seg.blue)

@app.route('/adjustScore', methods = ['POST', 'GET'])
def adjustScore():
    global homescore
    global awayscore
    global consecutive_pts_home, consecutive_pts_away
    #log.debug("adjustScore")
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

    # change to string and replace leading 0 with space
    setScore()

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
            # when we resume/start show the score first
            setScore()
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
        time.sleep(1)
        if paused:
            # pause with score
            setScore()
            continue

        # to test crash recovery
        # this will crash once, reload and continue couting down
        # if (clock == 19*60+57):
        #     clock = 19*60+55
        #     raise ValueError("crashing on purpose")

        if clock > 0:
            clock = clock - 1
            # clock is in seconds here - but we want to display minutes/seconds
            minutes = str(min(int(clock / 60), 99)).zfill(2) # max out at 99 because we have only 2 digits
            seconds = str(int(clock % 60)).zfill(2)
            clockstr = minutes + seconds
            # replace leading zero with space (easier to read)
            clockstr = replace_leading_zero(clockstr)
            #log.debug(clockstr)
            socketio.emit('clock', getData(), namespace='/status', broadcast=True)
            if clock == 0:
                pygame.mixer.Sound("/home/pi/scoreboard/buzzer.wav").play()
            elif clock < 10:
                pygame.mixer.Sound("/home/pi/scoreboard/beep2.wav").play()

            # every 10 seconds flash the score in red/blue
            if (clock % 10) == 0:
                    setScore()
            else:
                digit.set(0, clockstr)
            
        else:
            # end with score
            setScore()


def cleanup():
    log.debug("cleaning up")
    # turn the LEDs off
    pixels.fill((0,0,0))
    pixels.show()

if __name__ == '__main__':
    atexit.register(cleanup)
    load_saved_data()
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

    # startup sequence
    # for i in range(1,4):
    #     char = str(i)
    #     digit.set(0, char+char+char+char+char+char+char+char)
    #     pygame.mixer.Sound("/home/pi/scoreboard/beep2.wav").play()
    #     time.sleep(1)

    log.debug("starting HTTP for scoreboard")
    socketio.run(app,
        debug=True, host='0.0.0.0', port=80, use_reloader=False)
