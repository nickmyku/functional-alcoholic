#!/usr/bin/env python

# written by Nicholas Mykulowycz
# created on Dec 23, 2014
# script for reading straing gauges to monitor the weight of a keg

from time import sleep
import RPi.GPIO as GPIO
import pickle
import Adafruit_ADS1x15

# configure gpio pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

ADS1115 = 0x01

# set to the +/- 1.024V range
gain = 1024

# set the number of samples per second
sps = 250

# create an adc object
adc = ADS1x15(ic=ADS1115)

v_neg = 0
v_pos = 0
