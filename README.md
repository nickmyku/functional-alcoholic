functional-alcoholic
====================

A notification system to alert you when your keg is getting low, one less thing to remember in your high functioning alcoholic lifestyle!

install the supporting packages
```
sudo apt-get update
sudo apt-get install build-essential python-dev python-pip
sudo pip install RPi.GPIO
```

To install python imaging tools and smbus library which are used for generating text/images on the OLED and communicating with the screen
```
sudo apt-get install python-imaging python-smbus
```

install OLED library
```
sudo apt-get install git
git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
cd Adafruit_Python_SSD1306
sudo python setup.py install
```
