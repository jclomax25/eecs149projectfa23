# FRAT main.py - By: jclom - Mon Nov 6 2023

import sensor, fir
import machine

import sdcard
import uos

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(9, machine.Pin.OUT)

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
