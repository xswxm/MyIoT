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
    except Exception as e:
        logging.debug(e)


# Add a device and send its info to all clients
# Current: it only works for adding devives connected to our Pi
@socketio.on('add', namespace = mynamespace)
def addDevice(message):
    try:
        global devices
        deviceTitle = message['title']
        devicePort = (message.has_key('port')) and message['port'] or None
        # devicePort = message['port']
        for i in range(len(devices)):
            if 'port' in dir(devices[i]):
                if devices[i].port == devicePort:
                    # renew device
                    devices[i].title = deviceTitle
                    devices[i].port = devicePort
                    Device.updateDevice(devices[i])
                    emit('set', devices[i].description(), broadcast = True)
                    return
        # add device
        deviceID = devices[len(devices) - 1].id + 1
        message['id'] = deviceID
        deviceClassName = message['className']
        deviceCategory = (message.has_key('category')) and message['category'] or None
        device = Device.addDevice(deviceID, deviceClassName, deviceTitle, devicePort, deviceCategory)
        devices.append(device)
        message = device.description()
        emit('add', message, broadcast = True)
        # Use id as the room No.
        # join_room(deviceID)
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
                    devices[i].setValue(deviceValue)
                    emit('set', devices[i].description(), broadcast=True)
                else:
                    emit('set', message, room = devices[i].id)
                    # request.namespace.emit('message', "somthing here")
                break
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
@socketio.on('disconnect', namespace = mynamespace)
def test_disconnect():
    # Close room if exist, then remove the device added previous
    try:
        deviceID = request.id
        close_room(deviceID)
        # Remove device
        global devices
        for i in xrange(len(devices)):
            try:
                if (devices[i].id == deviceID):
                    message = {}
                    message['id'] = devices[i].id
                    # Sent message to announce all clients to remove the device
                    emit('remove', message, broadcast = True)
                    # Remove device from the devices list
                    # devices.remove(devices[i])
                    del devices[i]
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
# tokens.append("d1e90ebd-cbbf-46b8-b77d-de25ceca7a20")
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


# #Handle a POST requst from exteral devices
# @app.route('/add', methods=['POST'])
# def configuration():
#     try:
#         if ('token' in request.form):
#             token = request.form['token']
#             global tokens
#             if (token in tokens):
#                 deviceTitle = request.form['title']
#                 deviceType = request.form['type']
#                 deviceValue = request.form['value']
#                 idExt += 1

#                 global devices
#                 devices.append(Device(deviceTitle, deviceType, deviceValue, idExt))
#                 message = {}
#                 message['title'] = deviceTitle
#                 message['type'] = deviceType
#                 message['value'] = deviceValue
#                 message['id'] = idExt
#                 emit('add', message, broadcast = True)
#                 return str(idExt)
#             else:
#                 return '401'
#         else:
#             return '404'
#     except Exception as e:
#         logging.debug()
#         return '404'

# #Handle a POST requst here to write configurations
# @app.route('/set', methods=['POST'])
# def configuration():
#     try:
#         if ('token' in request.form):
#             token = request.form['token']
#             global tokens
#             if (token in tokens):
#                 deviceTitle = request.form['title']
#                 deviceType = request.form['type']
#                 deviceValue = request.form['value']
#                 deviceID = int(request.form['id'])
#                 idExt += 1

#                 global devices
#                 for i in xrange(len(devices)):
#                     if (devices[i].id == deviceID):
#                         if ((devices[i].title != deviceTitle) and (devices[i].value != deviceValue)):
#                             devices[i].title = deviceTitle
#                             devices[i].value = deviceValue
#                             emit('set', devices[i].description(), broadcast = True)
#                 return '200'
#             else:
#                 return '401'
#         else:
#             return '404'
#     except Exception as e:
#         logging.debug()
#         return '404'


# from flask import Response
# @app.route("/ogg", methods=['POST'])
# def streamogg():
#     def generate():
#         with open("song.ogg", "rb") as fogg:
#             data = fogg.read(1024)
#             while data:
#                 yield data
#                 data = fogg.read(1024)
#     return Response(generate(), mimetype="audio/ogg")


if __name__ == '__main__':
    socketio.run(app, debug=True, 
      certfile='/etc/nginx/ssl/cert.pem', 
      keyfile='/etc/nginx/ssl/key.pem', 
      port=5000)