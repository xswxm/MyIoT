#!/usr/bin/python
# -*- coding: UTF-8 -*-

# SSL
import eventlet
eventlet.monkey_patch()
from OpenSSL import SSL, crypto

import os, time, threading
import smbus
import random
import RPi.GPIO as GPIO

# Flask
from flask import Flask, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Modules for devices
from devices.device import RandomValue, Device
from devices.switch import Switch, BreathLight, SOSLight
from devices.seekbar import PWMSignal
from devices.value import BH1750FVI, CPUTemp, DH11Temp, DH11Humidity
from devices.button import Button

# Configuration: read and write configurations
import utils.config as Config

# Debug
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Initialize syncinterval
syncinterval = int(Config.ReadCfg('SYSTEM', 'syncinterval'))


# idInt: id for internal devices
# idDiff: id boundary for internal devices and external devices
# idExt: id for external devices
idInt = 1000;
idDiff = 2000;
idExt = idDiff

# device list, including internal devices and external devices
devices = []

# Initialize Devices
def devicesInit():
    device = {}
    deviceList = Config.ReadDevices()
    for i in xrange(len(deviceList)):
        device = deviceList[i]
        title = device['title']
        type = device['type']
        if 'port' in device:
            port = int(device['port'])
        elif 'address' in device:
            address = int(device['address'], 16)
        # Add device to devices
        if type == 'Switch':
            devices.append(Switch(title, port, idInt + i))
        elif type == 'Button':
            devices.append(Button(title, port, idInt + i))
        elif type == 'PWMSignal':
            devices.append(PWMSignal(title, port, idInt + i))
        elif type == 'BreathLight':
            devices.append(BreathLight(title, port, idInt + i))
        elif type == 'SOSLight':
            devices.append(SOSLight(title, port, idInt + i))
        elif type == 'DH11Temp':
            devices.append(DH11Temp(title, port, idInt + i))
        elif type == 'DH11Humidity':
            devices.append(DH11Humidity(title, port, idInt + i))
        elif type == 'BH1750FVI':
            devices.append(BH1750FVI(title, address, idInt + i))
        elif type == 'CPUTemp':
            devices.append(CPUTemp(title, idInt + i))
        elif type == 'RandomValue':
            devices.append(RandomValue(title, idInt + i))


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


# Generated events to clients in background
def background_thread():
    global syncinterval
    while True:
        for i in range(syncinterval):
            if i < syncinterval:
                socketio.sleep(1)
            else:
                break
        # socketio.sleep(syncinterval)
        message = {}
        logging.debug('-------------------Background Thread-----------------------------')
        for i in xrange(len(devices)):
            deviceType = devices[i].type
            if (deviceType == 'Value' or deviceType == 'SeekBar'):
                try:
                    if (devices[i].id <= idDiff):
                        # deviceDesc = devices[i].description()
                        message['id'] = devices[i].id
                        message['type'] = devices[i].type
                        message['value'] = devices[i].getValue()
                        logging.debug(message)
                        # message = deviceDesc
                        socketio.emit('set', message, broadcast = True, namespace='/devices')
                        # socketio.emit('setDevice', message, namespace='/')
                    else:
                        socketio.emit('set', message, room = devices[i].sid, namespace='/devices')
                except Exception as e:
                    logging.debug(e)


# Get the info of all devices and sent them back to the client
@socketio.on('getAll', namespace='/devices')
def get_alldevices():
    # An example of the received message: {'title': 'Green LED', 'type': 'Switch', 'value': False, 'id': 1000}
    try:
        message = {}
        logging.debug('-------------------get All Devices---------------------------------')
        for i in xrange(len(devices)):
            message = devices[i].description()
            logging.debug(message)
            emit('add', message)
    except Exception as e:
        logging.debug(e)


# Add a device and send its info to all clients
@socketio.on('add', namespace='/devices')
def add_device(message):
    try:
        deviceTitle = message['title']
        deviceType = message['type']
        deviceValue = message['value']
        idExt += 1
        # Use sid as the room no.
        join_room(request.sid)
        devices.append(Device(deviceTitle, deviceType, deviceValue, idExt))
        message['id'] = idExt
        emit('add', message, broadcast = True)
    except Exception as e:
        logging.debug(e)


# Get the info of one specific device and sent back to the client
@socketio.on('get', namespace='/devices')
def get_device(message):
    # An example of the received message: {'id': 1000}
    # An example of the sent message: {'id': 1000, 'type': 'Switch', 'value': False}
    try:
        deviceID = message['id']
        for i in xrange(len(devices)):
            if (devices[i].id == deviceID):
                if deviceID <= idDiff:
                    message['type'] = devices[i].type
                    message['value'] = devices[i].getValue()
                    emit('set', message)
                else:
                    emit('get', message, room = devices[i].sid)
    except Exception as e:
        logging.debug(e)


# Set the value of a specific device
@socketio.on('set', namespace='/devices')
def broadcast_message(message):
    # an example of the received message: {'id': 1000, 'value': false}
    # An example of the sent message: {'id': 1000, 'type': 'Switch', 'value': False}
    try:
        deviceID = message['id']
        for i in xrange(len(devices)):
            if (devices[i].id == deviceID):
                if deviceID <= idDiff:
                    # Reinitialize the device if it is a thread
                    # Thread: This method will raise a RuntimeError if called more than once on the same thread object.
                    if devices[i].isThread:
                        if not devices[i].isAlive():
                            if devices[i].cname == "BreathLight":
                                devices[i] = BreathLight(devices[i].title, devices[i].port, deviceID)
                            if devices[i].cname == "SOSLight":
                                devices[i] = SOSLight(devices[i].title, devices[i].port, deviceID)
                            if devices[i].cname == "PWMSignal":
                                devices[i] = PWMSignal(devices[i].title, devices[i].port, deviceID)
                    deviceValue = message['value']
                    message['type'] = devices[i].type
                    message['value'] = devices[i].setValue(deviceValue)
                    emit('set', message, broadcast=True)
                else:
                    emit('set', message, room = devices[i].sid)
                    # request.namespace.emit('message', "somthing here")
    except Exception as e:
        logging.debug(e)


# @app.route('/')
# def index():
#     return render_template('index.html', async_mode=socketio.async_mode)


# @socketio.on('request', namespace='/devices')
# def broadcast_message(message):
#     message = {'data': {'message': 'I am the message'}}
#     emit('response',
#          {'data': message['data']['message']},
#          broadcast=True)

import uuid
tokens = []
#Handle a POST requst here to verify username and password and then return our token
@app.route('/login', methods=['POST'])
def login():
    if ('username' in request.form) and ('password' in request.form):
        username = request.form['username']
        password = request.form['password']
        if (username == Config.ReadCfg('SYSTEM', 'username') and password == Config.ReadCfg('SYSTEM', 'password')):
            # Generate a token, add it to tokens and sent it to the client
            global tokens
            token = str(uuid.uuid4())
            tokens.append(token)
            return token
        else:
            return '401'

from flask import send_file
#Handle a POST requst here to verify username and password and then return our avatar
@app.route('/avatar', methods=['POST'])
def avatar():
    if ('token' in request.form):
        token = request.form['token']
        global tokens
        if (token in tokens):
            filename = 'avatar.png'
            return send_file(filename, mimetype='image/png')
        else:
            return None

#Handle a POST requst here to write configurations
@app.route('/configuration', methods=['POST'])
def configuration():
    if ('token' in request.form):
        token = request.form['token']
        global tokens
        if (token in tokens):
            if ('username' in request.form):
                Config.WriteCfg('SYSTEM', 'username', request.form['username'])
            if ('password' in request.form):
                Config.WriteCfg('SYSTEM', 'password', request.form['password'])
            if ('syncinterval' in request.form):
                global syncinterval
                syncinterval = int(request.form['syncinterval'])
                Config.WriteCfg('SYSTEM', 'syncinterval', syncinterval)
            return '200'
        else:
            return '401'

# Connect to client and run the background thread
@socketio.on('connect', namespace='/devices')
def connect():
    global tokens
    if (request.args.get('token', '') not in tokens):
    # if (request.args.get('token', '') != token):
        disconnect()
        return
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    # session['thread'] = socketio.start_background_task(background_thread, session['user'])
    # emit('response', {'data': 'Connected'})
    print('Client connected: ', request.sid)


# Disconnect the client and remove device if it has one
@socketio.on('disconnect', namespace='/devices')
def test_disconnect():
    # Close room if exist, then remove the device added previous
    try:
        deviceSID = request.sid
        close_room(deviceSID)
        # Remove device
        for i in xrange(len(devices)):
            try:
                if (devices[i].sid == deviceSID):
                    # Remove device from the devices list
                    devices.remove(devices[i])
                    message = {}
                    message['id'] = devices[i].id
                    # Sent message to announce all clients to remove the device
                    emit('remove', message, broadcast = True)
                    break
            except Exception as e:
                pass
    except Exception as e:
        pass

    # Remove token if exist
    global tokens
    token = request.args.get('token', '')
    if token in tokens:
        tokens.remove(token)
        logging.debug("Token removed:" + token)
    disconnect()
    print('Client disconnected: ', request.sid)


if __name__ == '__main__':
    devicesInit()
    socketio.run(app, debug=True, 
      certfile='/etc/nginx/ssl/cert.pem', 
      keyfile='/etc/nginx/ssl/key.pem', 
      port=5000)