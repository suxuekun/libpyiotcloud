from datetime import datetime, timezone, timedelta
from dashboards.dtos.chart_sensor_response import *
from dashboards.dtos.chart_sensor_query import ChartSensorQuery
import statistics


def setup_empty_int_arrays(size: int):
    arrays = []
    for i in range(size):
        arrays.append(None)
    return arrays

def setup_empty_mobile_dataset_sensor_response(size: int):
    arrays = []
    for i in range(size):
        item = MobileDatasetsSensorResponse()
        item.x = None
        item.y = None
        item.low = None
        item.y = None
        arrays.append(item)
    return arrays

def map_to_sensor_dataset_mobile(dataset, points: int, timestamp: int, minutes: int, customMinutes: int = 0):

    defaultTimeRangeInSecond = 5
    minutes = minutes
    if customMinutes != 0:
        minutes = customMinutes

    seconds = minutes * 60
    timeRange = seconds / points
    timeStart = datetime.fromtimestamp(
        timestamp) - timedelta(minutes=minutes)
    timeEnd = timeStart + timedelta(seconds=timeRange)

    datasetResponse = []
    totalPoints = points + 1
    for index in range(totalPoints):

        item = MobileDatasetsSensorResponse()
        item.x = int(timeStart.timestamp())
        pointsValue = find_value_with_timestamp_in_range(
            dataset, timeStart)

        if len(pointsValue) > 0:
            if minutes == 5:
                item.y= get_value_when_minutues_is_five(pointsValue)
                item.low = None
                item.high = None
            else:
                item.y = round(statistics.mean(pointsValue), 2)
                item.low = min(pointsValue)
                item.high = max(pointsValue)
        else:
            item.y = None
            item.low = None
            item.high = None

        # Renew plan for timeStart and timeEnd
        timeStart = timeEnd
        timeEnd = timeStart + timedelta(seconds=timeRange)
        datasetResponse.append(item)

    return datasetResponse


def map_to_sensor_dataset(dataset, points: int, timestamp: int, minutes: int, customMinutes: int = 0):

    defaultTimeRangeInSecond = 5

    minutes = minutes
    if customMinutes != 0:
        minutes = customMinutes

    seconds = minutes * 60
    timeRange = seconds / points
    timeStart = datetime.fromtimestamp(
        timestamp) - timedelta(minutes=minutes)
    timeEnd = timeStart + timedelta(seconds=timeRange)

    # points is 30 => 31 points
    totalPoints = points + 1
    data = setup_empty_int_arrays(totalPoints)
    low = setup_empty_int_arrays(totalPoints)
    high = setup_empty_int_arrays(totalPoints)
    timeArrays = []

    for index in range(totalPoints):
        timeArrays.append(int(timeStart.timestamp()))
        pointsValue = find_value_with_timestamp_in_range(
            dataset, timeStart)

        if len(pointsValue) > 0:
            if minutes == 5:
                data[index] = get_value_when_minutues_is_five(pointsValue)
                low[index] = None
                high[index] = None
            else:
                data[index] = round(statistics.mean(pointsValue), 2)
                low[index] = min(pointsValue)
                high[index] = max(pointsValue)
        # Renew plan for timeStart and timeEnd
        timeStart = timeEnd
        timeEnd = timeStart + timedelta(seconds=timeRange)

    datasetResponse = DatasetsSensorResponse()
    datasetResponse.data = data
    datasetResponse.low = low
    datasetResponse.high = high
    datasetResponse.labels = timeArrays

    return datasetResponse


def find_value_with_timestamp_in_range(datasets, timeStart):
    values = []
    timePreviors = (timeStart - timedelta(seconds=5)).timestamp()
    timeNext = (timeStart + timedelta(seconds=5)).timestamp()
    for dataset in datasets:
        if dataset["timestamp"] >= timePreviors and dataset["timestamp"] <= timeNext:
            values.append(dataset["value"])
        else:
            if dataset["timestamp"] > timeNext:
                return values

    return values


def get_value_when_minutues_is_five(values: []):

    if len(values) == 0:
        return 0

    # It'mean time range is 10 seconds has 2 value, we will get first value
    return values[0]


def map_to_charts_sensor_response(charts, dictSensors: {}, query: ChartSensorQuery, customMinutes: int = 0):

    response = list(map(lambda chart: map_to_chart_sensor_response(
        chart, dictSensors.get(chart.get("deviceId")), query, customMinutes=customMinutes), charts))
    return response


def map_to_chart_sensor_response(chart, sensor, query: ChartSensorQuery, customMinutes: int = 0) -> SensorResponse:

    device = SensorResponse()
    device.id = sensor["sensorId"]
    device.source = sensor["source"]
    device.number = sensor["number"]
    device.sensorName = sensor["sensorname"]
    device.port = sensor["port"]
    device.name = sensor["name"]
    device.sensorClass = sensor["class"]
    device.gatewayUUID = sensor["gatewayUUID"]
    device.gatewayName = sensor["gatewayName"]
    device.minmax = sensor["minmax"]
    device.accuracy = float(sensor["accuracy"])
    device.unit = sensor["unit"]
    device.format = sensor["format"]
    device.enabled = sensor["enabled"]
    
    sensorReadings = sensor["sensor_readings"]
    readingsResponse = ReadingSensorResponse()
    if sensor["sensor_readings"] is not None:
        readingsResponse.value = sensorReadings["value"]
        readingsResponse.highest = sensorReadings["highest"]
        readingsResponse.lowest = sensorReadings["lowest"]
    else:
        readingsResponse.value = 0
        readingsResponse.highest = 0
        readingsResponse.lowest = 0

    # Minutes
    minutes = query.minutes
    if customMinutes != 0:
        minutes = customMinutes

    # Mobile response
    if query.isMobile:
        mobileResponse = MobileChartSensorResponse()
        mobileResponse.selectedMinutes = minutes
        mobileResponse.id = chart["_id"]
        mobileResponse.chartTypeId = chart["chartTypeId"]
        mobileResponse.device = device
        mobileResponse.readings = readingsResponse
        mobileResponse.datasetsEx = []
        if sensor["dataset"] is not None:
            mobileResponse.datasetsEx = map_to_sensor_dataset_mobile(
                sensor["dataset"], query.points, query.timestamp, query.minutes, customMinutes=minutes)
           
        return mobileResponse.to_primitive()

    # Web Response
    response = WebChartSensorResponse()
    response.id = chart["_id"]
    response.chartTypeId = chart["chartTypeId"]
    response.device = device
    response.readings = readingsResponse
    response.selectedMinutes = minutes

    datasets = DatasetsSensorResponse()
    if sensor["dataset"] is not None:
        datasets = map_to_sensor_dataset(
            sensor["dataset"], query.points, query.timestamp, query.minutes, customMinutes=minutes)

    response.datasets = datasets

    return response.to_primitive()