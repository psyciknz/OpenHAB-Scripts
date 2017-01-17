import RPi.GPIO as GPIO
import sys
from time import sleep
import random
import paho.mqtt.client as mqtt
import logging



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print('topic')
	logging.info('Topic: ' +  msg.topic+'  Message: '+str(msg.payload))
	print('Topic: ' +  msg.topic+'  Message: '+str(msg.payload))
        if msg.payload == "1":
		print 'turning fan on'
		logging.info("Turning Fan on")
		fan.ChangeDutyCycle(100)
		(result1,mid) = client.publish("cupboard/fanstate","ON")
		print "After mqtt: %d mid: %d" %(result1 , mid)
	else:
		logging.info("Turning fan off")
		print 'turning fan off'
		fan.ChangeDutyCycle(0)
		client.publish("cupboard/fanstate",0)
		(result1,mid) = client.publish("cupboard/fanstate","OFF")
		print "After mqtt: %d mid: %d" %(result1 , mid)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
	logging.info("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe('cupboard/fan',1)

logging.basicConfig(filename="/var/log/fancontrol.log", level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) ## Indicates which pin numbering configuration to use

MOSQUITTO_HOST = 'mqttserver'
MOSQUITTO_PORT = 1883

fanMouth = 18
turnedon = 0
logging.info("Setting up GPIO ports")
print("Setting up GPIO ports")
GPIO.setup(fanMouth, GPIO.OUT)
GPIO.output(fanMouth,GPIO.HIGH)

fan = GPIO.PWM(fanMouth, 100)

fan.start(0)         
PAUSE_TIME = 60.02

print('Receiving commands to start stop fan')
print('Press Ctrl-C to quit.')
logging.info('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
print('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT)
while True:
	try:
		mqttc.loop_forever()

	except Exception,e:
		# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the lo
		logging.error("Error in mqtt loop")
		mqttc.disconnect()
		mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT)
		print('Append error, logging in again: ' + str(e))
		continue


	except KeyboardInterrupt:
		print("error")
		GPIO.cleanup()
		exit(0)

