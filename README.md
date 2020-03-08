# Introduction
This library includes a Python class for manipulating the TPLink Kasa
family of smart plugs and switches.

I purposely chose to show the request format for each kind of action in
full, so that programmers can see how each action is structured.

This rendition is a version of the excellent
[tplink-cloud-api NPM module](https://www.npmjs.com/package/tplink-cloud-api).
While that modules is written in the Node async paradigm, this
rendition in Python uses blocking calls that make it easier for novice
programmers to read.

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
