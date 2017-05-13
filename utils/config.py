#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ConfigParser
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Configuration file path
import os,os.path
curfilePath = os.path.abspath(__file__)
curDir = os.path.abspath(os.path.join(curfilePath,os.pardir))
parentDir = os.path.abspath(os.path.join(curDir,os.pardir))
cfgPath = parentDir + '/system.cfg'

# sys.path.append("..")
# cfgPath = '../system.cfg'

def WriteCfgDefault():
    if os.path.exists(cfgPath):
        os.remove(cfgPath)
    config = ConfigParser.RawConfigParser()
    config.add_section('DEFAULT')
    config.set('DEFAULT', 'username', 'username')
    config.set('DEFAULT', 'password', 'password')
    config.set('DEFAULT', 'syncInterval', '600')
    with open(cfgPath, 'wb') as configfile:
        config.write(configfile)


def ReadCfg(section, option):
    try:
        if not os.path.exists(cfgPath):
            WriteCfgDefault()
        config = ConfigParser.RawConfigParser()
        config.read(cfgPath)
        return config.get(section, option)
    except Exception as e:
        logging.debug(e)

def WriteCfg(section, option, value):
    try:
        config = ConfigParser.RawConfigParser()
        config.read(cfgPath)
        config.set(section, option, value)
        with open(cfgPath, 'wb') as configfile:
            config.write(configfile)
        return True
    except Exception as e:
        logging.debug(e)
        return False
