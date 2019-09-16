import jlrpy
from configparser import ConfigParser
import os
import json
import requests
import time

config = ConfigParser()
config.read('config.ini')

username = config.get('jlrpy', 'email')
password = config.get('jlrpy', 'password')
url = config.get('splunk', 'url')
verify_ssl = config.get('jlrpy', 'insecure_ssl')
token = config.get('splunk', 'token')
index = config.get('splunk', 'index')
epoch_time = int(time.time())

if verify_ssl == "True":
    ssl_verify = True
else:
    ssl_verify = False

# Authenticate using the username and password
c = jlrpy.Connection(username, password)
v = c.vehicles[0]
user_info = c.get_user_info()
status = v.get_status()

healthstatus = v.get_health_status()
status = { d['key'] : d['value'] for d in v.get_status()['vehicleStatus'] }

# Assigning a bunch of variables.

# Door position
front_left_door_position = status['DOOR_FRONT_LEFT_POSITION']
front_right_door_position = status['DOOR_FRONT_RIGHT_POSITION']
rear_left_door_position = status['DOOR_REAR_LEFT_POSITION']
rear_right_door_position = status['DOOR_REAR_RIGHT_POSITION']
bonnet_position = status['DOOR_ENGINE_HOOD_POSITION']
boot_position = status['DOOR_BOOT_POSITION']

# Door lock Status
overall_door_lock_status = status['DOOR_IS_ALL_DOORS_LOCKED']
rear_right_door_lock = status['DOOR_REAR_RIGHT_LOCK_STATUS']
rear_left_door_lock = status['DOOR_REAR_LEFT_LOCK_STATUS']
front_right_door_lock = status['DOOR_FRONT_RIGHT_LOCK_STATUS']
front_left_door_lock = status['DOOR_FRONT_LEFT_LOCK_STATUS']
bonnet_lock = status['DOOR_ENGINE_HOOD_LOCK_STATUS']
boot_lock = status['DOOR_IS_BOOT_LOCKED']
boot_lock_status = status['DOOR_BOOT_LOCK_STATUS']

# Warnings
washer_fluid_warn = status['WASHER_FLUID_WARN']
brake_fluid_warn = status['BRAKE_FLUID_WARN']
engine_coolant_warn = status['ENG_COOLANT_LEVEL_WARN']
exhaust_fluid_warn = status['EXT_EXHAUST_FLUID_WARN']
part_filter_warn = status['EXT_PARTICULATE_FILTER_WARN']

# Tyre Status
rear_left_tyre_status = status['TYRE_STATUS_REAR_LEFT']
rear_right_tyre_status = status['TYRE_STATUS_REAR_RIGHT']
front_left_tyre_status = status['TYRE_STATUS_FRONT_LEFT']
front_right_tyre_status = status['TYRE_STATUS_FRONT_RIGHT']

# Tyre Pressures - I dont know what unit of measurement these are in
rear_right_tyre_pres = status['TYRE_PRESSURE_REAR_RIGHT']
rear_left_tyre_pres = status['TYRE_PRESSURE_REAR_LEFT']
front_right_tyre_pres = status['TYRE_PRESSURE_FRONT_RIGHT']
front_left_tyre_pres = status['TYRE_PRESSURE_FRONT_LEFT']

# Window Status
rear_right_window = status['WINDOW_REAR_RIGHT_STATUS']
rear_left_window = status['WINDOW_REAR_LEFT_STATUS']
front_right_window = status['WINDOW_FRONT_RIGHT_STATUS']
front_left_window = status['WINDOW_FRONT_LEFT_STATUS']

# General
mileage = status['ODOMETER_MILES']
distance_to_empty = status['DISTANCE_TO_EMPTY_FUEL'] # in KM
panic_alarm = status['IS_PANIC_ALARM_TRIGGERED'] # Dunno wtf this is...currently showing as unknown
theft_alarm = status['THEFT_ALARM_STATUS']
crash_situation = status['IS_CRASH_SITUATION'] # lol
fuel_level_percent = status['FUEL_LEVEL_PERC']
cab_open = status['IS_CAB_OPEN'] # Unsure on this one

# Generate the JSON
json_out = {
    "time": epoch_time,
    "index": index,
    "source": "jlrpy",
    "event": [ {
    "Door Positions": [
    {"Front Left Door Position": front_left_door_position},
    {"Front Right Door Position": front_right_door_position},
    {"Rear Left Door Position": rear_left_door_position},
    {"Rear Right Door Position": rear_right_door_position},
    {"Boot Position":  boot_position},
    {"Bonnet Position": bonnet_position}
    ],
    "Door Lock Status": [
    {"Overall door lock status": overall_door_lock_status},
    {"Front Left Door Lock": front_left_door_lock},
    {"Front Right Door Lock": front_right_door_lock},
    {"Rear Left Door Lock": rear_left_door_lock},
    {"Rear Right Door Lock": rear_right_door_lock},
    {"Boot Lock": boot_lock_status},
    {"Bonnet Lock": bonnet_lock}
    ],
    "Warnings": [
    {"Washer Fluid Warning": washer_fluid_warn},
    {"Brake Fluid Warning": brake_fluid_warn},
    {"Engine Coolant Warning": engine_coolant_warn},
    {"Exhaust Fluid Warning": exhaust_fluid_warn},
    {"Particulate Filter Warning": part_filter_warn}
    ],
    "Tyre Status": [
    {"Front Left Tyre Status": front_left_tyre_status},
    {"Front Right Tyre Status": front_right_tyre_status},
    {"Rear Left Tyre Status": rear_left_tyre_status},
    {"Rear Right Tyre Status": rear_right_tyre_status}
    ],
    "Tyre Pressures": [
    {"Front Left Tyre Pressure": front_left_tyre_pres},
    {"Front Right Tyre Pressue": front_right_tyre_pres},
    {"Rear Left Tyre Pressure": rear_left_tyre_pres},
    {"Rear Right Tyre Pressure": rear_right_tyre_pres}
    ],
    "Window Status": [
    {"Front Left Window Status": front_left_window},
    {"Front Right Window Status": front_right_window},
    {"Rear Left Window Status": rear_left_window},
    {"Rear Right Window Status": rear_right_window}
    ],
    "General": [
    {"Mileage": mileage},
    {"Distance to Empty (in KM)": distance_to_empty},
    {"Panic Alarm Status": panic_alarm},
    {"Theft Alarm Status": theft_alarm},
    {"Crash Situation": crash_situation},
    {"Fuel Level in Percent": fuel_level_percent},
    {"Cab Open": cab_open}
    ]
    }
    ]
}
#print(json.dumps(json_out))

data_json = json.dumps(json_out)


headers = {
    "X-Splunk-Request-Channel": "FE0ECFAD-13D5-401B-847D-77833BD77131",
    "Authorization": "Splunk {0}".format(token)
}
r = requests.post(url, data=data_json, headers=headers, verify=ssl_verify)
print(r.content)
print(r.status_code)