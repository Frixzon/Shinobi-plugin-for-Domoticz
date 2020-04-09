# Shinobi-plugin-for-Domoticz
A Domoticz plugin that creates a switch for each monitor configured in your Shinobi server and enables Domoticz to change their state.

## Prerequisites
1. Rrequests libary for Python 3: https://pypi.org/project/requests/

## Installation
1. Clone repository into your Domoticz plugins folder
    ```
    cd domoticz/plugins
    git clone https://github.com/Frixzon/Shinobi-plugin-for-Domoticz.git
    ```
1. Restart domoticz
    ```
    sudo service domoticz.sh restart
    ```
1. Make sure that "Accept new Hardware Devices" is enabled in Domoticz settings
1. Go to "Hardware" page
1. Enter the Name
1. Select Type: `Shinobi`
1. Click `Add`

## Update
1. Go to plugin folder and pull new version
    ```
    cd domoticz/plugins/Shinobi-plugin
    git pull
    ```
1. Restart domoticz
    ```
    sudo service domoticz.sh restart
    ```

## Devices
The following devices are created:

| Type                | Name                      | Description
| :---                | :---                      | :---
| Selector Switch | Monitor #                     | Can set monitor state Watch Only/Record/Off
