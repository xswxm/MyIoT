#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import pigpio
class Button:
    def __init__(self, id, title, port, feasible = True):
        self.id = id
        self.title = title
        self.port = port
        self.pi = pigpio.pi()
        self.feasible = feasible
        self.category = 'Button'
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
        if self.pi.read(self.port):
            return True
        else:
            return False
    def setValue(self, value):
        self.pi.write(self.port, value)
        return value

class Switch:
    def __init__(self, id, title, port, feasible = True):
        self.id = id
        self.title = title
        self.port = port
        self.pi = pigpio.pi()
        self.feasible = feasible
        self.category = 'Switch'
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
        if self.pi.read(self.port):
            return True
        else:
            return False
    def setValue(self, value):
        self.pi.write(self.port, value)
        return value
