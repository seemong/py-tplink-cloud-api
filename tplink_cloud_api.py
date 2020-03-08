# Lint as: PY3
"""
# Introduction
This library includes a class for manipulating the TPLink Kasa
family of smart plugs and switches.

# Usage
    # First create the TPLink instance
    tplink = TPLink(username, password)

    # Get all devices for this user
    devices = tplink.get_device_list()
    for device in devices:
        print(device)

    # Assume the user has a device named 'MyPlug'
    # Print info about the device named 'MyPlug'
    device = tplink.get_device('MyPlug')
    print(device)

    # check if the device is on
    if (tpink.is_on('MyPlug')):
        print('MyPlug is on')

    # powercycle the device
    tplink.powercycle('MyPlug')

    # Turn it off completely
    tplink.turn_off('MyPlug')

    # Turn it back on
    tplink.turn_on('MyPlug')

# Running this file as a command line program

    Sample usage:
        python3 tplink_cloud_api.py command --username=XX --password=YY
            --device=ZZ

    Where command is one of
        'list', 'turnon', 'turnoff', 'powercycle', 'sysinfo', 'ison', 'isoff'
    When the command is 'list', '--device' option is not required.
    The '--username' and '--password' options are always required.
"""

import argparse
import certifi
import json
import pdb
import pprint
import ssl
import sys
import time
from typing import Dict
from typing import List
import urllib.parse
import urllib.request


class TPLink:
    """
    This class is the basic entry point for the library. Instantiate
    an instance of this class with a username and password. Use it
    to get device lists and open devices belonging to this user.
    """

    @staticmethod
    def form_url(request: Dict) -> str:
        """Return the URL formed from the request.

        Arguments:
            request: Dict dictionary defining the structure of the request.

        Returns:
            str of the URL formed from the URL and params
        """
        url = request['url'] + '?'
        for param in request['params']:
            url += param + '=' + request['params'][param] + '&'
        return url[:-1]


    @staticmethod
    def send_request(request: Dict) -> Dict:
        """Send the TP Link request.

        Arguments:
            request: Dict dictionary definining the structure of the request.

        Returns:
            Dict: The JSON response from the TPLink server

        Raises:
            RuntimeError: on server error
        """
        # Form the URL
        url = TPLink.form_url(request)

        # Extrac the headers
        headers = request['headers']
        # Encode the data payload as UTF-8
        data = json.dumps(request['data']).encode('utf-8')
        # Create the URL Request
        req = urllib.request.Request(url, data=data, headers=headers)
        response = urllib.request.urlopen(
            req,
            context=ssl.create_default_context(cafile=certifi.where()))
        # Check for a correct response
        if not response:
            return { 'error' : 'Null response from server' }
        # Expect the response as JSON
        response_data = response.read().decode('utf-8')
        json_response = json.loads(response_data)
        # Error code should be zero if there was no error
        if json_response['error_code'] != 0:
            return { 'error': response_data }
        # Return the results field
        return json_response['result']


    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        request = {
            'method': 'POST',
            'url': 'https://wap.tplinkcloud.com',
            'params': {
                'appName': 'Kasa_Android',
                'termID': 'TermID',
                'appVer': '1.4.4.607',
                'ospf': 'Android+6.0.1',
                'netType': 'wifi',
                'locale': 'es_ES'
            },
            'data': {
                'method': 'login',
                'url': 'https://wap.tplinkcloud.com',
                'params': {
                    'appType': 'Kasa_Android',
                    'cloudPassword': password,
                    'cloudUserName': username,
                    'terminalUUID': 'TermID'
                }
            },
            'headers': {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)',
                'Content-Type': 'application/json',
            }
        }
        # send the query
        result = TPLink.send_request(request)
        # save the returned token
        self.token = result['token']
        self.device_list = None
        self.device_list = self.get_device_list()

    def get_device_list(self) -> List:
        """Return the list of devices for this account.

        Returns:
            List the list of devices in JSON format
        """
        # Return cached device list if we have it
        if self.device_list:
            return self.device_list

        request = {
            'method': 'POST',
            'url': 'https://wap.tplinkcloud.com',
            'params': {
                'appName': 'Kasa_Android',
                'termID': 'TermID',
                'appVer': '1.4.4.607',
                'ospf': 'Android+6.0.1',
                'netType': 'wifi',
                'locale': 'es_ES',
                'token': self.token,
            },
            'headers': {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)',
                'Content-Type': 'application/json',
            },
            'data': {
                'method': 'getDeviceList'
            }
        }
        # send the query
        result = TPLink.send_request(request)
        # pull out the device list field
        self.device_list = result['deviceList']
        return self.device_list

    def get_device(self, alias: str) -> Dict:
        """Return the device json description with the given alias."""
        for device in self.device_list:
            if device['alias'] == alias:
                return device
        # Error on not found
        return None

    def set_relay_state(self, alias: str, state: int) -> Dict:
        """
        Turn off the device with the given alias.

        Arguments:
            alias: str The alias name
            state: int The state to set the device to

        Returns:
            Dict The JSON response from the server
        """
        device = self.get_device(alias)
        if not device:
            raise RuntimeError('Cannot find device: ' + alias)

        request = {
            'method': 'POST',
            'url': device['appServerUrl'],
            'params': {
                'appName': 'Kasa_Android',
                'termID': 'TermID',
                'appVer': '1.4.4.607',
                'ospf': 'Android+6.0.1',
                'netType': 'wifi',
                'locale': 'es_ES',
                'token': self.token,
            },
            'headers': {
                'cache-control': 'no-cache',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)',
                'Content-Type': 'application/json',
            },
            'data': {
                'method': 'passthrough',
                'params': {
                    'deviceId': device['deviceId'],
                    'requestData': {
                        'system': {
                            'set_relay_state': {
                                'state': state
                            }
                        }
                    }
                }
            }
        }
        # send the query
        result = TPLink.send_request(request)
        return result['responseData']

    def turn_on(self, alias: str) -> Dict:
        """Turn the device on."""
        return self.set_relay_state(alias, 1)

    def turn_off(self, alias: str) -> Dict:
        """Turn the device off."""
        return self.set_relay_state(alias, 0)

    def powercycle(self, alias: str) -> str:
        """Power cycle the device. Effectively, turn off, wait 5s, turn on."""
        self.turn_off(alias)
        time.sleep(5)
        self.turn_on(alias)
        return 'Done'

    def is_on(self, alias: str) -> bool:
        """Return true if the device is on, false otherwise."""
        state = self.get_sys_info(alias)
        return state['system']['get_sysinfo']['relay_state'] == 1

    def is_off(self, alias: str) -> bool:
        """Return true if the device is off, false otherwise."""
        return not self.is_on(alias)

    def get_sys_info(self, alias: str) -> Dict:
        """
        Get the device sys info with the given alias.
        """
        device = self.get_device(alias)
        if not device:
            raise RuntimeError('Cannot find device: ' + alias)

        request = {
            'method': 'POST',
            'url': device['appServerUrl'],
            'params': {
                'appName': 'Kasa_Android',
                'termID': 'TermID',
                'appVer': '1.4.4.607',
                'ospf': 'Android+6.0.1',
                'netType': 'wifi',
                'locale': 'es_ES',
                'token': self.token,
            },
            'headers': {
                'cache-control': 'no-cache',
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)',
                'Content-Type': 'application/json',
            },
            'data': {
                'method': 'passthrough',
                'params': {
                    'deviceId': device['deviceId'],
                    'requestData': {
                        'system': {
                            'get_sysinfo': None
                        },
                        'emeter': {
                            'get_realtime': None
                        }
                    }
                }
            }
        }
        # send the query
        result = TPLink.send_request(request)
        return result['responseData']


def main():
    """
    Pretty prints the device list belonging to the user.

    Sample usage:
        python3 tplink_cloud_api.py command --username=XX --password=YY
            --device=ZZ

    Where command is one of
        'list', 'turnon', 'turnoff', 'powercycle', 'sysinfo'
    When the command is 'list', '--device' option is not required.
    The '--username' and '--password' options are always required.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=[
            'list', 'turnon', 'turnoff', 'powercycle', 'sysinfo',
            'ison', 'isoff'
        ],
        help='The command to perform')
    parser.add_argument(
        '--device',
        required=False,
        help='The human readable name of the device')
    parser.add_argument(
        '--username',
        required=True,
        help='Username for the account')
    parser.add_argument(
        '--password',
        required=True,
        help='Password for the account')
    parser.add_argument(
        '--verbose',
        required=False,
        help='Add this option for verbose output for the list command'
    )
    args = parser.parse_args()

    tplink = TPLink(args.username, args.password)

    pp = pprint.PrettyPrinter()
    if args.command == 'list':
        devices = None
        try:
            device = tplink.get_device_list()
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            sys.exit(-1)

        for device in devices:
            if args.verbose:
                pp.pprint(device)
            else:
                device_status = 'Offline'
                if device['status'] == 1:
                    device_status = 'Online'
                print('%-20s  %-30s %10s' % (
                    device['alias'],
                    device['deviceName'],
                    device_status
                    ))
        return

    if not args.device:
        print('Missing --device argument', file=sys.stderr)
        sys.exit(-1)

    try:
        if args.command == 'turnoff':
            result = tplink.turn_off(args.device)
            pp.pprint(result)
        elif args.command == 'turnon':
            result = tplink.turn_on(args.device)
            pp.pprint(result)
        elif args.command == 'powercycle':
            result = tplink.powercycle(args.device)
            pp.pprint(result)
        elif args.command == 'sysinfo':
            result = tplink.get_sys_info(args.device)
            pp.pprint(result)
        elif args.command == 'ison':
            result = tplink.is_on(args.device)
            pp.pprint(result)
        elif args.command == 'isoff':
            result = tplink.is_off(args.device)
            pp.pprint(result)
        else:
            print('Unknown command: ' + args.commmand, file=sys.stderr)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(-1)

    sys.exit(0)

if __name__ == '__main__':
    main()
