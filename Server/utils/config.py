#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ConfigParser
import os,os.path
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

curfilePath = os.path.abspath(__file__)
curDir = os.path.abspath(os.path.join(curfilePath,os.pardir))
parentDir = os.path.abspath(os.path.join(curDir,os.pardir))
syscfg = parentDir + '/system.cfg'

def WriteCfgDefault():
    if os.path.exists(syscfg):
        os.remove(syscfg)
    config = ConfigParser.RawConfigParser()
    config.add_section('SYSTEM')
    config.set('SYSTEM', 'username', 'username')
    config.set('SYSTEM', 'password', 'password')
    config.set('SYSTEM', 'syncInterval', '600')
    with open(syscfg, 'wb') as configfile:
        config.write(configfile)


def ReadCfg(section, option):
    try:
        if not os.path.exists(syscfg):
            WriteCfgDefault()
        config = ConfigParser.RawConfigParser()
        config.read(syscfg)
        return config.get(section, option)
    except Exception as e:
        logging.debug(e)

def WriteCfg(section, option, value):
    try:
        config = ConfigParser.RawConfigParser()
        config.read(syscfg)
        config.set(section, option, value)
        with open(syscfg, 'wb') as configfile:
            config.write(configfile)
        return True
    except Exception as e:
        logging.debug(e)
        return False

def ReadDevices():
    try:
        devices = []
        if not os.path.exists(syscfg):
            WriteCfgDefault()
            return devices
        config = ConfigParser.RawConfigParser()
        config.read(syscfg)
        titles = config.sections()
        for i in xrange(1, len(titles)):
            title = titles[i]
            device = {'title': title}
            myItems = config.items(title)
            for i in xrange(len(myItems)):
                device[myItems[i][0]] = myItems[i][1]
            devices.append(device)
        return devices
    except Exception as e:
        logging.debug(e)
