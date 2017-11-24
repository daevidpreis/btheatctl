#!/usr/bin/env python3
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"THE BEER-WARE LICENSE" (Revision 42):
<daevid.preis@gmail.com> wrote this file. As long as you retain this notice
you can do whatever you want with this stuff. If we meet some day, and you
think this stuff is worth it, you can buy me a beer in return
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import sys
import struct
import argparse
from bluepy.btle import Peripheral

TERSE = False
LOGIN_CHARACTERISTIC_HANDLE = 70
TEMPERATURE_CHARACTERISTICS_HANDLE = 62


def parse_args():
    parser = argparse.ArgumentParser()

    optional_group = parser.add_argument_group("optional arguments")
    parser.add_argument("--offset", "-o", type=float, help="temperature offset", dest="offset")
    parser.add_argument("--terse", "-t", action="store_true", help="print parseable output", dest="terse")

    device_group = parser.add_argument_group("required arguments")
    device_group.add_argument("--device", "-d", required=True, help="mac address of the device", dest="device")
    device_group.add_argument("--pin", "-p", required=True, type=int, help="pin for the device", dest="pin")

    action_group = device_group.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--get", "-g", action="store_true", help="get current values", dest="get")
    action_group.add_argument("--set", "-s", type=float, help="set temperature", dest="set")

    args = parser.parse_args()

    if (args.terse):
        global TERSE
        TERSE = True

    device = prepare_device(args.device, args.pin)

    if args.get:
        get_temp(device)
        sys.exit(0)

    if args.set or args.offset:
        set_temp(device, args.set, args.offset)
        sys.exit(0)


def connect_to_device(addr):
    try:
        v_print("connecting to:", addr)
        device = Peripheral(addr)
        v_print("connection established")
        return device
    except:
        print("could not connect to device.", sys.exc_info()[0])
        sys.exit(1)


def authenticate(characteristic, pin):
    """ pin is an little endian byte array. 123456 would be => \x40\xe2\x01\x00 """
    try:
        v_print("sending pin")
        characteristic.write(struct.pack('<L', pin), True)
        v_print("pin accepted")
    except:
        print("login failed!", sys.exc_info()[0])
        sys.exit(4)


def write_value(device, characteristic_handle, data):
    try:
        prop = device.getCharacteristics(characteristic_handle, characteristic_handle)[0]
        if not prop or prop is None:
            print("could not find characteristic.")
            return False

        try:
            prop.write(data, True)
            return True
        except:
            print("write error:", sys.exc_info()[0])
    except:
        print("could not get characteristic.", sys.exc_info()[0])
    return False


def read_value(device, characteristic_handle):
    try:
        prop = device.getCharacteristics(characteristic_handle, characteristic_handle)[0]
        if not prop or prop is None:
            print("could not find characteristic.")
            return None

        if prop.supportsRead:
            try:
                return prop.read()
            except:
                print("read error:", sys.exc_info()[0])
        else:
            print("reading is not supported")
    except:
        print("could not get characteristic.", sys.exc_info()[0])
    return None


def set_temp(device, new_temp = None, offset = None):
    if new_temp is None and offset is None:
        return False
    new_temps = bytearray([128, 128, 128, 128, 128, 128, 128])
    if new_temp is not None:
        new_temps[1] = new_temps[2] = new_temps[3] = int(new_temp * 2)
        v_print("changing temperature to:", new_temp)
    if offset is not None:
        new_temps[4] = int(offset * 2)
        v_print("changing offset to:", offset)
    return write_value(device, TEMPERATURE_CHARACTERISTICS_HANDLE, new_temps)


def get_temp(device):
    global TERSE
    temperatures = read_value(device, TEMPERATURE_CHARACTERISTICS_HANDLE)
    current_temp = temperatures[0] / 2
    manual_temp = temperatures[1] / 2
    low_temp = temperatures[2] / 2
    high_temp = temperatures[3] / 2
    offset = temperatures[4] / 2
    open_win_interval = temperatures[5]
    open_win_duration = temperatures[6]

    if TERSE:
        print(current_temp, manual_temp, offset)
    else:
        print("current temperature:", current_temp, "set temperature:", manual_temp, "offset:", offset)
        print("auto => low:", low_temp, "high:", high_temp)
        print("open window => interval:", open_win_interval, "duration:", open_win_duration)


def prepare_device(addr, pin):
    device = connect_to_device(addr)

    try:
        login_characteristic = device.getCharacteristics(
            LOGIN_CHARACTERISTIC_HANDLE, LOGIN_CHARACTERISTIC_HANDLE
        )[0]
    except:
        print("could not get login characteristic.", sys.exc_info()[0])
        sys.exit(2)

    if not login_characteristic:
        print("could not find login characteristic.")
        sys.exit(3)

    authenticate(login_characteristic, pin)
    return device


def v_print(*args):
    global TERSE
    if not TERSE:
        print(*args)


parse_args()
