
from datetime import datetime, timezone, timedelta
from dashboards.repositories.dashboard_repository import IDashboardRepository
from dashboards.repositories.chart_repository import IChartRepository
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards.models.dashboard import Dashboard
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards.models.chart import Chart
from shared.core.response import Response
from schematics.exceptions import ValidationError, ModelValidationError
from dashboards.utils.mapper_util import map_chart_gateway_to_response
from dashboards.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from dashboards.repositories.device_repository import IDeviceRepostory
from dashboards.dtos.chart_sensor_dto import ChartSensorDto
from dashboards.repositories.sensor_repository import ISensorRepository
from dashboards.utils.mapper_chart_sensor_response import *
from dashboards.dtos.chart_sensor_query import ChartSensorQuery, ChartComparisonQuery
from dashboards.services.dashboard_service import DashboardService
from dashboards.exceptions.chart_sensor_query_exception import ChartSensorQueryException


class ChartSensorService:

    def __init__(self, dashboardRepository: IDashboardRepository,
                 chartRepository: IChartRepository,
                 attributeRepository: IGatewayAttributeRepository,
                 deviceRepository: IDeviceRepostory,
                 sensorRepository: ISensorRepository,
                 dashboardService: DashboardService):

        self.deviceRepository = deviceRepository
        self.dashboardRepository = dashboardRepository
        self.chartRepository = chartRepository
        self.attributeRepository = attributeRepository
        self.sensorRepository = sensorRepository
        self.dashboardService = dashboardService
        self.tag = type(self).__name__

    def create(self, dashboardId: str, dto: ChartSensorDto):
        try:
            dto.validate()
            sensor = self.sensorRepository.getById(dto.deviceId)

            if sensor is None:
                return Response.fail("This device was not existed")

            if sensor["enabled"] == 0:  
                return Response.fail("This device should be enabled")

            dashboardEntity = self.dashboardRepository.getById(dashboardId)

            dashoard = Dashboard.to_domain(dashboardEntity)

            # Create chart
            chart = Chart.create_for_sensor(
                dashboardId=dashoard.model._id, userId=dashoard.model.userId, dto=dto)
            chartId = self.chartRepository.create(
                chart.model.to_primitive())

            # Update dashboard
            dashoard.add_chart_sensor(chartId)
            self.dashboardRepository.update(
                dashboardId, dashoard.model.to_primitive())

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
            return Response.success_without_data(message="Delete chart gateway successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete chart gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets(self, dashboardId: str, userId: str, query: ChartSensorQuery):
        try:
            query.validate()

            chartEntites = self.chartRepository.get_charts_sensor(
                dashboardId, userId)

            sensorIds = list(map(lambda c: c["deviceId"], chartEntites))

            lastMinutes = datetime.fromtimestamp(
                query.timestamp) - timedelta(minutes=query.minutes)

            results = self.sensorRepository.get_data_reading(
                sensorIds, int(lastMinutes.timestamp()))

            dictSensors = {}
            for r in results:
                dictSensors[r["_id"]] = r

            response = map_to_charts_sensor_response(
                charts=chartEntites, dictSensors=dictSensors, query=query)
            return Response.success(data=response, message="Get chart responses successfully")

        except ChartSensorQueryException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def compare(self, dashboardId: str, userId: str, query: ChartComparisonQuery):
        try:
            query.validate()

            chartEntites = self.chartRepository.gets_with_ids(query.chartsId)
            sensorIds = list(map(lambda c: c["deviceId"], chartEntites))

            # Check sensors has the same sensor class
            sensors = self.sensorRepository.gets_with_ids(sensorIds)
            if len(sensors) == 0:
                return Response.fail("These sensors device are not existed")

            firstSensor = sensors[0]
            i = 1
            while i < len(sensors) - 1:
                if sensors[i]["class"] != sensors[i+1]["class"]:
                    return Response.fail("These sensors must have the same sensor class")

            lastMinutes = datetime.fromtimestamp(
                query.timestamp) - timedelta(minutes=query.minutes)

            results = self.sensorRepository.get_data_reading(
                sensorIds, int(lastMinutes.timestamp()))

            dictSensors = {}
            for r in results:
                dictSensors[r["_id"]] = r

            response = map_to_charts_sensor_response(
                charts=chartEntites, dictSensors=dictSensors, query=query)
            return Response.success(data=response, message="Get chart responses successfully")

        except ChartSensorQueryException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("ChartsId should have not empty and size >= 2")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def get(self, dashboarId: str, userId: str, chartId: str, query: ChartSensorQuery):
        try:
            query.validate()

            chartEntity = self.chartRepository.getById(chartId)
            sensorIds = [chartEntity["deviceId"]]
            lastMinutes = datetime.fromtimestamp(
                query.timestamp) - timedelta(minutes=query.minutes)
            results = self.sensorRepository.get_data_reading(
                sensorIds, int(lastMinutes.timestamp()))
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
