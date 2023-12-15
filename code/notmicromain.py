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
import busio, board
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


local_elevation = 15
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

i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code: " + str(rc))

def on_log(client, userdata, level, buf):
    print("log: ", buf)

def _c_to_f(temp:float):
        """ Convert temperature from C to F """
        return ((9.0/5.0)*temp+32.0)

client = mqtt.Client("frat1")

output_folder = '/home/johnlomax/Desktop/Imagery'

thermcam = pithermalcam(output_folder=output_folder)

client.connect(host=hostname1)

client.on_Connect = on_connect
#client.on_log=on_log
f = open("data.txt", "w")

try:
 
    while True:
        
        sensor = driver.SHT30()
        
        data = []
        
        if not sensor.is_plugged():
            print("SHT30 is not plugged!")
        if 0 == gpsd.read() and gpsd.valid:
            report = gpsd.next()
            if report['class'] == 'TPV':
                
                latitude = getattr(report,'lat',0.0)
                longitude = getattr(report,'lon',0.0)
                altitude = getattr(report,'alt', 0.0)
                #print(latitude,"\t",)
                #print(longitude,"\t",)
                #print(getattr(report,'time','None'),"\t",)
                #print(altitude,"\t\t",)
                #print(getattr(report,'epv','nan'),"\t",)
                #print(getattr(report,'ept','nan'),"\t",)
                #print(getattr(report,'speed','nan'),"\t",)
                #print(getattr(report,'climb','nan'),"\t")
                print(f"Latitude: {latitude}º, Longitude: {longitude}º, Altitude: {altitude} m")
        
        if not altitude <= 0 and altitude != 'nan':
            
            pixel_width = math.tan(55/2)*(altitude-local_elevation)*2/32/800
            pixel_height = math.tan(35/2)*(altitude-local_elevation)*2/24/600

        thermcam.display_next_frame_onscreen(pw=pixel_width, ph=pixel_height, lat=latitude,lon=longitude)
        
        temperature, humidity = sensor.measure()
        
        print('Temperature:', temperature, 'ºC, RH:', humidity, '%')
        wind = chan.voltage
        print("{:>5}\t{:>5.3f}".format(chan.value, wind))
        #print("SHT30 status:")
        sensor.status()
        wind_conv = 14.28*(wind - 0.45)

        msg1 = str(round(wind, 2))+" mph"
        print("Publishing Wind")
        info = client.publish(topic="fratPi/wind", payload=msg1.encode('utf-8'), qos=0)

        msg2 = str(round(temperature, 2))+" ºC"
        print("Publishing Temperature")
        info = client.publish(topic="fratPi/temp", payload=msg2.encsode('utf-8'), qos=0)
        
        #humidity = 34.05
        msg3 = str(round(humidity, 2))+" %"
        print("Publishing Humidity")
        info = client.publish(topic="fratPi/humidity", payload=msg3.encode('utf-8'), qos=0)
        
        
        #latitude=37.8731096667
        #longitude=-122.259815

        msg4 = "lat: "+str(latitude) +" , lon: "+str(longitude)+" , alt: "+str(altitude)
        print("Publishing GPS")
        info = client.publish(topic="fratPi/gps", payload=msg4.encode('utf-8'), qos=0)

        f.write(msg1+"\n" + msg2+"\n"+msg3+"\n"+msg4+"\n")

        time.sleep(10)
    


except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("Done.\nExiting.")

f.close()

gpsd.close()