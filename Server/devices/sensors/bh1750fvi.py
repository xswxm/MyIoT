#!/usr/bin/python
# -*- encoding: utf-8 -*-

import smbus
def get(addr):
    bus = smbus.SMBus(1)
    data = bus.read_i2c_block_data(addr,0x11)
    return (data[1] + (256 * data[0])) / 1.2