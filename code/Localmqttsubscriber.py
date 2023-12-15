import time
import paho.mqtt.client as mqtt

hostname = "127.0.1.1"
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

def on_log(client, userdata, level, buf):
    print("log: ", buf)

client = mqtt.Client('frat2')

client.on_Connect = on_connect
client.on_message = on_message
#client.on_log=on_log

client.connect(hostname)
client.subscribe("fratPi/gps")
client.subscribe("fratPi/temp")
client.subscribe("fratPi/humidity")
client.loop_forever()
