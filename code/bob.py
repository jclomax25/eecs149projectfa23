# FRAT main.py - By: John Cole Lomax - Mon Nov 6 2023

#import sensor, fir
import machine
from micropyGPS import MicropyGPS
from SHT30 import SHT30
from gps import gpsModule
import time

import sdcard
import uos

led = machine.Pin(6, machine.Pin.OUT)
tim = machine.Timer()
def tick(timer):
    global led
    led.toggle()

tim.init(freq=2, mode=machine.Timer.PERIODIC, callback=tick)

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(9, machine.Pin.OUT)

# Create GPS UART connection
gps_mod = gpsModule(0, baud_rate=9600)
"""
#gps_mod = machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, timeout=300)
#uart0= machine.UART(0, baudrate=9600, bits=8, parity=None, stop=1, tx=machine.Pin(0), rx=machine.Pin(1), timeout=300)

#  do a loop-back test first

msg = 'Test'
#uart0.write(msg)
print ('message written')
while True:
    #uart0.write(msg)
    new_msg = uart0.readline()
    print (new_msg)
"""
# Create i2c bus
temp = SHT30(scl_pin=13, sda_pin=12) #machine.I2C(id=0, scl=machine.Pin(13), sda=machine.Pin(12), freq=100_000) #SHT30(scl_pin=13, sda_pin=12)
"""print("trying")
print("started")
temp.writeto(0x44, b'\x2C\x10')
print("wrote")
if not 6:
    temp.stop()
    return
time.sleep_ms(50)
data = temp.readfrom(0x44, 6)
print("read")"""
"""
# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(8))

# Initialize SD card
sd = sdcard.SDCard(spi, cs)

# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

# Create a file and write something to it
with open("/sd/test01.txt", "w") as file:
    file.write("Hello, SD World!\r\n")
    file.write("This is a test\r\n")

# Open the file we just created and read from it
with open("/sd/test01.txt", "r") as file:
    data = file.read()
    print(data)
"""

while(True):
    print(gps_mod.gps_read())
    print(gps_mod.get_valid_data())
    print(gps_mod.get_latitude())
    print(gps_mod.get_longitude())
    print(gps_mod.get_satellite_count())
    if(temp.is_present()):
        print(temp.measure())
    time.sleep_ms(1000)

"""
# Setup Thermal Camera.
fir.init(fir.FIR_MLX90640)

# Show image.
while(True):
    ta, ir, to_min, to_max = fir.read_ir()
    image = fir.snapshot()
    fir.draw_ir(image, ir)
    print("====================")
    print("Ambient temperature: %0.2f" % ta)
    print("Min temperature seen: %0.2f" % to_min)
    print("Max temperature seen: %0.2f" % to_max)
    print("hello")
"""
