# Blue Maestro Tempo Disk Scanner for MQTT
# Takes all values from the scanned tempo disc and using the MAC id pushes each topic into MQTT
# requires paho.mqtt client and bluez.
# Also requires bluemaestroscan.py in th esame directory as this has the specifics for decoding
#  the advertising packets for the Blue Maestro Tempo Disc https://www.bluemaestro.com/product/tempo-disc-temperature/
# Unsure if there are any other Blue Maetro products that it would work with.
# David@andc.nz 15/12/2016


# Credit jcs 6/8/2014 as basis

import bluemaestroscan  #specific bluemaestro tempo disc scanner
import sys
import time
import paho.mqtt.client as mqtt
import bluetooth._bluetooth as bluez

dev_id = 0
FREQUENCY_SECONDS = 600
MOSQUITTO_HOST = 'frodo.lan'
MOSQUITTO_PORT = 1883

try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)
print('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
mqttc = mqtt.Client("python_pub")
bluemaestroscan.hci_le_set_scan_parameters(sock)
bluemaestroscan.hci_enable_le_scan(sock)


while True:
	try:
		returnedList = bluemaestroscan.parse_events(sock, 2)
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
				mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT);
		        	print 'Updating temp for {0} to {1}'.format(returnedList["mac"],float(returnedList["temp"]))
				(result1,mid) = mqttc.publish("%s/temperature" % returnedList["mac"],float(returnedList["temp"]))
				time.sleep(1)

				mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT);
				(result2,mid) =  mqttc.publish("%s/humidity" % returnedList["mac"],float(returnedList["humidity"]))
        			print  'Updating humidity {0} = {1}'.format(returnedList["mac"],float(returnedList["humidity"]))
				time.sleep(1)
                                
				mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT);
				(result3,mid) =  mqttc.publish("%s/dewpoint" % returnedList["mac"],float(returnedList["dewpoint"]))
				print  'Updating {0}/dewpoint = {1}'.format( returnedList["mac"],returnedList["dewpoint"])
				time.sleep(1)

				mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT);
				(result4,mid) =  mqttc.publish("%s/name" % returnedList["mac"],returnedList["name"])
				print  'Updating name {0}/name = {1}'.format(returnedList["mac"],returnedList["name"])
				time.sleep(1)

				mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT);
				(result5,mid) =  mqttc.publish("%s/battery" % returnedList["mac"],float(returnedList["battery"]))
				print 'Updating battery {0}/battery = {1}'.format(returnedList["mac"],float(returnedList["battery"]))
				print 'Updated Battery'
	        		#print 'MQTT Updated result {0} and {1} and {2} and {3} and {4} and {5}'.format(result1,result2,result3,result4,result5)

				if result1 == 1 or result2 == 1 or result3 == 1 or result4 == 1 or result5 ==1:
					raise ValueError('Result for one message was not 0')
#				mqttc.disconnect()
				print "Sleeping for %d seconds" % FREQUENCY_SECONDS
				time.sleep(FREQUENCY_SECONDS)
				mqttc.loop(1)


			except Exception,e:
				# Null out the worksheet so a login is performed at the top of the loop.
				mqttc.disconnect()
				print('Append error, logging in again: ' + str(e))
				print "Sleeping for 60 seconds"
				time.sleep(60)
				continue
		else:
			print "Sleeping for 30 seconds" 
			time.sleep(30)
	except Exception,e:
       	# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		print('Append error, logging in again: ' + str(e))
		print "Sleeping for 60 seconds"
		time.sleep(60)
		continue

