#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Debug
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Database file path
import os,os.path
curfilePath = os.path.abspath(__file__)
curDir = os.path.abspath(os.path.join(curfilePath,os.pardir))
parentDir = os.path.abspath(os.path.join(curDir,os.pardir))
dbPath = parentDir + '/system.db'
# dbPath = '../system.db'

sys.path.append("..")

# Modules for devices
from devices.general import Device, RandomValue
from devices.system import CPUTemp
from devices.basic import BasicButton, BasicSwitch, PWMSignal, SOSLight, BreathLight
from devices.bh1750fvi import BH1750FVI
from devices.dh11 import DH11Temp, DH11Humidity
from devices.others import AUD2RMB

# Initialize devices
devices = []

import sqlite3

# sqlite3 encode
reload(sys)
sys.setdefaultencoding('utf8')

# Annotation 
# id, module, title, port, value, mac, type used here are just for their names but not the real id or module...

def sqlTableInit():
    conn = sqlite3.connect(dbPath)
    logging.debug("Opened database successfully")
    conn.execute('''CREATE TABLE IF NOT EXISTS DEVICES
        (ID         INT          PRIMARY KEY     NOT NULL,
        CLASSNAME   CHAR(16)                     NOT NULL,
        TITLE       CHAR(255)                    NOT NULL,
        PORT        INT,
        CATEGORY    CHAR(16));''')
    conn.close()

def getDevices():
    return getDevicesSQL()

def getDevicesSQL():
    global devices
    conn = sqlite3.connect(dbPath)
    conn.text_factory = str
    logging.debug("Opened database successfully")
    cursor = conn.execute("SELECT ID, CLASSNAME, TITLE, PORT, CATEGORY from DEVICES")
    for row in cursor:
        # print "ID = ", row[0], ", TYPE = ", type(row[0])
        # print "CLASSNAME = ", row[1], ", TYPE = ", type(row[1])
        # print "TITLE = ", row[2], ", TYPE = ", type(row[2])
        # print "PORT = ", row[3], ", TYPE = ", type(row[3])
        # print "CATEGORY = ", row[4], ", TYPE = ", type(row[4]), "\n"
        id = row[0]
        className = row[1]
        title = row[2]
        port = row[3]
        category = row[4]
        # Create an class object
        classObj = eval(className)
        # Create a device instance
        if port == None:
            device = classObj(id, title)
        elif className != 'Device':
            device = classObj(id, title, port)
        else:
            device = classObj(id, title, port, category)
        devices.append(device)
    logging.debug("Operation done successfully")
    conn.close()
    return devices

def addDevice(id, className, title, port, category):
    # id = device.id
    # title = device.title
    # classFullName = str(device.__class__).split('.')
    # calssName = classFullName[len(classFullName) - 1]
    # title = device.title
    # port = (hasattr(device, 'port')) and device.port or None
    # mac = (hasattr(device, 'mac')) and device.mac or None
    # category = (hasattr(device, 'category')) and device.category or None
    classObj = eval(className)
    if port == None:
        device = classObj(id, title)
    else:
        device = classObj(id, title, port)
    if category == None:
        category = device.category
    else:
        device.category = category
    addDeviceSQL(id, className, title, port, category)
    return device

def addDeviceSQL(id, calssName, title, port, category):
    conn = sqlite3.connect(dbPath)
    conn.text_factory = str
    logging.debug("Opened database successfully")
    # conn.execute("INSERT INTO DEVICES (ID,TITLE,PORT,VALUE,TYPE) VALUES (1000, 'Demo Switch', '23', 'False', 'BasicSwitch')");
    commend = "INSERT INTO DEVICES (ID, CLASSNAME, TITLE, PORT, CATEGORY) VALUES ("
    commend += str(id) + ","
    commend += "'" + str(calssName) + "',"
    commend += "'" + str(title) + "',"
    commend += (port == None) and "NULL," or str(port) + ","
    commend += (category == None) and "NULL)" or "'" + str(category) + "')"
    conn.execute(commend)
    conn.commit()
    logging.debug("Record created successfully")
    conn.close()

def removeDevice(device):
    removeDeviceSQL(device.id)

def removeDeviceSQL(id):
    conn = sqlite3.connect(dbPath)
    logging.debug("Opened database successfully")
    conn.execute("DELETE from DEVICES where ID="+ str(id) + ";")
    conn.commit()
    logging.debug("Record deleted successfully")
    conn.close()

def configureDevice(device):
    id = device.id
    title = device.title
    classFullName = str(device.__class__).replace('\'>', '').split('.')
    calssName = classFullName[len(classFullName) - 1]
    title = device.title
    port = (hasattr(device, 'port')) and device.port or None
    category = (hasattr(device, 'category')) and device.category or None
    configureDeviceSQL(id, calssName, title, port, category)

def configureDeviceSQL(id, calssName, title, port, category):
    conn = sqlite3.connect(dbPath)
    conn.text_factory = str
    logging.debug("Opened database successfully")
    commend = "UPDATE DEVICES set "
    commend += "CLASSNAME='" + str(calssName) + "',"
    commend += "TITLE='" + str(title) + "',"
    commend += (port == None) and "PORT=NULL," or "PORT=" + str(port) + ","
    commend += (category == None) and "CATEGORY=NULL " or "CATEGORY='" + str(category) + "' "
    commend += "where ID=" + str(id)
    conn.execute(commend)
    conn.commit()
    logging.debug("Record updated successfully")
    conn.close()

# Recreate an device instance.
# Because some device is running as a thread 
# and thread in Python cannot be restart.
def renewDevice(device):
    id = device.id
    title = device.title
    classFullName = str(device.__class__).replace('\'>', '').split('.')
    className = classFullName[len(classFullName) - 1]
    classObj = eval(className)
    return classObj(device.id, device.title, device.port)

# Get all avaliable classes and return them as a dictionary
def getClassNameList():
    classNameList = []
    className = {'classname':'RandomValue', 'port':'False'}
    classNameList.append(className)
    className = {'classname':'CPUTemp', 'port':'False'}
    classNameList.append(className)
    className = {'classname':'BasicButton', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'BasicSwitch', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'PWMSignal', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'SOSLight', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'BreathLight', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'BH1750FVI', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'DH11Temp', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'DH11Humidity', 'port':'True'}
    classNameList.append(className)
    className = {'classname':'AUD2RMB', 'port':'False'}
    classNameList.append(className)
    return {'classnamelist':classNameList}

sqlTableInit()
