import dh11
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

print str(dh11.getTemp(4)) + " 'C"
print str(dh11.getTemp(4)) + " 'C"