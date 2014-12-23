#!/usr/bin/env python

# written by Nicholas Mykulowycz
# created on Dec 23, 2014
# script for reading straing gauges to monitor the weight of a keg

from time import sleep
import RPi.GPIO as GPIO
import pickle
from Adafruit_ADS1x15 import ADS1x15

# configure gpio pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

ADS1115 = 0x01

# set to the +/- 1.024V range
# +/- 4096
gain = 4096

# set the number of samples per second
sps = 250

# create an adc object
adc = ADS1x15(ic=ADS1115)

while(True):
	# measure the differential voltage
	v_bridge = adc.readADCDifferential(0,1,gain,sps)/1000.0
	# print the measured voltage
	print "%f" % v_bridge
	# delay for a few seconds before going into loop again
	sleep(1)
