#!/usr/bin/python
# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO
import time

prevTime = 0

def getTemp(port):
    time.sleep(0.168)
    temperature, humidity, check, tmp = get(port)
    if check== tmp:
        return temperature
    else:
        return getTemp(port)

def getHumidity(port):
    time.sleep(0.168)
    temperature, humidity, check, tmp = get(port)
    if check== tmp:
        return humidity
    else:
        return getHumidity(port)

def get(port):
    data = []
    j = 0
    GPIO.setup(port, GPIO.OUT)
    GPIO.output(port, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(port, GPIO.HIGH)
    GPIO.setup(port, GPIO.IN)
    while GPIO.input(port) == GPIO.LOW:
        continue
    while GPIO.input(port) == GPIO.HIGH:
        continue
    while j < 40:
        k = 0
        while GPIO.input(port) == GPIO.LOW:
            continue
        while GPIO.input(port) == GPIO.HIGH:
            k += 1
            if k > 100:
                break
        if k < 8:
            data.append(0)
        else:
            data.append(1)
        j += 1
    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check = 0
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7-i)
        humidity_point += humidity_point_bit[i] * 2 ** (7-i)
        temperature += temperature_bit[i] * 2 ** (7-i)
        temperature_point += temperature_point_bit[i] * 2 ** (7-i)
        check += check_bit[i] * 2 ** (7-i)
    tmp = humidity + humidity_point + temperature + temperature_point
    return (temperature, humidity, check, tmp)
