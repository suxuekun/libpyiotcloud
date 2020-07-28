
from dashboards.repositories.dashboard_repository import IDashboardRepository
from dashboards.repositories.chart_gateway_repository import IChartGatewayRepository
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards.models.dashboard import Dashboard
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards.models.chart import ChartGateway
from shared.core.response import Response
from schematics.exceptions import ValidationError, ModelValidationError
from dashboards.utils.mapper_chart_gateway_response import *
from dashboards.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from dashboards.repositories.device_repository import IDeviceRepostory
from dashboards.services.dashboard_service import DashboardService
from dashboards.dtos.chart_gateway_query import ChartGatewayQuery
from dashboards.repositories.heart_beat_repository import IHeartBeatRepository
from dashboards.repositories.storage_usage_repository import IStorageUsageRepositoy
from dashboards.repositories.menos_alert_repository import IMenosAlertRepository
from dashboards.repositories.chart_type_repository import IChartTypeRepository
from dashboards.models.gateway_attribute import *
import time

class ChartGatewayService:

    def __init__(self, dashboardRepository: IDashboardRepository,
                 chartRepository: IChartGatewayRepository,
                 attributeRepository: IGatewayAttributeRepository,
                 deviceRepository: IDeviceRepostory,
                 heartBeatRepository: IHeartBeatRepository,
                 menosAlertRepository: IMenosAlertRepository,
                 storageUsageRepository: IStorageUsageRepositoy,
                 chartTypeRepository: IChartTypeRepository,
                 dashboardService: DashboardService):

        self.deviceRepository = deviceRepository
        self.dashboardRepository = dashboardRepository
        self.chartRepository = chartRepository
        self.attributeRepository = attributeRepository
        self.dashboardService = dashboardService
        self.heartBeatRepository = heartBeatRepository
        self.storageUsageRepository = storageUsageRepository
        self.menosAlertRepository = menosAlertRepository
        self.chartTypeRepository = chartTypeRepository
        self.tag = type(self).__name__

    def create(self, dashboardId: str, userId: str, dto: ChartGatewayDto):
        try:
            # Validate request
            dto.validate()

            # Validate chartType
            chartType = self.chartTypeRepository.get_by_id(dto.chartTypeId)
            if chartType is None:
                LoggerService().error("This chartType was not existed", tag=self.tag)
                return Response.fail("This chartType was not existed")

            # Validate attribute
            attribute = self.attributeRepository.get_by_id(dto.attributeId)
            if attribute is None:
                LoggerService().error("This attribute was not existed", tag=self.tag)
                return Response.fail("This attribute was not existed")

            # Validate gateway device
            gatewayDevice = self.deviceRepository.get_by_uuid(dto.deviceId)
            if gatewayDevice is None:
                LoggerService().error("This device was not existed", tag=self.tag)
                return Response.fail("This device was not existed")

            #  Validate same chart
            sameChart = self.chartRepository.get_same_chart(
                dashboardId, dto.deviceId, dto.attributeId, dto.chartTypeId)
            if sameChart is not None:
                LoggerService().error("Sorry, This chart should not have same device, same attribute and same type", tag=self.tag)
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

    def _check_deviceId_in_list(self, deviceId: str, deviceIds: []):
        for item in deviceIds:
            if item == deviceId:
                return True

        return False

    def _gets_reports_by_attribute(self, attributeId: int, gatewaysUUID: []):
        if attributeId == ON_OFF_LINE_ID:
            timestamp = int(time.time())
            print(timestamp)
            reports = self.heartBeatRepository.gets_by_gatewaysId(
                gatewaysUUID, timestamp)
            return reports

        if attributeId == COUNT_OF_ALERTS_ID:
            reports = self.menosAlertRepository.gets_by_gatewaysId(
                gatewaysUUID)
            return reports

        if attributeId == STORAGE_USAGE_ID:
            reports = self.storageUsageRepository.gets_by_gatewaysId(
                gatewaysUUID)
            return reports

        return []

    def gets(self, dashboardId: str, userId: str, query: ChartGatewayQuery):
        try:
            attributes = self.attributeRepository.gets()
            chartEntites = self.chartRepository.get_charts(dashboardId, userId)

            # Group gateways by attribute => List gateways with attribute
            dictGateways = {}
            for chart in chartEntites:
                if chart["attributeId"] in dictGateways:
                    if self._check_deviceId_in_list(chart["deviceId"], dictGateways[chart["attributeId"]]) is False:
                        dictGateways[chart["attributeId"]].append(
                            chart["deviceId"])
                else:
                    dictGateways[chart["attributeId"]] = []
                    dictGateways[chart["attributeId"]].append(
                        chart["deviceId"])

            # Get data from attribute
            dictReports = {}
            for keyAttributeId in dictGateways:
                gatewaysUUID = dictGateways[keyAttributeId]

                report = self._gets_reports_by_attribute(
                    keyAttributeId, gatewaysUUID)

                dictReports[keyAttributeId] = report

            # Map data to every charts
            responses = list(map(lambda c: map_to_chart_gateway_to_response(
                c, dictReports, attributes, query), chartEntites))

            return Response.success(data=responses, message="Get chart responses successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def get(self, dashboardId: str, userId: str, chartId: str, query: ChartGatewayQuery):
        try:
            attributes = self.attributeRepository.gets()
            chartEntity = self.chartRepository.get_detail(
                dashboardId, userId, chartId)

            report = self._gets_reports_by_attribute(
                chartEntity["attributeId"], [chartEntity["deviceId"]])

            dictReports = {
                chartEntity["attributeId"]: report
            }

            response = map_to_chart_gateway_to_response(
                chartEntity, dictReports, attributes, query)

            return Response.success(data=response, message="Get chart responses successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
