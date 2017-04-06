#!/usr/bin/python
# -*- coding: UTF-8 -*-

# SSL
import eventlet
eventlet.monkey_patch()
from OpenSSL import SSL, crypto

import os, time, threading

# Flask
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Debug
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Configuration: read and write configurations
import utils.config as Config


# Initialize syncinterval
syncinterval = int(Config.ReadCfg('DEFAULT', 'syncinterval'))


# idInt: id for internal devices
# idDiff: id boundary for internal devices and external devices
# idExt: id for external devices
idInt = 1000;
idDiff = 2000;
idExt = idDiff

# device list, including internal devices and external devices
import device as Device
devices = Device.getDevices(idInt)


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
def getAllDevices():
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
def addDevice(message):
    try:
        deviceTitle = message['title']
        deviceType = message['type']
        deviceValue = message['value']
        idExt += 1
        # Use sid as the room no.
        join_room(request.sid)
        global devices
        devices.append(Device(deviceTitle, deviceType, deviceValue, idExt))
        message['id'] = idExt
        emit('add', message, broadcast = True)
    except Exception as e:
        logging.debug(e)


# Get the info of one specific device and sent back to the client
@socketio.on('get', namespace='/devices')
def getDevice(message):
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
def setDevice(message):
    # an example of the received message: {'id': 1000, 'value': false}
    # An example of the sent message: {'id': 1000, 'type': 'Switch', 'value': False}
    try:
        deviceID = message['id']
        for i in xrange(len(devices)):
            if (devices[i].id == deviceID):
                if deviceID <= idDiff:
                    # Reinitialize the device if it is a thread
                    # Thread: This method will raise a RuntimeError if called more than once on the same thread object.
                    try:
                        if not devices[i].isAlive():
                            devices[i] = Device.renewDevice(devices[i].cname, devices[i].title, devices[i].port, deviceID)
                    except:
                        pass
                    deviceValue = message['value']
                    message['type'] = devices[i].type
                    message['value'] = devices[i].setValue(deviceValue)
                    emit('set', message, broadcast=True)
                else:
                    emit('set', message, room = devices[i].sid)
                    # request.namespace.emit('message', "somthing here")
    except Exception as e:
        logging.debug(e)


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
        global devices
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
        logging.debug()

    # Remove token if exist
    global tokens
    token = request.args.get('token', '')
    if token in tokens:
        tokens.remove(token)
        logging.debug("Token removed:" + token)
    disconnect()
    print('Client disconnected: ', request.sid)


import uuid
tokens = []
#Handle a POST requst here to verify username and password and then return our token
@app.route('/login', methods=['POST'])
def login():
    if ('username' in request.form) and ('password' in request.form):
        username = request.form['username']
        password = request.form['password']
        if (username == Config.ReadCfg('DEFAULT', 'username') and password == Config.ReadCfg('DEFAULT', 'password')):
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
def getAvatar():
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
                Config.WriteCfg('DEFAULT', 'username', request.form['username'])
            if ('password' in request.form):
                Config.WriteCfg('DEFAULT', 'password', request.form['password'])
            if ('syncinterval' in request.form):
                global syncinterval
                syncinterval = int(request.form['syncinterval'])
                Config.WriteCfg('DEFAULT', 'syncinterval', syncinterval)
            return '200'
        else:
            return '401'

if __name__ == '__main__':
    socketio.run(app, debug=True, 
      certfile='/etc/nginx/ssl/cert.pem', 
      keyfile='/etc/nginx/ssl/key.pem', 
      port=5000)