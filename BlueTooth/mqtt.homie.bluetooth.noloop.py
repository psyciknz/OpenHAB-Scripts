# Blue Maestro Tempo Disk Scanner for MQTT
# Takes all values from the scanned tempo disc and using the MAC id pushes each topic into MQTT
# requires paho.mqtt client and bluez.
# Also requires bluemaestroscan.py in th esame directory as this has the specifics for decoding
#  the advertising packets for the Blue Maestro Tempo Disc https://www.bluemaestro.com/product/tempo-disc-temperature/
# Unsure if there are any other Blue Maetro products that it would work with.
# David@andc.nz 15/12/2016


# Credit jcs 6/8/2014 as basis

import bluemaestroscan  #specific bluemaestro tempo disc scanner
import json
import sys
import argparse
import time
import homie
import bluetooth._bluetooth as bluez

dev_id = 0
FREQUENCY_SECONDS = 600

def main(configfile='homie-bluetooth.json'):
	Homie = homie.Homie(configfile)
	Homie.setFirmware("bluemaestro-temperature","1.0.0")
	Homie.setup()

	try:
		sock = bluez.hci_open_dev(dev_id)
		print "ble thread started"

	except:
		print "error accessing bluetooth device..."
	    	sys.exit(1)
	
	bluemaestroscan.hci_le_set_scan_parameters(sock)
	bluemaestroscan.hci_enable_le_scan(sock)


	try:
		returnedList = bluemaestroscan.parse_events(sock, 2)
                nodes = {}
		print "-------------------------------------------------------------------------------------------------------"
		mac = ""
		temp = 0
		currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
		print('Date Time:   {0}'.format(currentdate))
		for beacon in returnedList:
			val = returnedList[beacon]
			print beacon, val
			mac = returnedList["mac"]
			temp = returnedList["temp"]
		
			print "number of beacons found {0}".format(len(returnedList))
			if len(returnedList) > 0:
				print "%s/temperature = %.2f" % (returnedList["mac"],returnedList["temp"])
				# Publish to the MQTT channel
				try:
					temperatureNode = Homie.Node(mac,"temperature")
					Homie.setNodeProperty(temperatureNode,"temperature",float(returnedList["temp"]),True)
		        		print 'Updating temp for {0} to {1}'.format(returnedList["mac"],float(returnedList["temp"]))
					humidityNode = Homie.Node(mac,"humidity")
					Homie.setNodeProperty(humidityNode,"humidity",float(returnedList["humidity"]),True)
	       				print  'Updating humidity {0} = {1}'.format(returnedList["mac"],float(returnedList["humidity"]))
					batteryNode = Homie.Node(mac,"battery")
					Homie.setNodeProperty(batteryNode,"battery",float(returnedList["battery"]),True)
					print 'Updating battery {0}/battery = {1}'.format(returnedList["mac"],float(returnedList["battery"]))
					dewpointNode = Homie.Node(mac,"dewpoint")
					Homie.setNodeProperty(dewpointNode,"dewpoint",float(returnedList["dewpoint"]),True)
					print  'Updating {0}/dewpoint = {1}'.format( returnedList["mac"],returnedList["dewpoint"])
					nameNode = Homie.Node(mac,"name")
					Homie.setNodeProperty(nameNode,"name",returnedList["name"],True)
					print  'Updating name {0}/name = {1}'.format(returnedList["mac"],returnedList["name"])
					time.sleep(1)

					print "Sleeping for %d seconds" % FREQUENCY_SECONDS

				except Exception,e:
					# Null out the worksheet so a login is performed at the top of the loop.
					print('Append error, logging in again: ' + str(e))
					print "Sleeping for 60 seconds"

	except Exception,e:
       	# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		print('Append error, logging in again: ' + str(e))
		print "Sleeping for 60 seconds"

if __name__ == '__main__':
    try:
        parser= argparse.ArgumentParser(description="Homie Based Bluetooth Reader")
        parser.add_argument('-c','--configfile', help='Configuration filename (json)',required=True)
        args = parser.parse_args()
        main(args.configfile)
    except (KeyboardInterrupt, SystemExit):
        print "quitting."

