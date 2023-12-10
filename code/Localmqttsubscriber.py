import time
import paho.mqtt.client as mqtt

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
    client.subscribe(topic_gps)
    client.subscribe(topic_temp)
    client.subscribe(topic_humidity)
    

def on_message(client, userdata, msg):
     print("Message received: " + msg.payload.decode('utf-8'))

client = mqtt.Client('fratPi')

client.on_Connect = on_connect
client.on_message = on_message

client.connect(hostname, broker_port, 60)

client.loop_start()

try:
 
    while True:
        
        

        time.sleep(1)
    


except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    client.loop_stop()
    print("Done.\nExiting.")