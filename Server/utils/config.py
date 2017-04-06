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
    config.add_section('DEFAULT')
    config.set('DEFAULT', 'username', 'username')
    config.set('DEFAULT', 'password', 'password')
    config.set('DEFAULT', 'syncInterval', '600')
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
