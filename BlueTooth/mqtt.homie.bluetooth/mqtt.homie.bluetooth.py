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
import logging
import homie
import bluetooth._bluetooth as bluez

dev_id = 0
FREQUENCY_SECONDS = 600
LOG = "/var/log/mqtt.home.bluetooth.log"

def updatenode(Homie, nodelist,mac,nodevalue,newvalue):
	if mac+nodevalue in nodelist:
		logging.info("Found existing " + nodevalue + " node: " +  mac)
		print("Found existing " + nodevalue + " node: " + mac)
		currentNode = nodelist[mac+nodevalue]
		print ("Obtained node for updating " + mac)
		Homie.setNodeProperty(currentNode,nodevalue,newvalue,True)
	else:
		logging.info("Added new " + nodevalue + "for mac " + mac)
		print("Adding new " + nodevalue + "node for mac " + mac)
		currentNode = Homie.Node(mac,nodevalue)
		Homie.setNodeProperty(currentNode,nodevalue,newvalue,True)
		nodelist[mac+nodevalue] = currentNode
		print("Added new " + nodevalue + " node for mac" + mac)


def main(configfile='homie-bluetooth.json'):
	Homie = homie.Homie(configfile)
	Homie.setFirmware("bluemaestro-temperature","1.0.1")
	Homie.setup()
	json_data=open(configfile).read()
	data = json.loads(json_data)
	FREQUENCY_SECONDS =data["bluetooth"]["frequency"]
	LOG = data["bluetooth"]["log"]
	logging.basicConfig(filename=LOG, level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')   


	try:
		sock = bluez.hci_open_dev(dev_id)
		logging.info("ble thread started")

	except:
		print( "error accessing bluetooth device...")
		logging.info("error accessing bluetooth device...")
		sys.exit(1)
	
	bluemaestroscan.hci_le_set_scan_parameters(sock)
	bluemaestroscan.hci_enable_le_scan(sock)


	while True:
		try:
			returnedList = bluemaestroscan.parse_events(sock, 2)
			nodes = {}
			print("-------------------------------------------------------------------------------------------------------")
			logging.info("-------------------------------------------------------------------------------------------------------")
			mac = ""
			temp = 0
			currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
			print('Date Time:   {0}'.format(currentdate))
			logging.info('Date Time:   {0}'.format(currentdate))
			for beacon in returnedList:
				val = returnedList[beacon]
				print( beacon, val)
				mac = returnedList["mac"]
				temp = returnedList["temp"]
		
				print("number of beacons found {0}".format(len(returnedList)))
				logging.info("number of beacons found {0}".format(len(returnedList)))
				if len(returnedList) > 0:
					print("%s/temperature = %.2f" % (returnedList["mac"],returnedList["temp"]))
					logging.info("%s/temperature = %.2f" % (returnedList["mac"],returnedList["temp"]))
					# Publish to the MQTT channel
					try:
						print("CHecking nodes for " + mac+"temperature")
						updatenode(Homie, nodes,mac,"temperature",float(returnedList["temp"]))

						#if mac+"temperature" in nodes:
						#	logging.info("Found existing temperature node: " +  mac+"temperature")
						#	print("Found existing temperature node: " + mac+"temperature")
						#	temperatureNode = nodes[mac+"temperature"]
						#	print ("Obtained temperature node for updating")
						#	Homie.setNodeProperty(tempNode,"temperature",float(returnedList["temp"]),True)
						#else:
						#	logging.info("Added new temperature node for mac" + mac)
						#	print("Adding new temperature node for mac" + mac)
						#	temperatureNode = Homie.Node(mac,"temperature")
						#	Homie.setNodeProperty(temperatureNode,"temperature",float(returnedList["temp"]),True)
						#	nodes[mac+"temperature"] = temperatureNode
						#	print("Added new temperature node for mac" + mac)
						print('Updating temp for {0} to {1}'.format(returnedList["mac"],float(returnedList["temp"])))
						logging.info('Updating temp for {0} to {1}'.format(returnedList["mac"],float(returnedList["temp"])))

						print("CHecking nodes for " + mac+"humidity")
						updatenode(Homie, nodes,mac,"humidity",float(returnedList["humidity"]))
						#humidityNode = Homie.Node(mac,"humidity")
						#Homie.setNodeProperty(humidityNode,"humidity",float(returnedList["humidity"]),True)
						print ( 'Updating humidity {0} = {1}'.format(returnedList["mac"],float(returnedList["humidity"])))
						logging.info('Updating humidity {0} = {1}'.format(returnedList["mac"],float(returnedList["humidity"])))
						
						print("CHecking nodes for " + mac+"battery")
						updatenode(Homie, nodes,mac,"battery",float(returnedList["battery"]))

						#batteryNode = Homie.Node(mac,"battery")
						#Homie.setNodeProperty(batteryNode,"battery",float(returnedList["battery"]),True)
						print ('Updating battery {0}/battery = {1}'.format(returnedList["mac"],float(returnedList["battery"])))
						logging.info('Updating battery {0}/battery = {1}'.format(returnedList["mac"],float(returnedList["battery"])))
						
						print("CHecking nodes for " + mac+"dewpoint")
						updatenode(Homie, nodes,mac,"dewpoint",float(returnedList["dewpoint"]))
						#dewpointNode = Homie.Node(mac,"dewpoint")
						#Homie.setNodeProperty(dewpointNode,"dewpoint",float(returnedList["dewpoint"]),True)
						print( 'Updating {0}/dewpoint = {1}'.format( returnedList["mac"],returnedList["dewpoint"]))
						logging.info('Updating {0}/dewpoint = {1}'.format( returnedList["mac"],returnedList["dewpoint"]))
						
						print("CHecking nodes for " + mac+"name")
						updatenode(Homie, nodes,mac,"name",returnedList["name"])

						#nameNode = Homie.Node(mac,"name")
						#Homie.setNodeProperty(nameNode,"name",returnedList["name"],True)
						print ( 'Updating name {0}/name = {1}'.format(returnedList["mac"],returnedList["name"]))
						logging.info('Updating name {0}/name = {1}'.format(returnedList["mac"],returnedList["name"]))
						time.sleep(1)

					except Exception as e:
						# Null out the worksheet so a login is performed at the top of the loop.
						logging.error('Append error, logging in again: ' + str(e))
						logging.error("Sleeping for 60 seconds")
						time.sleep(60)
						continue
				else:
					print ("Sleeping for 30 seconds" )
					logging.info("Sleeping for 30 seconds" )
					time.sleep(30)
					logging.info("Sleeping for %s seconds" % FREQUENCY_SECONDS)
					print("Sleeping for %s seconds" % FREQUENCY_SECONDS)
			time.sleep(FREQUENCY_SECONDS)

		except Exception as e:
		   	# Error appending data, most likely because credentials are stale.
			# Null out the worksheet so a login is performed at the top of the loop.
			print('Append error, logging in again: ' + str(e))
			print ("Sleeping for 60 seconds")
			time.sleep(60)
			continue

if __name__ == '__main__':
	try:
		parser= argparse.ArgumentParser(description="Homie Based Bluetooth Reader")
		parser.add_argument('-c','--configfile', help='Configuration filename (json)',required=True)
		args = parser.parse_args()
		main(args.configfile)
	except (KeyboardInterrupt, SystemExit):
		print ("quitting.")

