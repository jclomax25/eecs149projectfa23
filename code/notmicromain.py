import SHT30 as driver
import sys
import argparse
import time
import json
from gps import *
import time
import paho.mqtt.client as mqtt
import math
from pi_therm_cam import pithermalcam
#import rasterio as rio
from pyproj import Proj, transform
#import gdal, osr


local_elevation = 70
pixel_width = 0
pixel_height = 0
altitude = 0
latitude = 0.0
longitude = 0.0
temperature = 0
humidity = 0
wind_speed = 0

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE) 

hostname1 = "127.0.1.1"
broker_port = 1883
topic_wind = "fratPi/wind"
topic_gps = "fratPi/gps"
topic_temp = "fratPi/temp"
topic_humidity = "fratPi/humidity"
topic_image = "fratPi/image"
topic_map = "fratPi/map"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code: " + str(rc))

def on_log(client, userdata, level, buf):
    print("log: ", buf)

client = mqtt.Client("frat1")

output_folder = '/home/johnlomax/Desktop/Imagery'

thermcam = pithermalcam(output_folder=output_folder)

client.connect(host=hostname1)

client.on_Connect = on_connect
#client.on_log=on_log

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
            altitude = getattr(report,'alt', 0.0)
            print(latitude,"\t",)
            print(longitude,"\t",)
            print(getattr(report,'time',''),"\t",)
            print(altitude,"\t\t",)
            print(getattr(report,'epv','nan'),"\t",)
            print(getattr(report,'ept','nan'),"\t",)
            print(getattr(report,'speed','nan'),"\t",)
            print(getattr(report,'climb','nan'),"\t")
        
        if not altitude <= 0 and altitude != 'nan':
            pixel_width = math.tan(55/2)*(altitude-local_elevation)*2/32/800
            pixel_height = math.tan(35/2)*(altitude-local_elevation)*2/24/600

        thermcam.display_next_frame_onscreen(pw=pixel_width, ph=pixel_height, lat=latitude,lon=longitude)

        temperature, humidity = sensor.measure()
        print('Temperature:', temperature, 'ºC, RH:', humidity, '%')
        print("SHT30 status:")
        print(sensor.status())
        msg = str(round(temperature, 2))+" ºC"
        info = client.publish(topic="fratPi/temp", payload=msg.encode('utf-8'), qos=0)
        
        msg = str(round(humidity, 2))+" %"
        info = client.publish(topic="fratPi/humidity", payload=msg.encode('utf-8'), qos=0)
        
        msg = "lat: "+str(latitude) +", lon: "+str(longitude)+", alt: "+str(altitude)
        info = client.publish(topic="fratPi/gps", payload=msg.encode('utf-8'), qos=0)
        

        time.sleep(1)
    


except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("Done.\nExiting.")