
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


class ChartSensorService:

      def __init__(self, dashboardRepository: IDashboardRepository,
                 chartRepository: IChartRepository,
                 attributeRepository: IGatewayAttributeRepository,
                 deviceRepository: IDeviceRepostory,
                 sensorRepository: ISensorRepository):

            self.deviceRepository = deviceRepository
            self.dashboardRepository = dashboardRepository
            self.chartRepository = chartRepository
            self.attributeRepository = attributeRepository
            self.sensorRepository = sensorRepository
            self.tag = type(self).__name__

      def get_sensor_data_reading(self, id: str):
            try:
                  # Default time is last 5 mins

                  lastFiveMinutes = datetime.now() - timedelta(minutes=5)
                  results=self.sensorRepository.get_data_reading(id, int(lastFiveMinutes.timestamp()))
                  return Response.success(data=results, message="Get data successfully")
            except Exception as e:
                  LoggerService().error(str(e), tag=self.tag)
                  return Response.fail("Sorry, there is something wrong")

      def create(self, dashboardId: str, dto: ChartSensorDto):
            try:
                  dto.validate()
                  dashboardEntity=self.dashboardRepository.getById(dashboardId)
                  dashoard=Dashboard.to_domain(dashboardEntity)

                  # Create chart
                  chart=Chart.create_for_sensor(
                      dashboardId=dashoard.model._id, userId=dashoard.model.userId, dto=dto)
                  chartId=self.chartRepository.create(
                      chart.model.to_primitive())

                  # Update dashboard
                  dashoard.add_chart_gateway(chartId)
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

      def gets(self, dashboardId: str, userId: str, query: {}=None):
            try:
                  return Response.success(data=[], message="Get chart responses successfully")

            except Exception as e:
                  LoggerService().error(str(e), tag=self.tag)
                  return Response.fail("Sorry, there is something wrong")

      def get(self, dashboarId: str, userId: str, chartId: str, query: {}=None):
            try:
                  return Response.success(data={}, message="Get chart responses successfully")
            except Exception as e:
                  LoggerService().error(str(e), tag=self.tag)
                  return Response.fail("Sorry, there is something wrong")
