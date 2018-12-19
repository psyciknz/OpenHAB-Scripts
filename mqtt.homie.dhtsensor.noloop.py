#!/usr/bin/python
# DHT Sensor Data-logging to MQTT Temperature channel

# Requies a Mosquitto Server Install On the destination.

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
# MQTT Encahncements: David Cole (2016)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
import requests
import sys
import argparse
import time
import datetime
import homie
import Adafruit_DHT

#================================================================================================================================================== 
#Usage python mqtt.channel.py <temp topic> <humidity topic> <gpio pin> <optional update frequency># Type of sensor, can be 
#Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
# eg python mqtt.channel.py 'cupboard/temperature1' 'cupboard/humidity1' 4DHT_TYPE = Adafruit_DHT.DHT22 will start an instance using 
#'cupboard/temperature1' as the temperature topic, and using gpio port 4 to talk to a DHT22 sensor Example of sensor connected to 
#Raspberry Pi pin 23 it will use the default update time of 300 secons.DHT_PIN = sys.argv[3] Example of sensor connected to Beaglebone 
#Black pin P8_11 DHT_PIN = 'P8_11'
#==================================================================================================================================================
# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT22

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = 4
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'


# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 200

def main(configfile='homie-dht.json'):
    Homie = homie.Homie(configfile)
    temperatureNode = Homie.Node("temperature","temperature")
    humidityNode = Homie.Node("humidity","humidity")

    json_data=open(configfile).read()
    data = json.loads(json_data)
    FREQUENCY_SECONDS =data["dht"]["frequency"]
    DHT_PIN =  data["dht"]["pin"]
    print('Logging sensor measurements to mqtt.')
    Homie.setFirmware("dht-temperature","1.0.0")
    Homie.setup()
    try:
        # Attempt to get sensor reading.
        notfound = True
        while notfound:
            print('Performing read on dht')
            humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
            print('After dht read')

            # Skip to the next reading if a valid measurement couldn't be taken.
            # This might happen if the CPU is under a lot of load and the sensor
            # can't be reliably read (timing is critical to read the sensor).
            if humidity is None or temp is None:
               time.sleep(2)
               print "Nothing received from sensor"
            else:
               notfound = False

        currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
        print('Date Time:   {0}'.format(currentdate))
        print('Temperature: {0:0.2f} C'.format(temp))
        print('Humidity:    {0:0.2f} %'.format(humidity))

        # Publish to the MQTT channel
        print('Connecting to host')
        print("Posting Temperature to homie")
        Homie.setNodeProperty(temperatureNode,"degrees",temp,True)
        Homie.setNodeProperty(humidityNode,"humidity",humidity,True)

    except Exception,e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error, logging in again: ' + str(e))
    else:
        # Wait 30 seconds before continuing
        print('Wrote a message tp MQQTT')

if __name__ == '__main__':
    try:
        parser= argparse.ArgumentParser(description="Homie Based DHT Reader")
        parser.add_argument('-c','--configfile', help='Configuration filename (json)',required=True)
        args = parser.parse_args()
        main(args.configfile)
    except (KeyboardInterrupt, SystemExit):
        print "quitting."

