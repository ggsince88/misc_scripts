import argparse
import configparser
import json
import requests
import yaml
from pprint import pprint

st_token = '1111'
st_api_url = 'https://api.smartthings.com/v1/'
api_call_headers = {'Authorization': 'Bearer ' + st_token}


def smartthings_get(st_query):
    resp = requests.get(st_api_url + st_query, headers=api_call_headers).json()
    return resp


def smartthings_post(st_query, data):
    post = requests.post(st_api_url + st_query, json=data, headers=api_call_headers).json()
    return post


def list_all_devices():
    resp = requests.get(st_api_url + 'devices', headers=api_call_headers).json()
    for devices in resp["items"]:
        print(devices["label"])


def get_all_devices():
    resp = requests.get(st_api_url + 'devices', headers=api_call_headers).json()
    return resp["items"]


def get_device_status(name):
    device_list = get_all_devices()
    for device in device_list:
        if device['label'] == name:
            # print(device['deviceId'])
            st_status = smartthings_get('devices/' + device['deviceId'] + '/status')
            # print(yaml.dump(st_status, default_flow_style=False))
            return st_status
    return 'No device found'


def operate_switches(commands, name):
    device_list = get_all_devices()
    for device in device_list:
        if device['label'] == name:
            switch_status = smartthings_post('devices/' + device['deviceId'] + '/commands', commands)
            print('Command sent')
            return switch_status


def main():
    parser = argparse.ArgumentParser(description='Smart devices control script')
    parser.add_argument('-list', help='List all devices', action='store_true')
    parser.add_argument('-status', help='Get status of device', metavar='DEVICE')
    parser.add_argument('-turnon', help='Turn on device', metavar='DEVICE')
    parser.add_argument('-turnoff', help='Turn off device', metavar='DEVICE')
    parser.add_argument('-lock', help='Lock door')
    args = parser.parse_args()
    if args.list:
        list_all_devices()
    if args.status:
        print(yaml.dump(get_device_status(args.status), default_flow_style=False))
        #pprint(get_device_status(args.status))
    if args.turnon:
        on_command = {"commands": [{"component": "main", "capability": "switch", "command": "on"}]}
        operate_switches(on_command, args.turnon)
    if args.turnoff:
        off_command = {"commands": [{"component": "main", "capability": "switch", "command": "off"}]}
        operate_switches(off_command, args.turnoff)
    #if args.lock:
    #    lock_command = {"command": [{"component": "main", "capability": "switch", "command": }]}


if __name__ == '__main__':
    main()