import SHT30 as driver
import sys
import argparse
import time
import json
from gps import *
import time
import paho.mqtt.client as mqtt
import math

IMAGE_CENTER_X = 400
IMAGE_CENTER_Y = 300 
THERM_CENTER_X = 16
THERM_CENTER_Y = 12
local_elevation = 150
pixel_width = 0
pixel_height = 0
altitude = 0
latitude = 0.0
longitude = 0.0
temperature = 0
humidity = 0
wind_speed = 0

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 

hostname = '192.'
broker_port = 1883
topic_wind = "fratPi/wind"
topic_gps = "fratPi/gps"
topic_temp = "fratPi/temp"
topic_humidity = "fratPi/humidity"
topic_image = "fratPi/image"
topic_map = "fratPi/map"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code: " + str(rc))
    

def on_message(client, userdata, msg):
     print("Message received: " + msg.payload.decode('utf-8'))

client = mqtt.Client('fratPi')

client.on_Connect = on_connect
client.on_message = on_message

client.connect(hostname, broker_port, 60)

client.loop_start()

try:
 
    while True:
        
        report = gpsd.next() #
        sensor = driver.SHT30()
        data = []

        if not sensor.is_plugged():
            print("SHT30 is not plugged!")
        if report['class'] == 'TPV':

            latitude = getattr(report,'lat',0.0)
            longitude = getattr(report,'lon',0.0)
            altitude = getattr(report,'alt','nan')
            print(latitude,"\t",)
            print(longitude,"\t",)
            print(getattr(report,'time',''),"\t",)
            print(altitude,"\t\t",)
            print(getattr(report,'epv','nan'),"\t",)
            print(getattr(report,'ept','nan'),"\t",)
            print(getattr(report,'speed','nan'),"\t",)
            print(getattr(report,'climb','nan'),"\t")
        
        if altitude != 0:
            pixel_width = math.tan(55/2)*(altitude-local_elevation)*2/32/800
            pixel_height = math.tan(35/2)*(altitude-local_elevation)*2/24/600

        temperature, humidity = sensor.measure()
        print('Temperature:', temperature, 'ºC, RH:', humidity, '%')
        print("SHT30 status:")
        print(sensor.status())
        msg = str(temperature)
        info = client.publish(topic='fratPi/temp', payload=msg.encode('utf-8'), qos=0)
        info.wait_for_publish()
        msg = str(humidity)
        info = client.publish(topic='fratPi/humidity', payload=msg.encode('utf-8'), qos=0)
        info.wait_for_publish()
        msg = "lat"+str(latitude) +",lon"+str(longitude)+",alt"+str(altitude)
        info = client.publish(topic='fratPi/gps', payload=msg.encode('utf-8'), qos=0)
        info.wait_for_publish()

        time.sleep(1)
    


except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    client.loop_stop()
    print("Done.\nExiting.")