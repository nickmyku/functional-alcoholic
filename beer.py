#!/usr/bin/env python

# written by Nicholas Mykulowycz
# created on Dec 23, 2014
# script for reading straing gauges to monitor the weight of a keg

from time import sleep
import RPi.GPIO as GPIO
import pickle
import Adafruit_ADS1x15

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

