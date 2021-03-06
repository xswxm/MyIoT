#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import RPi.GPIO as GPIO

class Button:
    def __init__(self, id, title, port, feasible = True):
        self.id = id
        self.title = title
        self.port = port
        self.feasible = feasible
        self.category = 'Button'
        GPIO.setup(self.port, GPIO.OUT)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['port'] = self.port
        message['category'] = self.category
        message['value'] = self.getValue()
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        if (GPIO.input(self.port) == 1):
            return True
        else:
            return False
    def setValue(self, value):
        GPIO.output(self.port, value)
        return value

class Switch:
    def __init__(self, id, title, port, feasible = True):
        self.id = id
        self.title = title
        self.port = port
        self.feasible = feasible
        self.category = 'Switch'
        GPIO.setup(self.port, GPIO.OUT)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['port'] = self.port
        message['category'] = self.category
        message['value'] = self.getValue()
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        if (GPIO.input(self.port) == 1):
            return True
        else:
            return False
    def setValue(self, value):
        GPIO.output(self.port, value)
        return value
