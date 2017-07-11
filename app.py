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
# syncinterval = 600

# device list, including internal devices and external devices
import utils.device as Device
devices = Device.getDevices()

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None
mynamespace = '/devices'

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
        for i in range(len(devices)):
            deviceCategory = devices[i].category
            if (deviceCategory == 'Value' or deviceCategory == 'SeekBar'):
                try:
                    if devices[i].port < 5000:
                        message = devices[i].description()
                        # message['id'] = devices[i].id
                        # message['category'] = devices[i].category
                        # message['value'] = devices[i].getValue()
                        logging.debug(message)
                        # message = deviceDesc
                        socketio.emit('set', message, broadcast = True, namespace = mynamespace)
                        # socketio.emit('setDevice', message, namespace='/')
                    else:
                        socketio.emit('set', message, room = devices[i].id, namespace = mynamespace)
                except Exception as e:
                    logging.debug(e)


# Get the info of all devices and sent them back to the client
@socketio.on('getAll', namespace = mynamespace)
def getAllDevices():
    # An example of the received message: {'title': 'Green LED', 'type': 'Switch', 'value': False, 'id': 1000}
    try:
        message = {}
        logging.debug('-------------------get All Devices---------------------------------')
        for i in range(len(devices)):
            message = devices[i].description()
            logging.debug(message)
            emit('add', message)
        emit('adddone', {})
    except Exception as e:
        logging.debug(e)

# Get the info of one specific device and sent back to the client
@socketio.on('get', namespace = mynamespace)
def getDevice(message):
    # An example of the received message: {'id': 1000}
    # An example of the sent message: {'id': 1000, 'type': 'Switch', 'value': False}
    try:
        deviceID = message['id']
        global devices
        for i in range(len(devices)):
            if devices[i].id == deviceID:
                if not 'port' in dir(devices[i]):
                    emit('set', devices[i].description())
                elif devices[i].port < 5000:
                    emit('set', devices[i].description())
                else:
                    emit('get', message, room = devices[i].id)
                break
    except Exception as e:
        logging.debug(e)


# Set the value of a specific device
@socketio.on('set', namespace = mynamespace)
def setDevice(message):
    # an example of the received message: {'id': 1000, 'value': false}
    # An example of the sent message: {'id': 1000, 'type': 'Switch', 'value': False}
    try:
        deviceID = message['id']
        global devices
        for i in range(len(devices)):
            if devices[i].id == deviceID:
                if devices[i].port < 5000:
                    # Reinitialize the device if it is a thread
                    # Thread: This method will raise a RuntimeError if called more than once on the same thread object.
                    try:
                        if not devices[i].isAlive():
                            devices[i] = Device.renewDevice(devices[i])
                    except:
                        pass
                    deviceValue = message['value']
                    # import time
                    # timeNow = time.time()
                    # print 0
                    devices[i].setValue(deviceValue)
                    # timePrev = timeNow
                    # timeNow = time.time()
                    # print timeNow - timePrev
                    emit('set', devices[i].description(), broadcast=True)
                    # timePrev = timeNow
                    # timeNow = time.time()
                    # print timeNow - timePrev

                else:
                    emit('set', message, room = devices[i].id)
                    # request.namespace.emit('message', "somthing here")
                break
    except Exception as e:
        logging.debug(e)


# Add a device and send its info to all clients
# Current: no accessable funtion
@socketio.on('add', namespace = mynamespace)
def addDevice(message):
    try:
        global devices
        deviceClassName = message['classname']
        deviceTitle = message['title']
        devicePort = None
        deviceCategory = (message.has_key('category')) and message['category'] or None
        # if port is larger than 5000, then it is an remote device,
        # we should create an room based on its sid
        # if port is allready used, then update the device and make it accessable
        if message.has_key('port'):
            devicePort = message['port']
            for i in range(len(devices)):
                if 'port' in dir(devices[i]):
                    if devicePort > 5000:
                        join_room(request.sid)
                    if devices[i].port == devicePort:
                        # update device
                        deviceID = devices[i].id
                        devices[i] = Device.updateDevice(deviceID, deviceClassName, deviceTitle, devicePort, deviceCategory)
                        emit('remove', {'id':deviceID}, broadcast = True)
                        emit('add', devices[i].description(), broadcast = True)
                        return
        # add device as usual
        deviceID = devices[len(devices) - 1].id + 1
        message['id'] = deviceID
        device = Device.addDevice(deviceID, deviceClassName, deviceTitle, devicePort, deviceCategory)
        devices.append(device)
        emit('add', device.description(), broadcast = True)
    except Exception as e:
        logging.debug(e)

# Remove a device and notify all clients
@socketio.on('remove', namespace = mynamespace)
def removeDevice(message):
    try:
        deviceID = message['id']
        global devices
        for i in range(len(devices)):
            if devices[i].id == deviceID:
                Device.removeDevice(devices[i])  # Remove device from database
                devices.remove(devices[i])  # Remove device from devices list
                emit('remove', message, broadcast = True)
                break
    except Exception as e:
        logging.debug(e)

# Configure a device, including its port and title, and notify all clients
# this part may need further development, such as adding schedule
@socketio.on('configure', namespace = mynamespace)
def configureDevice(message):
    try:
        deviceID = message['id']
        global devices
        for i in range(len(devices)):
            if devices[i].id == deviceID:
                # Configure device from devices list
                if message.has_key('port'):
                    devices[i].port = message['port']
                devices[i].title = message['title']
                # Configure device from database
                Device.configureDevice(devices[i])
                # Broadcast the changes of the device
                message.pop('port', None)  # Remove key 'port' from message
                message['category'] = devices[i].category
                emit('configure', message, broadcast = True)
                break
    except Exception as e:
        logging.debug(e)


@socketio.on('getclassnamelist', namespace = mynamespace)
def getClassNameList():
    try:
        emit('setClassNameList', Device.getClassNameList())
    except Exception as e:
        logging.debug(e)

# Connect to client and run the background thread
@socketio.on('connect', namespace = mynamespace)
def connect():
    global tokens
    if (request.args.get('token', '') not in tokens):
        disconnect()
        return
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    # session['thread'] = socketio.start_background_task(background_thread, session['user'])
    # emit('response', {'data': 'Connected'})
    print('Client connected: ', request.sid)


# Disconnect the client and remove device if it has one
# Current: no accessable funtion
@socketio.on('disconnect', namespace = mynamespace)
def test_disconnect():
    # here we have to use the sid to locate the the disconnected device
    # and if it exists, remove its room and set it as unaceessable
    try:
        close_room(request.sid)
    except Exception as e:
        logging.debug(e)

    # Remove token if exist
    global tokens
    token = request.args.get('token', '')
    if token in tokens:
        tokens.remove(token)
        logging.debug("Token removed:" + token)
    # disconnect()
    print('Client disconnected: ', request.sid)


# @app.route('/')
# def index():
#     return render_template('index.html', async_mode=socketio.async_mode)


# @socketio.on('request', namespace = mynamespace)
# def broadcast_message(message):
#     message = {'data': {'message': 'I am the message'}}
#     emit('response',
#          {'data': message['data']['message']},
#          broadcast=True)

import uuid
tokens = []
tokens.append("d1e90ebd-cbbf-46b8-b77d-de25ceca7a20")
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


# @app.route('/login', methods=['GET'])
# def loginx():
#     username = request.args.get('username')
#     password = request.args.get('password')
#     if (username == Config.ReadCfg('DEFAULT', 'username') and password == Config.ReadCfg('DEFAULT', 'password')):
#         # Generate a token, add it to tokens and sent it to the client
#         global tokens
#         token = str(uuid.uuid4())
#         tokens.append(token)
#         return token
#     else:
#         return '401'

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

class SocketIONoSSL(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        socketio.run(app, debug=True, 
            host="0.0.0.0", 
            port=8800)

class SocketIOSSL(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        socketio.run(app, debug=True, 
            certfile='/etc/nginx/ssl/cert.pem', 
            keyfile='/etc/nginx/ssl/key.pem', 
            port=5000)

if __name__ == '__main__':
    socketioNoSSL = SocketIONoSSL()
    SocketIOSSL = SocketIOSSL()
    socketio.run(app, debug=True, 
        certfile='/etc/nginx/ssl/cert.pem', 
        keyfile='/etc/nginx/ssl/key.pem', 
        port=5000)