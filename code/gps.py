# FRAT gps.py - By: jclom - Tue Nov 7 2023

from machine import Pin, UART
from micropygps import MicropyGPS
import utime, time

class gpsModule():

    def __init__(self, uart_bus=1, baudrate=9600):
        self.uart = UART(uart_bus, baudrate)
        time.sleep_ms(50)
        self.latitude = [0, 0.0, 'N']
        self.longitude = [0, 0.0, 'W']
        self.satellites = 0
        self.GPStime = [0, 0, 0.0]
        self.altitude = 0.0
        self.valid = False
        self.data = bytearray(255)
        self.parser = MicropyGPS()
    
    def gps_read(self):
        timeout = time.time() + 8
        self.uart.readline()
        self.data = str(self.uart.readline())
        for x in self.data:
            self.parser.update(x)
        
        self.latitude = self.parser.latitude
        self.longitude = self.parser.longitude
        self.valid = self.parser.valid
        self.altitude = self.parser.altitude
        self.satellites = self.parser.satellites_in_use
        self.GPStime = self.parser.timestamp

        if (time.time() > timeout):
            return False
        
        utime.sleep_ms(10)
        return True
    
    def get_latitude(self):
        return self.latitude
    
    def get_longitude(self):
        return self.longitude
    
    def get_valid_data(self):
        return self.valid
    
    def get_altitude(self):
        return self.altitude
    
    def get_satellite_count(self):
        return self.satellites
    
    def get_GPS_time(self):
        return self.GPStime
    

