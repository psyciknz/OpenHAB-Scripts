import RPi.GPIO as GPIO
import sys
import time
import json
import homie
import random
import argparse
import logging




def main(configfile="homie-python.json"):
     global fan
     global Homie
     global switchNode
     json_data=open(configfile).read()
     data = json.loads(json_data)
     fanMouth = data["relay"]["pin"]
     logname = data["relay"]["log"]
     logging.basicConfig(filename=logname, level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

     turnedon = 0
     logging.info("Setting up GPIO ports")
     GPIO.setwarnings(False)
     GPIO.setmode(GPIO.BCM) ## Indicates which pin numbering configuration to use
     print("Setting up GPIO ports")
     GPIO.setup(fanMouth, GPIO.OUT)
     GPIO.output(fanMouth,GPIO.HIGH)

     fan = GPIO.PWM(fanMouth, 100)
     logging.info("GPIO ports set up on port %s" % fanMouth)
     print("GPIO ports set up on port %s" % fanMouth)
  

     fan.start(0)         
     PAUSE_TIME = 60.02

     logging.info("Starting homie")
     print("Starting homie")
     Homie = homie.Homie(configfile)
     switchNode = Homie.Node("switch","switch")
     Homie.setFirmware("fancontrol","1.0.0")
     Homie.subscribe(switchNode, "on", switchOnHandler)
     logging.info("Running setup")
     print("Running setup")
     Homie.setup()
     print Homie
     print switchNode

     while True:
         try:
            time.sleep(1)
         except Exception,e:
	    # Error appending data, most likely because credentials are stale.
	    # Null out the worksheet so a login is performed at the top of the lo
	    logging.error("Error in mqtt loop")
            print('Append error, logging in again: ' + str(e))
	    continue


	 except KeyboardInterrupt:
	    print("error")
	    GPIO.cleanup()
	    exit(0)

# The callback for when a PUBLISH message is received from the server.
def switchOnHandler(mqttc, obj, msg):
        global fan
        global Homie
	global switchNode
   	print('topic')
	logging.info('Topic: ' +  msg.topic+'  Message: '+str(msg.payload))
	print('Topic: ' +  msg.topic+'  Message: '+str(msg.payload))
        if msg.payload == "1" or msg.payload == "true" or msg.payload == "ON" or msg.payload == "on":
		print 'turning fan on'
		logging.info("Turning Fan on")
		fan.ChangeDutyCycle(100)
		Homie.setNodeProperty(switchNode,"on" "false", True)
	else:
		logging.info("Turning fan off")
		print 'turning fan off'
		fan.ChangeDutyCycle(0)
		Homie.setNodeProperty(switchNode, "on" "false", True)



if __name__ == '__main__':
    try:
        parser= argparse.ArgumentParser(description="Homie Based Fan Control")
        parser.add_argument('-c','--configfile', help='Configuration filename (json)',required=True)
        args = parser.parse_args()
        main(args.configfile)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Quitting.")
