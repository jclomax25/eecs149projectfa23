from machine import I2C, Pin
import time

__version__ = '0.2.1'
__author__ = 'Roberto Sánchez'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

# I2C address B 0x45 ADDR (pin 2) connected to VDD
DEFAULT_I2C_ADDRESS = 0x44

class SHT30():
    """SHT30 Python Driver"""
    POLYNOMIAL = 0x131  # P(x) = x^8 + x^5 + x^4 + 1 = 100110001

    ALERT_PENDING_MASK = 0x8000 # 15
    HEATER_MASK = 0x2000        # 13
    RH_ALERT_MASK = 0x0800		# 11
    T_ALERT_MASK = 0x0400		# 10
    RESET_MASK = 0x0010	        # 4
    CMD_STATUS_MASK = 0x0002	# 1
    WRITE_STATUS_MASK = 0x0001	# 0

    # MSB = 0x2C LSB = 0x06 Repeatability = High, Clock stretching = enabled
    MEASURE_CMD = b'\x2C\x10'
    STATUS_CMD = b'\xF3\x2D'
    RESET_CMD = b'\x30\xA2'
    CLEAR_STATUS_CMD = b'\x30\x41'
    ENABLE_HEATER_CMD = b'\x30\x6D'
    DISABLE_HEATER_CMD = b'\x30\x66'

    def __init__(self, scl_pin=13, sda_pin=12, delta_temp=0, delta_hum=0, i2c_address=0x44):
        self.i2c = I2C(id=0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100_000)
        self.i2c_addr = i2c_address
        self.set_delta(delta_temp, delta_hum)
        time.sleep_ms(50)

    def init(self, scl_pin=13, sda_pin=12):
        self.i2c.init(scl=Pin(scl_pin), sda=Pin(sda_pin))

    def is_present(self):
        return self.i2c_addr in self.i2c.scan()

    def set_delta(self, delta_temp, delta_hum):
        self.delta_temp = delta_temp
        self.delta_hum = delta_hum

    def chk_crc(self, data):
        crc = 0xFF

        for d in data[:-1]:
            crc ^= d
            for x in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ SHT30.POLYNOMIAL
                else:
                    crc <<= 1
        crc_to_comp = data[-1]
        return crc_to_comp == crc

    def send_cmd(self, cmd_request, response_size=6, read_delay_ms=100):
        try:
            #print("trying")
            #print("started")
            self.i2c.writeto(self.i2c_addr, cmd_request)
            #print("wrote")
            if not response_size:
                return
            time.sleep_ms(read_delay_ms)
            data = self.i2c.readfrom(self.i2c_addr, response_size)
            #print("read")
            #print("stopped")
            for i in range(response_size//3):
                if not self.chk_crc(data[i*3:(i+1)*3]):
                    raise SHT30Error(SHT30Error.CRC_ERROR)
            if data == bytearray(response_size):
                raise SHT30Error(SHT30Error.DATA_ERROR)
            return data
        except OSError as ex:
            if 'I2C' in ex.args[0]:
                raise SHT30Error(SHT30Error.BUS_ERROR)
            raise ex

    def clear_status(self):
        return self.send_cmd(SHT30.CLEAR_STATUS_CMD, None)

    def reset(self):
        return self.send_cmd(SHT30.RESET_CMD, None)

    def measure(self, raw=False):
        data = self.send_cmd(SHT30.MEASURE_CMD, 6)

        if raw:
            return data

        t_celsius = (((data[0] << 8 | data[1]) * 175) / 0xFFFF) - 45 + self.delta_temp
        rh = (((data[3] << 8 | data[4]) * 100.0) / 0xFFFF) + self.delta_hum
        return t_celsius, rh

    def measure_int(self, raw=False):
        data = self.send_cmd(SHT30.MEASURE_CMD, 6)

        if raw:
            return data

        aux = (data[0] << 8 | data[1]) * 175
        t_int = (aux // 0xffff) - 45
        t_dec = (aux % 0xffff * 100) // 0xffff
        aux = (data[3] << 8 | data[4]) * 100
        h_int = aux // 0xffff
        h_dec = (aux % 0xffff * 100) // 0xffff
        return t_int, t_dec, h_int, h_dec

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
