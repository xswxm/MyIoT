#!/usr/bin/python
# -*- coding: UTF-8 -*-


# Plese delete 'system.db' before running this module
# This is a temporary solution, i will add suport to the android app later on
# But it is still very useful if you keen to add device though this method

import utils.device as Device
# Example format: Device.addDevice(id, className, title, port, category)
# Highly recommond that the id start from 1000 or a larger integer
# port could be None for some types, check it out in the modules in devices folder
# category could be None if you do not use 'Device' as the className
Device.addDevice(1000, 'BasicSwitch', 'Fake Switch at Port 23', 23, None)
Device.addDevice(1001, 'RandomValue', 'Random Value', None, None)
Device.addDevice(1002, 'CPUTemp', 'CPU Temperature', None, None)
Device.addDevice(1003, 'BasicButton', 'Green LED', 18, None)
Device.addDevice(1004, 'PWMSignal', 'Blue PWM LED', 15, None)
Device.addDevice(1005, 'DH11Temp', 'Temperature', 4, None)
Device.addDevice(1006, 'DH11Humidity', 'Humidity', 4, None)
Device.addDevice(1007, 'BH1750FVI', 'Brightness', 0x23, None)

# the following code is from the previous version
# devices.append(BasicSwitch('Fake Switch at Port 23', 23))
# devices.append(RandomValue('Random Value'))
# devices.append(CPUTemp('CPU Temperature'))
# devices.append(BasicButton('Green LED', 18))
# devices.append(PWMSignal('Blue PWM LED', 15))
# devices.append(DH11Temp('Temperature', 4))
# devices.append(DH11Humidity('Humidity', 4))
# devices.append(BH1750FVI('Brightness', 0x23))
devices = Device.getDevices()
print devices
for device in devices:
	print device.description()