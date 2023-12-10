#!/usr/bin/python3
from smbus2 import SMBus
import time

__version__ = '1.0.0'
__author__ = 'Morskov Maksim'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

DEFAULT_I2C_ADDRESS = 0x44


class SHT30:
    """
    SHT30 sensor driver in python based on I2C bus

    References:
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf  # NOQA
    * https://www.wemos.cc/sites/default/files/2016-11/SHT30-DIS_datasheet.pdf
    * https://github.com/wemos/WEMOS_SHT3x_Arduino_Library
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/11_Sample_Codes_Software/Humidity_Sensors/Sensirion_Humidity_Sensors_SHT3x_Sample_Code_V2.pdf
    """
    POLYNOMIAL = 0x131  # P(x) = x^8 + x^5 + x^4 + 1 = 100110001

    # See Datasheet chapter 2.2
    REPEATABILITY_HIGH = 1
    REPEATABILITY_MEDIUM = 2
    REPEATABILITY_LOW = 3

    # MSB = 0x2C LSB = 0x06 Repeatability = High, Clock stretching = enabled
    # MEASURE_CMD = b'\x2C\x10'
    STATUS_CMD = b'\xF3\x2D'
    RESET_CMD = b'\x30\xA2'
    CLEAR_STATUS_CMD = b'\x30\x41'
    ENABLE_HEATER_CMD = b'\x30\x6D'
    DISABLE_HEATER_CMD = b'\x30\x66'
    BREAK_CMD = b'\x30\x93'  # Break   command   /   Stop   PeriodicData Acquisition Mode
    ACCELERATED_RESPONSE_TIME_CMD = b'\x2B\x32'

    def __init__(self, bus_num=4, delta_temp=0, delta_hum=0, i2c_address=DEFAULT_I2C_ADDRESS):
        self.i2c_bus_num = bus_num
        self.i2c_addr = i2c_address
        self.set_delta(delta_temp, delta_hum)
        time.sleep(0.2)

    def __get_i2c_devs(self, start=0x03, end=0x78) -> tuple:
        """
        Lists all working devices on bus
        """
        devs = []
        with SMBus(self.i2c_bus_num) as bus:
            time.sleep(0.5)
            for i in range(start, end):
                val = 1
                try:
                    bus.read_byte(i)
                except OSError as e:
                    val = e.args[0]
                finally:
                    if val != 5:  # No device
                        if val == 1 or val == 16:
                            devs.append(i)
        return tuple(devs)

    def is_plugged(self):
        """
        Return true if the sensor is correctly conneced, False otherwise
        """
        devs = []
        with SMBus(self.i2c_bus_num) as bus:
            time.sleep(0.5)
            val = 1
            try:
                bus.read_byte(self.i2c_addr)
            except OSError as e:
                val = e.args[0]
            finally:
                if val != 5:  # No device
                    if val == 1 or val == 16:
                        return True
        return False

    def set_delta(self, delta_temp=0, delta_hum=0):
        """
        Apply a delta value on the future measurements of temperature and/or humidity
        The units are Celsius for temperature and percent for humidity (can be negative values)
        """
        self.delta_temp = delta_temp
        self.delta_hum = delta_hum

    @staticmethod
    def __check_crc(data):
        # calculates 8-Bit checksum with given polynomial
        crc = 0xFF

        for b in data[:-1]:
            crc ^= b
            for _ in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ SHT30.POLYNOMIAL
                else:
                    crc <<= 1
        crc_to_check = data[-1]
        return crc_to_check == crc

    def __i2c_transaction(self, register, command, response_size=6, read_delay_ms=20):
        """
        Proceeds i2c command
        """
        data = []
        with SMBus(self.i2c_bus_num) as bus:
            time.sleep(0.5)  # Or it will always be 121 error code
            bus.write_byte_data(self.i2c_addr, register, command)
            if not response_size:
                return
            time.sleep(read_delay_ms / 1000)
            data = bus.read_i2c_block_data(self.i2c_addr, register, response_size)
        return data

    def __send_cmd(self, cmd_request: bytes, response_size=6, read_delay_ms=10):
        """
        Send a command to the sensor and read (optionally) the response
        The received data is validated by CRC
        :return response data or none
        """

        register, command = list(cmd_request)
        try:
            data = self.__i2c_transaction(register, command, response_size, read_delay_ms)
            for i in range(response_size // 3):
                if not self.__check_crc(data[i * 3:(i + 1) * 3]):  # pos 2 and 5 are CRC
                    raise SHT30Error(SHT30Error.CRC_ERROR)

            if data == bytearray(response_size):
                raise SHT30Error(SHT30Error.DATA_ERROR)

            return data
        except OSError as ex:
            if 'I2C' in ', '.join([str(x) for x in ex.args]):
                raise SHT30Error(SHT30Error.BUS_ERROR)
            raise ex

    def __get_single_shot_measure_command(self, clock_stretching=True, repeatability=REPEATABILITY_HIGH):
        """
        See Datasheet, chapter 4
        :param clock_stretching: bool
        :param repeatability:
        :return: bytes
        """
        if clock_stretching:
            command = b'\x2c'
            if repeatability == self.REPEATABILITY_HIGH:
                command += b'\x06'
            elif repeatability == self.REPEATABILITY_MEDIUM:
                command += b'\x0d'
            else:
                command += b'\x10'
        else:
            command = b'\x24'
            if repeatability == self.REPEATABILITY_HIGH:
                command += b'\x00'
            elif repeatability == self.REPEATABILITY_MEDIUM:
                command += b'\x0b'
            else:
                command += b'\x16'
        return command

    def clear_status(self):
        """
        Clear the status register
        """
        return self.__send_cmd(SHT30.CLEAR_STATUS_CMD, None)

    def reset(self):
        """
        Send a soft-reset to the sensor
        """
        return self.__send_cmd(SHT30.RESET_CMD, None)

    def status(self, raw=False):
        """
        Get the sensor status register.
        It returns a int value or the bytearray(3) if raw==True
        """
        data = self.__send_cmd(SHT30.STATUS_CMD, 3, read_delay_ms=50)

        status_register = data[0] << 8 | data[1]
        status = {
            'Checksum of last write transfer was correct': not (status_register & 1),
            'Last command executed successfully': not (status_register & 2),
            'Reset detected': bool(status_register & 16),
            'Temperature tracking alert': bool(status_register & 1024),
            'Humidity tracking alert': bool(status_register & 2048),
            'Heater is ON': bool(status_register & 8192),
            'At least one pending alert': bool(status_register & 32768)
        }
        return status_register if raw else status

    def measure(self, clock_stretching=False, repeatability=REPEATABILITY_MEDIUM, raw=False) -> (float, float):
        """
        If raw==True returns a bytearrya(6) with sensor direct measurement otherwise
        It gets the temperature (T) and humidity (RH) measurement and return them.

        The units are Celsius and percent
        """
        data = self.__send_cmd(self.__get_single_shot_measure_command(clock_stretching, repeatability), 6, 20)

        if raw:
            return data

        t_celsius = (((data[0] << 8 | data[1]) * 175) / 0xFFFF) - 45 + self.delta_temp
        rh = (((data[3] << 8 | data[4]) * 100.0) / 0xFFFF) + self.delta_hum
        return t_celsius, rh

    def art(self):
        """
        The ART (accelerated  response  time) feature  can  be activated  by issuing  the command in Table 12.
        After issuing the ART command the sensor will start acquiring data with a frequency of 4Hz
        :return:
        """
        self.__send_cmd(SHT30.ACCELERATED_RESPONSE_TIME_CMD, 0)


class SHT30Error(Exception):
    """
    Custom exception for errors on sensor management
    """
    BUS_ERROR = 0x01
    DATA_ERROR = 0x02
    CRC_ERROR = 0x03

    def __init__(self, error_code=None):
        self.error_code = error_code
        super().__init__(self.get_message())

    def get_message(self):
        if self.error_code == SHT30Error.BUS_ERROR:
            return "Bus error"
        elif self.error_code == SHT30Error.DATA_ERROR:
            return "Data error"
        elif self.error_code == SHT30Error.CRC_ERROR:
            return "CRC error"
        else:
            return "Unknown error"
