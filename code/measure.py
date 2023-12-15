#!/usr/bin/python3
import SHT30 as driver
import sys
import argparse
import time
import json

__version__ = '1.0.0'
__author__ = 'Morskov Maksim'
__license__ = "Apache License 2.0. https://www.apache.org/licenses/LICENSE-2.0"

"""
    SHT30 sensor measuring driver in python based on I2C bus

    References:
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf  # NOQA
    * https://www.wemos.cc/sites/default/files/2016-11/SHT30-DIS_datasheet.pdf
    * https://github.com/wemos/WEMOS_SHT3x_Arduino_Library
    * https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/11_Sample_Codes_Software/Humidity_Sensors/Sensirion_Humidity_Sensors_SHT3x_Sample_Code_V2.pdf
    """


def get_params_using_parser(args: list):
    params_parser = argparse.ArgumentParser()
    params_parser.add_argument(
        '-m', '--measurements',
        type=int, help='mesurements count',
        default='10'
    )
    params_parser.add_argument(
        '-i', '--interval',
        type=float, help='mesurements interval (seconds)',
        default='2.0'
    )
    params_parser.add_argument(
        '-j', '--json_out',
        type=bool, help='json output',
        default=False
    )
    return params_parser.parse_args(args)


def main(params):
    sensor = driver.SHT30()
    data = []

    if not sensor.is_plugged():
        print("SHT30 is not plugged!")

    if not params.json_out:
        print("SHT30 is starting measurements...")
    for index in range(params.measurements):
        temperature, humidity = sensor.measure()
        if not params.json_out:
            print('Temperature:', temperature, 'ºC, RH:', humidity, '%')
        else:
            data.append({'temp': temperature, 'hum': humidity})
        time.sleep(params.interval)
    if params.json_out:
        print(json.dumps(data))
    else:
        print("Done!")
        print("SHT30 status:")
        print(sensor.status())


# --== Entry point ==--
if __name__ == "__main__":
    params = get_params_using_parser(sys.argv[1:])
    main(params)
