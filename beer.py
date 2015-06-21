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
gain = 256

# set the number of samples per second
sps = 250

# create an adc object
adc = ADS1x15(ic=ADS1115)

# number of samples to take average of
samples = 15

# voltage offset to remove weight of scale itself
v_offset = -0.1

# values for calibrating the strain gauge
known_weight = 196
known_volt = 3.11
conv_fact = known_weight/known_volt

min_weight = 0
max_weight = 1

def getVoltage(samples):
	v_bridge_avg = 0
	for  i in range(0,samples):
		# measure the differential voltage
		v_bridge = adc.readADCDifferential(1,0,gain,sps)
		v_bridge = abs(v_bridge)
		v_bridge_avg += v_bridge
	# average the signal
	v_bridge_avg /=samples
	# return the voltage
	return v_bridge_avg


def toWeight(val, offset, scale):
	# zero with offset
	val += offset
	# calculate the weight
	val *= conv_fact
	# retunr the weight value
	return val

def getKegState(type):
	global v_offset
	global conv_fact
	global samples	
	global min_weight
	global max_weight

	# get data
	voltage = getVoltage(samples)
	weight = toWeight(voltage, v_offset, samples)
	
	# assign wight of keg
	if (type == "mini" or type == "Mini"):
		min_weight = 0
		max_weight = 13
	elif (type == "cornelius" or type == "Cornelius"):
		min_weight = 0
		max_weight = 49
	elif (type == "sixth" or type == "Sixth"):
		min_weight = 10
		max_weight = 45 #58
	elif (type == "quarter" or type == "Quarter"):
		min_weight = 20
		max_weight = 87
	elif (type == "slim" or type == "Slim"):
		min_weight = 20	# need to confirm this number
		max_weight = 87
	else: #(type == "half" or type == "Half"):
		min_weight = 0
		max_weight = 161

	# determine the percentage of beer remaining
	percent = (weight-min_weight)/(max_weight-min_weight)
	# convert that percentage to a state integer ranging from 0 to 5
	state = int(5 * percent)
	# return the keg state
	return state



while (False):
	volts = getVoltage(15)
	pounds = toWeight(volts,v_offset, conv_fact) 
	status = getKegState("quarter")
	# print the measured voltage
	print "%f      %f      %d " % (volts,pounds,status)
	# delay for a few seconds before going into loop again
	sleep(1)
