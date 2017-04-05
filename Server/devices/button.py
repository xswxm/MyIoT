#!/usr/bin/python
# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO
import threading

class Button:
    _lock = threading.RLock()
    def __init__(self, title, port, id = 1000):
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Button'
        self.isThread = False
        GPIO.setup(self.port, GPIO.OUT)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        if (GPIO.input(self.port) == '1'):
            message['value'] = True
        else:
            message['value'] = False
        return message
    def setValue(self, value):
        with Button._lock:
            GPIO.output(self.port, value)
        return value
