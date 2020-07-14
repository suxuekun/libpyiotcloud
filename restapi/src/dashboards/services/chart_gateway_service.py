
from dashboards.repositories.dashboard_repository import IDashboardRepository
from dashboards.repositories.chart_gateway_repository import IChartGatewayRepository
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards.models.dashboard import Dashboard
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards.models.chart import ChartGateway
from shared.core.response import Response
from schematics.exceptions import ValidationError, ModelValidationError
from dashboards.utils.mapper_chart_gateway_response import map_chart_gateway_to_response, map_chart_gateway_to_ex_response
from dashboards.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from dashboards.repositories.device_repository import IDeviceRepostory
from dashboards.services.dashboard_service import DashboardService
from dashboards.dtos.chart_gateway_query import ChartGatewayQuery


class ChartGatewayService:

    def __init__(self, dashboardRepository: IDashboardRepository,
                 chartRepository: IChartGatewayRepository,
                 attributeRepository: IGatewayAttributeRepository,
                 deviceRepository: IDeviceRepostory,
                 dashboardService: DashboardService):

        self.deviceRepository = deviceRepository
        self.dashboardRepository = dashboardRepository
        self.chartRepository = chartRepository
        self.attributeRepository = attributeRepository
        self.dashboardService = dashboardService
        self.tag = type(self).__name__

    def create(self, dashboardId: str, userId: str, dto: ChartGatewayDto):
        try:
            # Validate request
            dto.validate()
            gatewayDevice = self.deviceRepository.get_by_uuid(dto.deviceId)

            if gatewayDevice is None:
                return Response.fail("This device was not existed")

            #  Validate same chart
            sameChart = self.chartRepository.get_same_chart(
                dashboardId, dto.deviceId, dto.attributeId, dto.chartTypeId)
            if sameChart is not None:
                return Response.fail("Sorry, This chart should not have same device, same attribute and same type")

            # Create chart
            chart = ChartGateway.create(
                dashboardId=dashboardId, userId=userId, dto=dto)
            chartId = self.chartRepository.create(chart.model.to_primitive())

            # Update dashboard
            self.dashboardService.add_chart_gateway(dashboardId, chartId)

            return Response.success_without_data("Create chart gateway successfully")

        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except CreatedExeception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, Create chart gatway faield")

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
            self.dashboardService.remove_many_charts_gateways_in_many_dashboards(
                chartsWithDashboards)
            return True

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

    def delete(self, dashboardId: str, chartId: str):
        try:
            self.chartRepository.delete(chartId)
            # Notify to dashboard update
            self.dashboardService.remove_chart_gateway(dashboardId, chartId)
            return Response.success_without_data(message="Delete chart gateway successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete chart gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets(self, dashboardId: str, userId: str, query: ChartGatewayQuery):
        try:
            attributes = self.attributeRepository.gets()
            chartEntites = self.chartRepository.get_charts(dashboardId, userId)

            responses = list(map(lambda c: map_chart_gateway_to_response(
                c, attributes, query), chartEntites))
            return Response.success(data=responses, message="Get chart responses successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets_ex(self, dashboardId: str, userId: str, query: ChartGatewayQuery):
        try:
            attributes = self.attributeRepository.gets()
            chartEntites = self.chartRepository.get_charts(dashboardId, userId)

            responses = list(map(lambda c: map_chart_gateway_to_ex_response(
                c, attributes, query), chartEntites))
            return Response.success(data=responses, message="Get chart responses successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def get(self, dashboardId: str, userId: str, chartId: str, query: ChartGatewayQuery):
        try:
            attributes = self.attributeRepository.gets()
            chartEntity = self.chartRepository.get_detail(
                dashboardId, userId, chartId)

            response = map_chart_gateway_to_response(
                chartEntity, attributes, query)
            return Response.success(data=response, message="Get chart responses successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def get_ex_detail(self, dashboardId: str, userId: str, chartId: str, query: ChartGatewayQuery):
        try:
            attributes = self.attributeRepository.gets()
            chartEntity = self.chartRepository.get_detail(
                dashboardId, userId, chartId)

            response = map_chart_gateway_to_ex_response(
                chartEntity, attributes, query)
            return Response.success(data=response, message="Get chart responses successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
