#!/usr/bin/python
# -*- coding: UTF-8 -*-

import RPi.GPIO as GPIO

# Debug
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


# Modules for devices
from devices.general import Device, RandomValue
from devices.system import CPUTemp
from devices.base import BaseButton, BaseSwitch, PWMSignal, SOSLight, BreathLight
from devices.bh1750fvi import BH1750FVI
from devices.dh11 import DH11Temp, DH11Humidity

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Initialize devices
devices = []
devices.append(RandomValue('Random Value'))
devices.append(CPUTemp('CPU Temperature'))
devices.append(BaseButton('Green LED', 18))
devices.append(BaseSwitch('Fake Switch at Port 23', 23))
devices.append(PWMSignal('Blue PWM LED', 15))
devices.append(DH11Temp('Temperature', 4))
devices.append(DH11Humidity('Humidity', 4))
devices.append(BH1750FVI('Brightness', 0x23))


def getDevices(deviceID):
    global devices
    for i in xrange(len(devices)):
        devices[i].id = deviceID
        deviceID += 1
    return devices

def renewDevice(cname, title, port, id):
    if cname == "BreathLight":
        return BreathLight(title, port, id)
    if cname == "SOSLight":
        return SOSLight(title, port, id)
    if cname == "PWMSignal":
        return PWMSignal(title, port, id)