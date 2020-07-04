#import os
#import ssl
import json
import time
#import hmac
#import hashlib
import flask
#import base64
import datetime
import calendar
#from flask_json import FlaskJSON, JsonError, json_response, as_json
#from certificate_generator import certificate_generator
#from messaging_client import messaging_client
#from rest_api_config import config
#from database import database_client
#from flask_cors import CORS
from flask_api import status
from jose import jwk, jwt
#import http.client
#from s3_client import s3_client
import threading
#import copy
#from redis_client import redis_client
import statistics
import rest_api_utils
from database import database_categorylabel, database_crudindex



#CONFIG_SEPARATOR            = '/'
#CONFIG_PREPEND_REPLY_TOPIC  = "server"



class device_dashboard_old:

    def __init__(self, database_client, messaging_requests):
        self.database_client = database_client
        self.messaging_requests = messaging_requests

    def sort_by_timestamp(self, elem):
        return elem['timestamp']

    def sort_by_devicename(self, elem):
        return elem['devicename']

    def sort_by_sensorname(self, elem):
        return elem['sensorname']


    def get_running_sensors(self, token, username, devicename, device):

        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        # query device
        api = "get_devs"
        data = {}
        data['token'] = token
        data['devicename'] = devicename
        data['username'] = username
        response, status_return = self.messaging_requests.process(api, data)
        if status_return == 200:
            device['status'] = 1
            # query database
            sensors = self.database_client.get_all_device_sensors(entityname, devicename)

            # map queried result with database result
            #print("from device")
            response = json.loads(response)
            #print(response["value"])

            for sensor in sensors:
                #print(sensor)
                found = False
                peripheral = "{}{}".format(sensor['source'], sensor['number'])

                if True: #sensor["source"] == "i2c":
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            # match found for database result and actual device result
                            # set database record to configured and actual device item["enabled"]
                            if sensor["address"] == item["address"]:
                                self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break
                else:
                    if response["value"].get(peripheral):
                        for item in response["value"][peripheral]:
                            if item["class"] == rest_api_utils.utils().get_i2c_device_class(sensor["class"]):
                                self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], item["enabled"], 1)
                                found = True
                                break

                # no match found
                # set database record to unconfigured and disabled
                if found == False:
                    self.database_client.set_enable_configure_sensor(entityname, devicename, sensor['source'], sensor['number'], sensor['sensorname'], 0, 0)
            #print()
        else:
            device['status'] = 0
            # cannot communicate with device so set database record to unconfigured and disabled
            self.database_client.disable_unconfigure_sensors(entityname, devicename)
            #print('\r\nERROR Get All Device Sensors Dataset: Device is offline\r\n')
            return response, status_return
        return response, 200

    def get_sensor_data_threaded(self, sensor, entityname, datebegin, dateend, period, maxpoints, readings, devicename, devices):
        if devicename is not None:
            sensor["devicename"] = devicename
        elif devices is not None:
            for device in devices:
                if device["deviceid"] == sensor["deviceid"]:
                    sensor["devicename"] = device["devicename"]
                    break

        # add the dataset parameter
        dataset = self.database_client.get_sensor_reading_dataset_timebound(entityname, sensor["devicename"], sensor["source"], int(sensor["number"]), datebegin, dateend, period, maxpoints)
        if dataset is not None:
            sensor['dataset'] = dataset

        # add the readings parameter
        for reading in readings:
            if sensor["source"] == reading["source"]:
                if int(sensor["number"]) == reading["number"]:
                    sensor['readings'] = reading['sensor_readings']
                    break

    def get_sensor_comparisons(self, devices, sensors_list):
        classes = []
        comparisons = []

        for sensor in sensors_list:
            label = sensor["sensorname"] + "." + sensor["devicename"]

            try:
                average_data = round(statistics.mean(sensor["dataset"]["data"][0]), 1)
            except:
                average_data = 0
            try:
                min_low = round(min(sensor["dataset"]["low"][0]), 1)
            except:
                min_low = 0
            try:
                max_high = round(max(sensor["dataset"]["high"][0]), 1)
            except:
                max_high = 0

            if average_data > 0:
                if sensor["class"] not in classes:
                    classes.append(sensor["class"])
                    item = {
                        'class': sensor["class"], 'labels': [], 'data': [[],[],[]]
                    }
                    item['data'][0].append(min_low)
                    item['data'][1].append(average_data)
                    item['data'][2].append(max_high)
                    item['labels'].append(label)
                    comparisons.append(item)
                else:
                    for comparison in comparisons:
                        if comparison["class"] == sensor["class"]:
                            comparison['data'][0].append(min_low)
                            comparison['data'][1].append(average_data)
                            comparison['data'][2].append(max_high)
                            comparison['labels'].append(label)
                            break

            if sensor.get("subclass"):
                try:
                    average_data = round(statistics.mean(sensor["dataset"]["data"][1]), 1)
                except:
                    average_data = 0
                try:
                    min_low = round(min(sensor["dataset"]["low"][1]), 1)
                except:
                    min_low = 0
                try:
                    max_high = round(max(sensor["dataset"]["high"][1]), 1)
                except:
                    max_high = 0

                if average_data > 0:
                    if sensor["subclass"] not in classes:
                        classes.append(sensor["subclass"])
                        item = {
                            'class': sensor["subclass"], 'labels': [], 'data': [[],[],[]]
                        }
                        item['data'][0].append(min_low)
                        item['data'][1].append(average_data)
                        item['data'][2].append(max_high)
                        item['labels'].append(label)
                        comparisons.append(item)
                    else:
                        for comparison in comparisons:
                            if comparison["class"] == sensor["subclass"]:
                                comparison['data'][0].append(min_low)
                                comparison['data'][1].append(average_data)
                                comparison['data'][2].append(max_high)
                                comparison['labels'].append(label)
                                break
        for x in range(len(comparisons)-1, 0, -1):
            if len(comparisons[x]['labels']) == 1:
                comparisons.remove(comparisons[x])
        #    print(comparison)
        return comparisons

    def get_device_stats(self, entityname, devices, sensordevicename):
        print("\nget_device_stats\n")
        stats = {}

        if sensordevicename is not None: # All devices
            devices[0]["deviceid"] = self.database_client.get_deviceid(entityname, devices[0]["devicename"])

        devicegroups    = self.database_client.get_devicegroups(entityname)
        devicelocations = self.database_client.get_devices_location(entityname)
        stats['groups']    = { 'labels': ['no group'], 'data': [0] }
        stats['versions']  = { 'labels': ['unknown'], 'data': [0] }
        stats['locations'] = { 'labels': ['known', 'unknown'], 'data': [0, 0] }
        enabled_devices = 0

        for device in devices:
            # handle statuses
            if device.get("status") is not None:
                if device["status"] == 1:
                    enabled_devices += 1

            # handle groups
            found = 0
            #print(device["devicename"])
            for devicegroup in devicegroups:
                if len(devicegroup["devices"]):
                    if device["deviceid"] in devicegroup["devices"]:
                        #print(devicegroup["groupname"])
                        found = 1
                        try:
                            index = stats['groups']['labels'].index(devicegroup["groupname"])
                            stats['groups']['data'][index] += 1
                        except:
                            stats['groups']['labels'].insert(0, devicegroup["groupname"])
                            stats['groups']['data'].insert(0, 1)
                        break
            if found == 0:
                #print(stats['groups']['labels'][0])
                stats['groups']['data'][-1] += 1

            # handle versions
            if device.get("version") is not None:
                try:
                    index = stats['versions']['labels'].index("version " + device["version"])
                    stats['versions']['data'][index] += 1
                except:
                    stats['versions']['labels'].insert(0, "version " + device["version"])
                    stats['versions']['data'].insert(0, 1)
            else:
                stats['versions']['data'][-1] += 1

            # handle locations
            found = 0
            for devicelocation in devicelocations:
                if device.get("deviceid"):
                    if device["deviceid"] == devicelocation["deviceid"]:
                        stats['locations']['data'][0] += 1
                        found = 1
                        break
            if found == 0:
                stats['locations']['data'][1] += 1


        stats['statuses'] = { 
            'total': len(devices), 
            'online': enabled_devices, 
            'offline': len(devices)-enabled_devices, 
            'labels': ['online', 'offline'], 
            'data': [enabled_devices, len(devices)-enabled_devices] }

        return stats

    def get_sensor_stats(self, sensors_list):
        stats = {}

        input_sensors = 0
        stats['types'] = { 'total': 0, 'input': 0, 'output': 0 }
        peripherals = []
        stats['peripherals'] = { 'total': 0, 'labels': [], 'data': [] }
        classes = []
        stats['classes'] = { 'total': 0, 'labels': [], 'data': [] }

        enabled_sensors = 0
        for sensor in sensors_list:
            if sensor["enabled"] == 1:
                enabled_sensors += 1

            if sensor["type"] == "input":
                input_sensors += 1

            if sensor["source"] not in peripherals:
                peripherals.append(sensor["source"])
                stats['peripherals']['total'] += 1
                stats['peripherals'][sensor["source"]] = 1
                stats['peripherals']['label'] = ''
            else:
                stats['peripherals'][sensor["source"]] += 1

            if sensor["class"] not in classes:
                classes.append(sensor["class"])
                stats['classes']['total'] += 1
                stats['classes'][sensor["class"]] = 1
                stats['classes']['label'] = ''
            else:
                stats['classes'][sensor["class"]] += 1

            if sensor.get("subclass"):
                if sensor["subclass"] not in classes:
                    classes.append(sensor["subclass"])
                    stats['classes']['total'] += 1
                    stats['classes'][sensor["subclass"]] = 1
                    stats['classes']['label'] = ''
                else:
                    stats['classes'][sensor["subclass"]] += 1

        len_sensors = len(sensors_list)
        stats['types'] = { 
            'total': len_sensors, 
            'input': input_sensors, 
            'output': len_sensors-input_sensors, 
            'labels': ['input', 'output'], 
            'data': [input_sensors, len_sensors-input_sensors] }
        stats['statuses'] = { 
            'total': len_sensors, 
            'enabled': enabled_sensors, 
            'disabled': len_sensors-enabled_sensors, 
            'labels': ['enabled', 'disabled'], 
            'data': [enabled_sensors, len_sensors-enabled_sensors] }

        if len(peripherals):
            peripherals.sort()
        for peripheral in peripherals:
            stats['peripherals']['labels'].append(peripheral)
            stats['peripherals']['data'].append(stats['peripherals'][peripheral])
            stats['peripherals']['label'] += "{} {}, ".format(stats['peripherals'][peripheral], peripheral)
        if len(peripherals):
            stats['peripherals']['label'] = stats['peripherals']['label'][:len(stats['peripherals']['label'])-2]

        if len(classes):
            classes.sort()
        for classe in classes:
            stats['classes']['labels'].append(classe)
            stats['classes']['data'].append(stats['classes'][classe])
            stats['classes']['label'] += "{} {}, ".format(stats['classes'][classe], classe[:3])
        if len(classes):
            stats['classes']['label'] = stats['classes']['label'][:len(stats['classes']['label'])-2]

        return stats

    def get_usage(self):
        curr_month = calendar.month_name[datetime.datetime.now().month]
        usages = {
    #        'month': curr_month,
    #        'alerts':  {'labels': ['sms', 'email', 'notification'], 'data': [75, 50, 25]},
    #        'storage': {'labels': ['sensor data', 'alert data'], 'data': [50, 25]},
    #        'login':   {'labels': ['email', 'sms'], 'data': [100, 100]}
            'alerts':  {'labels': [curr_month], 'data': [[75], [50], [25]]},
            'storage': {'labels': [""], 'data': [[50], [25]]},
            'login':   {'labels': [curr_month], 'data': [[100], [100]]}
        }
        return usages

    def get_device_summary(self, entityname, devices, sensordevicename):
        devices_list = []

        devicegroups    = self.database_client.get_devicegroups(entityname)
        devicelocations = self.database_client.get_devices_location(entityname)

        if sensordevicename is not None: #"All devices":
            devices[0]["deviceid"] = self.database_client.get_deviceid(entityname, devices[0]["devicename"])

        for device in devices:
            version = "unknown"
            if device.get("version") is not None:
                version = device["version"]

            group = "no group"
            for devicegroup in devicegroups:
                if len(devicegroup["devices"]):
                    if device["deviceid"] in devicegroup["devices"]:
                        group = devicegroup["groupname"]
                        break

            location = "unknown"
            for devicelocation in devicelocations:
                if device["deviceid"] == devicelocation["deviceid"]:
                    location = json.dumps(devicelocation["location"])
                    break

            devices_list.append({
                "devicename": device["devicename"],
                "version": version,
                "group": group,
                "location": location,
                "status": device["status"],
            })

        return devices_list


    def get_sensor_summary(self, entityname, devices, sensordevicename):
        sensors_list = []
        if sensordevicename is not None: #"All devices":
            devices[0]["deviceid"] = self.database_client.get_deviceid(entityname, devices[0]["devicename"])
        for device in devices:
            # get all user input sensors
            sensors = self.database_client.get_all_device_sensors_by_deviceid(device["deviceid"])
            if len(sensors):
                #print(len(sensors))
                for sensor in sensors:
                    address = None
                    if sensor.get("address") is not None:
                        address = sensor["address"]
                    configuration = self.database_client.get_device_peripheral_configuration_by_deviceid(device["deviceid"], sensor["source"], int(sensor["number"]), address)
                    if sensor["type"] == "input":
                        if configuration is not None:
                            mode = configuration["attributes"]["mode"]
                            # check if continuous mode (sensor forwarding) or thresholding mode (notification triggering)
                            if configuration.get("attributes"):
                                if mode == 2: #MODE_CONTINUOUS: 
                                    value = configuration["attributes"]["hardware"]["devicename"]
                                    value = "forward: " + value
                                else: 
                                    threshold = configuration["attributes"]["threshold"]
                                    if mode == 0: # MODE_THRESHOLD_SINGLE
                                        value = {"value": threshold["value"]}
                                    elif mode == 1: # MODE_THRESHOLD_DUAL
                                        value = {"min": threshold["min"], "max": threshold["max"]}
                                    value = "threshold: " + json.dumps(value)
                                classes = sensor["class"]
                            # handle subclass
                            if configuration["attributes"].get("subattributes"):
                                if mode == 2: #MODE_CONTINUOUS: 
                                    subvalue = configuration["attributes"]["subattributes"]["hardware"]["devicename"]
                                    subvalue = "forward: " + value
                                else: 
                                    threshold = configuration["attributes"]["subattributes"]["threshold"]
                                    if mode == 0: # MODE_THRESHOLD_SINGLE
                                        subvalue = {"value": threshold["value"]}
                                    elif mode == 1: # MODE_THRESHOLD_DUAL
                                        subvalue = {"min": threshold["min"], "max": threshold["max"]}
                                    subvalue = "threshold: " + json.dumps(subvalue)
                                value += ", " + subvalue
                                classes += ", " + sensor["subclass"]
                        else:
                            value = "Unconfigured"
                            classes = sensor["class"]
                            if sensor.get("subclass"):
                                classes += ", " + sensor["subclass"]
                    elif sensor["type"] == "output":
                        if configuration is not None:
                            if sensor["class"] == "light":
                                usage = configuration["attributes"]["color"]["usage"]
                                if usage == 0:
                                    endpoint = configuration["attributes"]["color"]["single"]["endpoint"]
                                    if endpoint == 0:
                                        value = "source: manual"
                                    else:
                                        hardware = configuration["attributes"]["color"]["single"]["hardware"]
                                        value = "source: " + hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                else:
                                    individual = configuration["attributes"]["color"]["individual"]
                                    value = {"red": "", "blue": "", "green": ""}
                                    # red
                                    if individual["red"]["endpoint"] == 0:
                                        value["red"] = "manual"
                                    else:
                                        hardware = individual["red"]["hardware"]
                                        value["red"] = hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                    # blue
                                    if individual["blue"]["endpoint"] == 0:
                                        value["blue"] = "manual"
                                    else:
                                        hardware = individual["blue"]["hardware"]
                                        value["blue"] = hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                    # green
                                    if individual["green"]["endpoint"] == 0:
                                        value["green"] = "manual"
                                    else:
                                        hardware = individual["green"]["hardware"]
                                        value["green"] = hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                                    value = "source: " + json.dumps(value)
                            else:
                                try:
                                    endpoint = configuration["attributes"]["endpoint"]
                                except:
                                    print("XXXXXXX" + str(json.dumps(configuration)))
                                    endpoint = 0
                                if endpoint == 0:
                                    value = "source: manual"
                                else:
                                    hardware = configuration["attributes"]["hardware"]
                                    value = "source: " + hardware["devicename"] + "." + hardware["peripheral"] + "." + hardware["sensorname"]
                        else:
                            value = "Unconfigured"
                        classes = sensor["class"]
                        if sensor.get("subclass"):
                            classes += ", " + sensor["subclass"]
                    #print("{}, {}, {}, {}, {}, {}".format(sensor["sensorname"], device["devicename"], classes, value, sensor["enabled"], sensor["source"]))
                    sensors_list.append({
                        "sensorname": sensor["sensorname"], 
                        "devicename": device["devicename"], 
                        "type": sensor["type"], 
                        "peripheral": sensor["source"], 
                        "classes": classes, 
                        "configuration": value, 
                        "enabled": sensor["enabled"]})
        return sensors_list


    #
    # Below is the design of timerange filtering for sensor data dashboard...
    # - Users can select filtering by timeranges of minutes, hours, weeks, months or years.
    # - All timeranges will be divided into 60 periods.
    # - A maximum of 60 datapoints, corresponding to 60 periods, is always returned by the backend.
    # - Each period (or data point) will have average, minimum and maximum
    # - The backend returns arrays for:
    #   labels : timestamp for a max of 60 datapoints, corresponding computed begintime of the 60 periods
    #   data : 60 points max, corresponding to the average value for each period
    #   low : 60 points max, corresponding to the minimum value for each period
    #   high : 60 points max, corresponding to the maximum value for each period
    # - for mobile apps, since screen is small, it shall pass 30 points as a parameter so that backend will use 30 period instead of 60
    # 
    # Computation of time range and period:
    # TimeRange  5 mins    300 secs  =    5 secs Period x 60 points - no averaging (actual values are returned)
    # TimeRange 15 mins    900 secs  =   15 secs Period x 60 points - average all points w/in 15secs
    # TimeRange 30 mins   1800 secs  =   30 secs Period x 60 points - average all points w/in 30secs
    # TimeRange 60 mins   3600 secs  =   60 secs Period x 60 points - ...
    # TimeRange  3 hrs   10800 secs  =  180 secs Period x 60 points - ...
    # TimeRange  6 hrs   21600 secs  =  360 secs Period x 60 points - ...
    # TimeRange 12 hrs   43200 secs  =  720 secs Period x 60 points - ...
    # TimeRange 24 hrs   86400 secs  = 1440 secs Period x 60 points - ...
    # 
    # 7 days    86400*7=604800
    # 
    # 4 weeks   604800*4=2419200
    # 
    # 12 months 2419200=29030400
    # 
    # TimeRange 3  days
    # TimeRange 7  days
    # TimeRange 2  weeks
    # TimeRange 4  weeks
    # TimeRange 3  months
    # TimeRange 6  months
    # TimeRange 12 months
    # 
    # Consider the simplest use case: 
    # sensor data is sending every 5 seconds, time range=15 mins, 15 secs Period
    # - there will be 60 periods
    # - for every period, there will be at most 15/5=3 datapoints
    # - for every period, the average, minimum and maximum will be computed
    # Computing for endtime and begintime:
    # - endtime = int(currenttime/period)*period
    #   begintime = endtime-timerange+period
    # - endtime must be computed with /period x period to round down the nearest divisible by period, so that begintime can be the same for the upcoming data points of the 60th period, that is, all periods 1st-59th will be constant, except for the last period, 60th
    # 
    #   ex. timerange=15mins, period=15secs
    #   begintime: 8:45:15 - begintime is the same for the endtimes 9:00:00-9:00:14
    #     1st period
    #        8:45:15
    #        8:45:20
    #        8:45:25
    #      60th period
    #        endtime: 9:00:00 
    #          9:00:00 
    #        endtime: 9:00:05
    #          9:00:00 
    #          9:00:05 
    #        endtime: 9:00:10
    #          9:00:00 
    #          9:00:05 
    #          9:00:10 
    #      begintime: 8:45:30 - begintime is the same for the endtimes 9:00:15-9:00:29
    #      1st period
    #        8:45:15
    #        8:45:20
    #        8:45:25
    #      60th period
    #        endtime: 9:00:15 - 1st
    #        endtime: 9:00:20 - 2nd
    #        endtime: 9:00:25 - 3rd
    #
    # - when sensordata is sent every 5secs, since timerange=15mins, period=15secs, then 1 period will cover 15/5=3 datapoints.
    #  then for 1st,2nd,3rd datapoint of every period, all preceding periods will be constant (the same points are for averaging)
    #  that is, only the last period will change computation until the (15/5=3) 3rd data point of the 60th period arrives.
    #
    #- otherwise, if this is not done, everytime there is a new data, different datapoints will be average for every period (as shown below), thus making the graph constantly changing everything, not good to look at.
    #      endtime: 9:00:00
    #      1st period
    #        8:45:15
    #        8:45:20
    #        8:45:25
    #      endtime: 9:00:05
    #      1st period
    #        8:45:20
    #        8:45:25
    #        8:45:30
    #
    #- with the adaptive endtime and begintime computation, the graph changes and only "shifts to the left" every after period (in this case, period=15 seconds) instead of every after new sensor data publish (5seconds).
    #
    #
    # what get_sensor_reading_dataset_by_deviceid_timebound() does is 
    #
    # for every datapoint in a period, it will put it in a bucket.
    # on last datapoint of the period, it will take the average, minimum and maximum of the datapoints in the temporary bucket
    # then it repeats this until all periods within datebegin and dateend are all covered
    #
    # date[0] = datestart
    # date[1]
    # ..
    # date[61] = dateend
    #
    # date[0]-date[1] is 1 period // can contain multiple data points
    #   ex. 1 period is 30 secs; if rate is 5 seconds of the sensor, then you have 6 datapoints in 1 period
    #   you get the average, minimum and maximum of that 6 datapoints.
    #   and that will correspond to data[0], low[0], high[0]
    #

    ########################################################################################################
    #
    # GET PERIPHERAL SENSOR READINGS DATASET (FILTERED)
    #
    # - Request:
    #   POST /devices/sensors/readings/dataset
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #   data: {'devicename': string, 'class': string, 'status': string, 'timerange': string, 'points': int, 'index': int, 'checkdevice': int}
    #   // devicename can be "All devices" or the devicename of specific device
    #   // class can be ["All classes", "potentiometer", "temperature", "humidity", "anemometer", "battery", "fluid"]
    #   // status can be ["All online/offline", "online", "offline"]
    #   // timerange can be:
    #        Last 5 minutes
    #        Last 15 minutes
    #        Last 30 minutes
    #        Last 60 minutes
    #        Last 3 hours
    #        Last 6 hours
    #        Last 12 hours
    #        Last 24 hours
    #        Last 3 days
    #        Last 7 days
    #        Last 2 weeks
    #        Last 4 weeks
    #        Last 3 months
    #        Last 6 months
    #        Last 12 months
    #   // points can be 60, 30 or 15 points (for mobile, since screen is small, should use 30 or 15 instead of 60)
    #   // index is 0 by default. 
    #        To view the timeranges above, index is 0
    #        To view the next timerange, ex. "Last Last 5 minutes", the previous instance, index is 1. and so on...
    #   // checkdevice is 1 or 0. 1 if device status needs to be check if device is online and if sensor is active
    #
    # - Response:
    #   { 'status': 'OK', 'message': string, 
    #     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string, 'readings': [{'timestamp': float, 'value': float, 'subclass': {'value': float}}], 'enabled': int}, ...] }
    #   { 'status': 'NG', 'message': string }
    #
    #
    # DELETE PERIPHERAL SENSOR READINGS DATASET (FILTERED)
    #
    # - Request:
    #   POST /devices/sensors/readings/dataset
    #   headers: { 'Authorization': 'Bearer ' + token.access }
    #   data: {'devicename': string}
    #   // devicename can be "All devices" or the devicename of specific device
    #
    # - Response:
    #   { 'status': 'OK', 'message': string }
    #   { 'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def get_all_device_sensors_enabled_input_readings_dataset_filtered(self):

        #start_time = time.time()

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get All Device Sensors Dataset: Invalid authorization header\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get All Device Sensors Dataset: Token expired\r\n')
            return response, status.HTTP_401_UNAUTHORIZED
        #print('get_all_device_sensors_enabled_input_readings_dataset_filtered {}'.format(username))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get All Device Sensors Dataset: Token expired [{}] DATETIME {}\r\n'.format(username, datetime.datetime.now()))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get All Device Sensors Dataset: Token is invalid [{}]\r\n'.format(username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        if flask.request.method == 'POST':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Get All Device Sensors Dataset: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # get filter parameters
            filter = flask.request.get_json()
            if filter.get("devicename") is None or filter.get("class") is None or filter.get("status") is None or filter.get("timerange") is None or filter.get("points") is None or filter.get("index") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            #print(filter["timerange"])
            timerange = [int(s) for s in filter["timerange"].split() if s.isdigit()][0]
            timeranges = ["minute", "hour", "day", "week", "month", "year"]
            multiplier = [60, 3600, 86400, 604800, 2592000, 31536000]
            for x in range(len(timeranges)):
                if timeranges[x] in filter["timerange"]:
                    timerange *= multiplier[x]
                    break

            devices = []
            if filter["devicename"] == "All devices":
                devices = self.database_client.get_devices(entityname)
            else:
                devices.append({"devicename": filter["devicename"]})

            # get active sensors for each device
            checkdevice = 1
            if filter.get("checkdevice") is not None:
                checkdevice = filter["checkdevice"]
            #print(checkdevice)
            if False: #checkdevice != 0:
                thread_list = []
                for device in devices:
                    devicename = device["devicename"]
                    thr = threading.Thread(target = self.get_running_sensors, args = (token, username, devicename, device, ))
                    thread_list.append(thr) 
                    thr.start()
                for thr in thread_list:
                    thr.join()

            # get all sensors based on specified filter
            sensors_list = []
            source = None
            number = None
            sensorclass = None
            sensorstatus = None
            sensordevicename = filter["devicename"]
            if sensordevicename == "All devices":
                sensordevicename = None
            filter["peripheral"] = "All peripherals" # updated for LDSU
            #if filter["peripheral"] != "All peripherals":
            #    source = filter["peripheral"][:len(filter["peripheral"])-1].lower()
            #    number = filter["peripheral"][len(filter["peripheral"])-1:]
            if filter["class"] != "All classes":
                sensorclass = filter["class"]
            if filter["status"] != "All online/offline":
                sensorstatus = 1 if filter["status"] == "online" else 0
            sensors_list = self.database_client.get_all_device_sensors_enabled_input(entityname, sensordevicename, source, number, sensorclass, sensorstatus)
            #print("1")
            #rest_api_utils.utils().print_json(sensors_list)
            if len(sensors_list):
                sensors_list.sort(key=self.sort_by_sensorname)

            # get time bound
            maxpoints = filter["points"] # tested with 60 points
            if (maxpoints != 60 and maxpoints != 30 and maxpoints != 15):
                maxpoints = 60
            period = int(timerange/maxpoints)
            maxpoints += 1
            dateend = int(time.time())
            #print(dateend)
            if period == 5:
                dateend = int(dateend/period) * period + period
                # adjust based on specified index
                if filter["index"] != 0:
                    dateend -= filter["index"] * timerange
                datebegin = dateend - timerange - period
            else:
                # adjust for adaptive begin and end "shift to left"
                dateend = int(dateend/period) * period# + period
                # adjust based on specified index
                if filter["index"] != 0:
                    dateend -= filter["index"] * timerange
                #print(dateend)
                # add - period since we added 1 point
                datebegin = dateend - timerange - period 
            #print("datebegin={} dateend={} period={} maxpoints={}".format(datebegin, dateend, period, maxpoints))

            # add sensor properties to the result filtered sensors
            thread_list = []
            if filter["devicename"] != "All devices":
                #print("xxxxxxxxxxxx")
                readings = self.database_client.get_device_sensors_readings(entityname, filter["devicename"])
                for sensor in sensors_list:
                    thr = threading.Thread(target = self.get_sensor_data_threaded, args = (sensor, entityname, datebegin, dateend, period, maxpoints, readings, filter["devicename"], None, ))
                    thread_list.append(thr) 
                    thr.start()
            else:
                readings = self.database_client.get_user_sensors_readings(entityname)
                for sensor in sensors_list:
                    thr = threading.Thread(target = self.get_sensor_data_threaded, args = (sensor, entityname, datebegin, dateend, period, maxpoints, readings, None, devices, ))
                    thread_list.append(thr) 
                    thr.start()
            for thr in thread_list:
                thr.join()

            if len(sensors_list):
                sensors_list.sort(key=self.sort_by_devicename)


            # compute stats, summary and comparisons
            stats = None
            summary = None
            comparisons = None
            usages = None
            if checkdevice != 0:
                # stats
                output_sensors_list = self.database_client.get_all_device_sensors_enabled_input(entityname, sensordevicename, source, number, sensorclass, sensorstatus, type="output")
                stats = {"sensors": {}, "devices": {}}
                try:
                    stats["sensors"] = self.get_sensor_stats(sensors_list+output_sensors_list)
                except:
                    pass
                try:
                    stats["devices"] = self.get_device_stats(entityname, devices, sensordevicename)
                except:
                    pass

                # summary
                summary = {"sensors": [], "devices": []}
                try:
                    summary["sensors"] = self.get_sensor_summary(entityname, devices, sensordevicename)
                except:
                    pass
                try:
                    summary["devices"] = self.get_device_summary(entityname, devices, sensordevicename)
                except:
                    pass

                # comparisons
                try:
                    comparisons = self.get_sensor_comparisons(devices, sensors_list)
                except:
                    pass

                usages = self.get_usage()

            #print(time.time()-start_time)
            msg = {'status': 'OK', 'message': 'Get All Device Sensors Dataset queried successfully.', 'sensors': sensors_list}
            if stats:
                msg['stats'] = stats
            if summary:
                msg['summary'] = summary
            if comparisons:
                msg['comparisons'] = comparisons
            if usages:
                msg['usages'] = usages

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Delete All Device Sensors Dataset: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            filter = flask.request.get_json()
            if filter.get("devicename") is None:
                response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
                print('\r\nERROR Get All Device Sensors Dataset: Empty parameter found\r\n')
                return response, status.HTTP_400_BAD_REQUEST

            if filter["devicename"] == "All devices":
                devices = self.database_client.get_devices(entityname)
                for device in devices:
                    self.database_client.delete_device_sensor_reading(entityname, device["devicename"])
            else:
                self.database_client.delete_device_sensor_reading(entityname, filter["devicename"])

            msg = {'status': 'OK', 'message': 'Delete All Device Sensors Dataset queried successfully.'}


        if new_token:
            msg['new_token'] = new_token
        response = json.dumps(msg)
        #print('\r\nGet All Device Sensors Dataset successful: {} {} {} sensors\r\n'.format(username, devicename, len(sensors)))
        return response


    ########################################################################################################
    #
    # GET I2C DEVICES READINGS (per peripheral slot)
    #
    # - Request:
    #   GET /devices/device/<devicename>/i2c/NUMBER/sensors/readings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
    #   {'status': 'NG', 'message': string }
    #
    # GET ADC DEVICES READINGS (per peripheral slot)
    # GET 1WIRE DEVICES READINGS (per peripheral slot)
    # GET TPROBE DEVICES READINGS (per peripheral slot)
    #
    # - Request:
    #   GET /devices/device/<devicename>/adc/NUMBER/sensors/readings
    #   GET /devices/device/<devicename>/1wire/NUMBER/sensors/readings
    #   GET /devices/device/<devicename>/tprobe/NUMBER/sensors/readings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
    #   {'status': 'NG', 'message': string }
    #
    #
    # DELETE I2C DEVICES READINGS (per peripheral slot)
    #
    # - Request:
    #   DELETE /devices/device/<devicename>/i2c/NUMBER/sensors/readings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string }
    #   {'status': 'NG', 'message': string }
    #
    # DELETE ADC DEVICES READINGS (per peripheral slot)
    # DELETE 1WIRE DEVICES READINGS (per peripheral slot)
    # DELETE TPROBE DEVICES READINGS (per peripheral slot)
    #
    # - Request:
    #   DELETE /devices/device/<devicename>/adc/NUMBER/sensors/readings
    #   DELETE /devices/device/<devicename>/1wire/NUMBER/sensors/readings
    #   DELETE /devices/device/<devicename>/tprobe/NUMBER/sensors/readings
    #   headers: {'Authorization': 'Bearer ' + token.access}
    #
    # - Response:
    #   {'status': 'OK', 'message': string }
    #   {'status': 'NG', 'message': string }
    #
    ########################################################################################################
    def get_xxx_sensors_readings(self, devicename, xxx, number):

        # check number parameter
        if int(number) > 4 or int(number) < 1:
            response = json.dumps({'status': 'NG', 'message': 'Invalid parameters'})
            print('\r\nERROR Invalid parameters\r\n')
            return response, status.HTTP_400_BAD_REQUEST

        # get token from Authorization header
        auth_header_token = rest_api_utils.utils().get_auth_header_token()
        if auth_header_token is None:
            response = json.dumps({'status': 'NG', 'message': 'Invalid authorization header'})
            print('\r\nERROR Get {} Sensor: Invalid authorization header\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        token = {'access': auth_header_token}

        # get username from token
        username = self.database_client.get_username_from_token(token)
        if username is None:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensor: Token expired\r\n'.format(xxx))
            return response, status.HTTP_401_UNAUTHORIZED
        print('get_{}_sensor_readings {} devicename={} number={}'.format(xxx, username, devicename, number))

        # check if a parameter is empty
        if len(username) == 0 or len(token) == 0 or len(devicename) == 0:
            response = json.dumps({'status': 'NG', 'message': 'Empty parameter found'})
            print('\r\nERROR Get {} Sensor: Empty parameter found\r\n'.format(xxx))
            return response, status.HTTP_400_BAD_REQUEST

        # check if username and token is valid
        verify_ret, new_token = self.database_client.verify_token(username, token)
        if verify_ret == 2:
            response = json.dumps({'status': 'NG', 'message': 'Token expired'})
            print('\r\nERROR Get {} Sensor: Token expired [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED
        elif verify_ret != 0:
            response = json.dumps({'status': 'NG', 'message': 'Unauthorized access'})
            print('\r\nERROR Get {} Sensor: Token is invalid [{}]\r\n'.format(xxx, username))
            return response, status.HTTP_401_UNAUTHORIZED


        # get entity using the active organization
        orgname, orgid = self.database_client.get_active_organization(username)
        if orgname is not None:
            # has active organization
            entityname = "{}.{}".format(orgname, orgid)
        else:
            # no active organization, just a normal user
            entityname = username


        source = "{}{}".format(xxx, number)
        if flask.request.method == 'GET':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.READ) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Get Peripheral Sensor Readings: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            if True:
                # get enabled input sensors
                sensors = self.database_client.get_sensors_enabled_input(entityname, devicename, xxx, number)

                # get sensor reading for each enabled input sensors
                for sensor in sensors:
                    address = None
                    if sensor.get("address") is not None:
                        address = sensor["address"]
                    sensor_reading = self.database_client.get_sensor_reading(entityname, devicename, source, address)
                    sensor['readings'] = sensor_reading

                msg = {'status': 'OK', 'message': 'Sensors readings queried successfully.', 'sensor_readings': sensors}
                if new_token:
                    msg['new_token'] = new_token
                response = json.dumps(msg)
                print('\r\nSensors readings queried successful: {}\r\n{}\r\n'.format(entityname, response))
                return response
            else:
                # get sensors readings
                sensor_readings = self.database_client.get_sensors_readings(entityname, devicename, source)

                msg = {'status': 'OK', 'message': 'Sensors readings queried successfully.', 'sensor_readings': sensor_readings}
                if new_token:
                    msg['new_token'] = new_token
                response = json.dumps(msg)
                print('\r\nSensors readings queried successful: {}\r\n{}\r\n'.format(entityname, response))
                return response

        elif flask.request.method == 'DELETE':
            if orgname is not None:
                # check authorization
                if self.database_client.is_authorized(username, orgname, orgid, database_categorylabel.DASHBOARDS, database_crudindex.DELETE) == False:
                    response = json.dumps({'status': 'NG', 'message': 'Authorization failed! User is not allowed to access resource. Please check with the organization owner regarding policies assigned.'})
                    print('\r\nERROR Get Peripheral Sensor Readings: Authorization not allowed [{}]\r\n'.format(username))
                    return response, status.HTTP_401_UNAUTHORIZED

            # delete sensors readings
            self.database_client.delete_sensors_readings(entityname, devicename, source)

            msg = {'status': 'OK', 'message': 'Sensors readings deleted successfully.'}
            if new_token:
                msg['new_token'] = new_token
            response = json.dumps(msg)
            print('\r\nSensors readings deleted successful: {}\r\n{}\r\n'.format(entityname, response))
            return response

