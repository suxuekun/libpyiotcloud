
from datetime import datetime, timezone, timedelta
from dashboards.repositories.dashboard_repository import IDashboardRepository
from dashboards.repositories.chart_sensor_repository import IChartSensorRepository
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards.models.dashboard import Dashboard
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards.models.chart import ChartSensor
from shared.core.response import Response
from schematics.exceptions import ValidationError, ModelValidationError
from dashboards.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from dashboards.repositories.device_repository import IDeviceRepostory
from dashboards.dtos.chart_sensor_dto import ChartSensorDto
from dashboards.utils.mapper_chart_sensor_response import *
from dashboards.dtos.chart_sensor_query import ChartSensorQuery, ChartComparisonQuery
from dashboards.services.dashboard_service import DashboardService
from dashboards.exceptions.chart_sensor_query_exception import ChartSensorQueryException
from dashboards.repositories.sensor_repository import ISensorRepository
from dashboards.repositories.sensor_readings_latest_repository import ISensorReadingsLatestRepository
import time


class ChartSensorService:

    def __init__(self, dashboardRepository: IDashboardRepository,
                 chartRepository: IChartSensorRepository,
                 attributeRepository: IGatewayAttributeRepository,
                 deviceRepository: IDeviceRepostory,
                 sensorRepository: ISensorRepository,
                 sensorReadingsLatestRepository: ISensorReadingsLatestRepository,
                 dashboardService: DashboardService):

        self.deviceRepository = deviceRepository
        self.dashboardRepository = dashboardRepository
        self.chartRepository = chartRepository
        self.attributeRepository = attributeRepository
        self.sensorRepository = sensorRepository
        self.sensorReadingsLatestRepository = sensorReadingsLatestRepository
        self.dashboardService = dashboardService
        self.tag = type(self).__name__

    def create(self, dashboardId: str, userId: str, dto: ChartSensorDto):
        try:
            dto.validate()
            sensor = self.sensorRepository.get_by_source_and_number(
                dto.source, dto.number)

            if sensor is None:
                return Response.fail("This device was not existed")

            # if sensor["enabled"] == 0:
            #     return Response.fail("This device should be enabled")

            sameChart = self.chartRepository.get_same_chart(dashboardId,sensor["_id"])

            if sameChart is not None:
                return Response.fail("Sorry, This chart should not have same device")

            # Create chart
            chart = ChartSensor.create(
                dashboardId=dashboardId, userId=userId, dto=dto, sensorId=sensor["_id"])
            chartId = self.chartRepository.create(
                chart.model.to_primitive())

            # Update dashboard
            self.dashboardService.add_chart_sensor(dashboardId, chartId)

            return Response.success_without_data(message="Create chart sensor successfully")

        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except CreatedExeception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, Create chart gatway faield")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def delete(self, dashboardId: str, chartId: str):
        try:
            self.chartRepository.delete(chartId)
            # Notify to dashboard update
            self.dashboardService.remove_chart_sensor(dashboardId, chartId)
            return Response.success_without_data(message="Delete chart sensor successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete chart gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets(self, dashboardId: str, userId: str, query: ChartSensorQuery):
        try:

            timestart = time.time()
            query.validate()

            chartEntites = self.chartRepository.gets_charts(
                dashboardId, userId)

            calculateMultiTimeRange = 1
            if query.isRealtime == False:
                calculateMultiTimeRange= query.timeSpan + 1
            
            sensorIds = []
            # Not have query.chartsId
            if len(query.chartsId) == 0:
                sensorIds = list(map(lambda c: c["deviceId"], chartEntites))
                sensors = self.sensorRepository.gets_sensors(ids=sensorIds)

                if len(sensors) == 0:
                    return Response.success([], message="Get chart responses successfully")
                
                lastMinutes = datetime.fromtimestamp(
                    query.timestamp) - timedelta(minutes=query.minutes * calculateMultiTimeRange)
                results = self.sensorReadingsLatestRepository.gets_dataset(
                    sensors, int(lastMinutes.timestamp()), query.timestamp)

                dictSensors = {}
                for r in results:
                    dictSensors[r.get("sensorId", "")] = r

                response = map_to_charts_sensor_response(
                    charts=chartEntites, dictSensors=dictSensors, query=query)
                
                return Response.success(data=response, message="Get chart responses successfully")

            dictSelectedMinutesAndChartsId = {}
            for i in range(len(query.selectedMinutes)):
                dictSelectedMinutesAndChartsId[query.chartsId[i]] = query.selectedMinutes[i]

            selectedSensorIds = []
            selectedCharts = []
            unSelectedCharts = []
            results = []
            for chart in chartEntites:
                if query.check_id_in_chartsId(chart["_id"]):
                    selectedSensorIds.append(chart["deviceId"])
                    selectedCharts.append(chart)
                else:
                    sensorIds.append(chart["deviceId"])
                    unSelectedCharts.append(chart)
            response = []
            sensors = []
            # Try to get charts with default minutes
            if len(sensorIds) != 0:
                sensors = self.sensorRepository.gets_sensors(ids=sensorIds)
                lastMinutes = datetime.fromtimestamp(
                    query.timestamp) - timedelta(minutes=query.minutes * calculateMultiTimeRange)
                    
                firstResults = self.sensorReadingsLatestRepository.gets_dataset(
                    sensors, int(lastMinutes.timestamp()), query.timestamp)
                results = firstResults
                dictSensors = {}
                for r in results:
                    dictSensors[r.get("sensorId", "")] = r
                response = map_to_charts_sensor_response(
                    charts=unSelectedCharts, dictSensors=dictSensors, query=query)

            if len(selectedSensorIds) != len(query.selectedMinutes):
                LoggerService().error("Selected Charts does not have the same size", tag=self.tag)
                return Response.fail("Sorry, there is something wrong")

            selectedSensors = self.sensorRepository.gets_sensors(
                ids=selectedSensorIds)

            maxMinutes = max(query.selectedMinutes)
            lastMinutes = datetime.fromtimestamp(
                query.timestamp) - timedelta(minutes=maxMinutes * calculateMultiTimeRange)
            secondResults = self.sensorReadingsLatestRepository.gets_dataset(
                selectedSensors, int(lastMinutes.timestamp()), query.timestamp)
            dictSensors = {}

            if len(selectedCharts) != len(secondResults):
                LoggerService().error("Selected Charts does not have the same size", tag=self.tag)
                return Response.fail("Sorry, there is something wrong")

            # Expected that len of selectedCharts and secondResults has the same result
            for i in range(len(selectedCharts)):
                chart = selectedCharts[i]
                sensor = secondResults[i]
                itemResponse = map_to_chart_sensor_response(
                    chart, sensor, query, customMinutes=dictSelectedMinutesAndChartsId[chart["_id"]])
                response.append(itemResponse)

            return Response.success(data=response, message="Get chart responses successfully")

        except ChartSensorQueryException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong!")
        
    def compare(self, dashboardId: str, userId: str, query: ChartComparisonQuery):
        try:
            query.validate()

            chartEntites = self.chartRepository.gets_with_ids(query.chartsId)

            calculateMultiTimeRange = 1
            if query.isRealtime == False:
                calculateMultiTimeRange= query.timeSpan + 1


            sensorIds = list(map(lambda c: c["deviceId"], chartEntites))

            # Check sensors has the same sensor class
            sensors = self.sensorRepository.gets_sensors(sensorIds)
            if len(sensors) == 0:
                return Response.fail("These sensors device are not existed")

            firstSensor = sensors[0]
            i = 1
            while i < len(sensors):
                if firstSensor["class"] != sensors[i]["class"]:
                    return Response.fail("These sensors must have the same sensor class")
                i += 1

            lastMinutes = datetime.fromtimestamp(
                query.timestamp) - timedelta(minutes=query.minutes * calculateMultiTimeRange)
            seconds = query.minutes * 60
            timeRange = seconds / query.points
            timEnd = datetime.fromtimestamp(
                query.timestamp) + timedelta(seconds=timeRange)

            results = self.sensorReadingsLatestRepository.gets_dataset(
                sensors, int(lastMinutes.timestamp()), timEnd)

            dictSensors = {}
            for r in results:
                dictSensors[r["sensorId"]] = r

            response = map_to_charts_sensor_response(
                charts=chartEntites, dictSensors=dictSensors, query=query)

            return Response.success(data=response, message="Get chart responses successfully")

        except ChartSensorQueryException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def get(self, dashboarId: str, userId: str, chartId: str, query: ChartSensorQuery):
        try:
            query.validate()

            chartEntity = self.chartRepository.getById(chartId)
            sensor = self.sensorRepository.getById(chartEntity["deviceId"])

            calculateMultiTimeRange = 1
            if query.isRealtime == False:
                calculateMultiTimeRange= query.timeSpan + 1
            
            lastMinutes = datetime.fromtimestamp(
                query.timestamp) - timedelta(minutes=query.minutes * calculateMultiTimeRange)

            results = self.sensorReadingsLatestRepository.gets_dataset(
                [sensor], int(lastMinutes.timestamp()), query.timestamp)

            if len(results) == 0:
                return Response.success(data={}, message="Get chart responses successfully")

            result = results[0]
            response = map_to_chart_sensor_response(
                chart=chartEntity, sensor=result, query=query)

            return Response.success(data=response, message="Get chart responses successfully")

        except ChartSensorQueryException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def delete_by_deviceId(self, deviceId: str):
        try:
            charts = self.chartRepository.get_chart_by_device(deviceId)

            if charts is None:
                LoggerService().error("Chart is not existed with deviceId: " + deviceId, tag=self.tag)
                return False

            self.chartRepository.delete_many_by_id(
                list(map(lambda c: c["_id"], charts)))

            # Notify to dashboard handler
            chartsWithDashboards = {}
            for item in chartsWithDashboards:
                chartsWithDashboard[item["dashboardId"]] = item["_id"]

            self.dashboardService.remove_many_charts_sensors_in_many_dashboards(
                chartsWithDashboards)
            return True

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

    def delete_by_dashboard(self, dashboardId: str):
        try:
            self.chartRepository.delete_many_by_dashboard(dashboardId)
            return True

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")