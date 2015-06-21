#!/usr/bin/env python

# written by Nicholas Mykulowycz
# created on Dec 23, 2014
# script for reading straing gauges to monitor the weight of a keg

import time
from time import sleep
from time import time
import RPi.GPIO as GPIO
import pickle
#import Adafruit_GPIO.I2C as I2C
from Adafruit_ADS1x15 import ADS1x15 			# ADC package
from Adafruit_SSD1306 import SSD1306_128_64		# OLED display package
#import Adafruit_SSD1306
import smbus

# supporting packages for OLED
import Image
import ImageDraw
import ImageFont

############################################################################################
#
#  Adafruit i2c interface plus protection against errors and minor enhancement
#
############################################################################################
class I2C:

   def __init__(self, address, bus=smbus.SMBus(1)):
      self.address = address
      self.bus = bus

   def reverseByteOrder(self, data):
      "Reverses the byte order of an int (16-bit) or long (32-bit) value"
      # Courtesy Vishal Sapre
      dstr = hex(data)[2:].replace('L','')
      byteCount = len(dstr[::2])
      val = 0
      for i, n in enumerate(range(byteCount)):
         d = data & 0xFF
         val |= (d << (8 * (byteCount - i - 1)))
         data >>= 8
      return val

   def write8(self, reg, value):
      "Writes an 8-bit value to the specified register/address"
      while True:
         try:
            self.bus.write_byte_data(self.address, reg, value)
            logger.debug('I2C: Wrote 0x%02X to register 0x%02X', value, reg)
            break
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)

   def writeList(self, reg, list):
      "Writes an array of bytes using I2C format"
      while True:
         try:
            self.bus.write_i2c_block_data(self.address, reg, list)
            break
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)

   def readU8(self, reg):
      "Read an unsigned byte from the I2C device"
      while True:
         try:
            result = self.bus.read_byte_data(self.address, reg)
            logger.debug('I2C: Device 0x%02X returned 0x%02X from reg 0x%02X', self.address, result & 0xFF, reg)
            return result
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)

   def readS8(self, reg):
      "Reads a signed byte from the I2C device"
      while True:
         try:
            result = self.bus.read_byte_data(self.address, reg)
            logger.debug('I2C: Device 0x%02X returned 0x%02X from reg 0x%02X', self.address, result & 0xFF, reg)
            if (result > 127):
               return result - 256
            else:
               return result
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)

   def readU16(self, reg):
      "Reads an unsigned 16-bit value from the I2C device"
      while True:
         try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg+1)
            logger.debug('I2C: Device 0x%02X returned 0x%04X from reg 0x%02X', self.address, result & 0xFFFF, reg)
            if result == 0x7FFF or result == 0x8000:
               logger.critical('I2C read max value')
               time.sleep(0.001)
            else:
               return result
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)

   def readS16(self, reg):
      "Reads a signed 16-bit value from the I2C device"
      while True:
         try:
            hibyte = self.bus.read_byte_data(self.address, reg)
            if (hibyte > 127):
               hibyte -= 256
            result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg+1)
            logger.debug('I2C: Device 0x%02X returned 0x%04X from reg 0x%02X', self.address, result & 0xFFFF, reg)
            if result == 0x7FFF or result == 0x8000:
               logger.critical('I2C read max value')
               time.sleep(0.001)
            else:
               return result
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)
            
   def readList(self, reg, length):
      "Reads a a byte array value from the I2C device"
      while True:
         try:
            result = self.bus.read_i2c_block_data(self.address, reg, length)
            logger.debug('I2C: Device 0x%02X from reg 0x%02X', self.address, reg)
            return result
         except IOError, err:
            logger.exception('Error %d, %s accessing 0x%02X: Check your I2C address', err.errno, err.strerror, self.address)
            time.sleep(0.001)

# reset pin for OLED display
RST = 8

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
# create OLED object
disp = SSD1306_128_64(rst=RST, i2c_bus=1)

# initilaize display
disp.begin()
disp.clear()
disp.display()
FONT = ImageFont.load_default()

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

global msg_array

msg_array = [	"We regret to inform you that your life is over as you know it... your keg is now empty",
			"It would appear that your keg was mortally wounded and has lost a lot of fluid, we advice you get your keg to a medical professional at your earliest convenience",
			"Looks like your keg isn't in the best shape... you should take care of that",
			"So you still have a lot of beer left, but honestly is \"a lot\" really good enough for you?",
			"Your keg is in good shape... for now... we'll be watching you.",
			"Congradulations! its a keg!" ]
		


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

def setScreenMsg(txt):
	# typecast as a string
	txt = str(txt)
	MSG_XPOS = 10
	MSG_YPOS = 10
	# write the messgae to the screen buffer
	disp.text((MSG_XPOS,MSG_YPOS), txt, font=FONT, fill=255)
	# refresh the display
	disp.display()
	return 0

def setScreenValue(val):
	# typecast as a float
	val = float(val)
	VAL_XPOS = 10
	VAL_YPOS = 50
	# create value string
	val_str = "%.3f lbs of beer remaining" % val
	# Write the value string to the screen buffer
	disp.text((VAL_XPOS,VAL_YPOS), val_str, font=FONT, fill=255)
	# refresh the display
	disp.display()
	return 0

def setScreenIndicator(level):
	# typecast as an integer
	level = int(level)

	x_offset = 70
	y_offset = 5

	segment_fill = [0, 0, 0, 0, 0]
	FILLED_SHADE = 128

	# full keg indicator
	if(level >= 5):
		segment_fill[4] = FILLED_SHADE
	# 80% of keg indicator
	if(level >= 4):
		segment_fill[3] = FILLED_SHADE
	# 60% of keg indicator
	if(level >= 3):
		segment_fill[2] = FILLED_SHADE
	# 40% of keg indicator
	if(level >= 2):
		segment_fill[1] = FILLED_SHADE
	# 20% keg indicator 
	if(level >= 1):
		segment_fill[0] = FILLED_SHADE
	# empty keg indicator
	#elif(level = 0):
		#return 0
	# hide keg indicator
	#else:
		#return -1

	# set dimensions of top trapazoidal section
	height_element = 7
	width_element = 28
	x_element = x_offset + width_element + 1
	y_element = y_offset + height_element
	# draw top trapazoidal section
	#draw.polygon([], outline=255, fill=segment_fill[4])

	y_offset += height_element
	# set dimenstions of top rectangular section
	height_element = 7
	width_element = 30
	x_element = x_offset + width_element
	y_element += height_element
	# draw the top rectangular section
	draw.rectangle((x_offset, y_offset, x_element, y_element), outline=255, fill=segment_fill[3])

	y_offset += height_element
	# set dimentions of middle rectangular section
	height_element = 27 
	width_element = 28
	x_element = x_offset + width_element + 1
	y_element += height_element
	# draw the middle rectangular section
	draw.rectangle((x_offset+1, y_offset, x_element, y_element), outline=255, fill=segment_fill[2]) 

	y_offset += height_element
	# set dimensions for botton rectangular section
	height_element = 7
	width_element = 30
	x_element = x_offset + width_element
	y_element += height_element
	# draw the bottom rectangular section
	draw.rectangle((x_offset, y_offset, x_element, y_element), outline=255, fill=segment_fill[1])

	y_offset += height_element
	# set dimentiosn for bottom trapazoidal section
	height_element = 7
	width_element = 30
	x_element = x_offset + width_element + 1
	y_element += height_element
	# draw bottom trapazoidal section
	#draw.polygon([], outline=255, fill=segment_fill[0])


	

last_update_time = time()

while (True):
	global last_update_time
	global last_alert_time
	global msg_array
	try:
		curr_time = time()
		if((curr_time - last_update_time) > refresh_time):
			# get values from ADC and format them into something useful
			volts = getVoltage(15)
			pounds = toWeight(volts,v_offset, conv_fact) 
			status = getKegState("quarter")
			
			# update vales on OLED
			setScreenValue(pounds)
			# make sure status is within array bounds before trying to index array element
			if((status>=0) and (status<=len(msg_array))):
				setScreenMsg(msg_array[status])
			# make sure the keg isnt in empty alarm state before showing indicator
			if(status != 0):
				setScreenIndicator(status)

			# print the measured voltage to terminal
			print "%f-V      %f-lbs      %d " % (volts,pounds,status)

			# update the last update time
			last_update_time = time()
		# alert flash for low keg
		if(status < 1):
			if((curr_time - last_alert_time) > alert_time):
				# hide keg indicator
				print "stuff"
				# show keg indicator
				print "things"
		# delay for 50 milliseconds before going into loop again
		sleep(.05)
	except KeyboardInterrupt:
		break







