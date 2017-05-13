#!/usr/bin/python
# -*- encoding: utf-8 -*-

import random
import threading

class Device:
    def __init__(self, id, title, feasible = True):
        self.id = id
        self.title = title
        self.category = 'UNIDENTIFIED'
        self.feasible = feasible
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.value
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        print 'Developing...'
    def setValue(self, value):
        print 'Developing...'

class RandomValue:
    _lock = threading.RLock()
    def __init__(self, id, title, feasible = True):
        self.id = id
        self.title = title
        self.feasible = feasible
        self.category = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = str(self.getValue(100))
        message['feasible'] = self.feasible
        return message
    def getValue(self, value = 100):
        with RandomValue._lock:
            return str(random.randrange(0, value + 1, 2))
