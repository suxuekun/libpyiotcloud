
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

class ChartGatewayService:
    
    def __init__(self, dashboardRepository: IDashboardRepository, 
                 chartRepository: IChartRepository,
                 attributeRepository: IGatewayAttributeRepository,
                 deviceRepository: IDeviceRepostory):
        
        self.deviceRepository = deviceRepository
        self.dashboardRepository = dashboardRepository
        self.chartRepository = chartRepository
        self.attributeRepository = attributeRepository
        self.tag = type(self).__name__
        
    def create_for_gateway(self, dashboardId: str, dto: ChartGatewayDto):
        try:
            # Validate step
            dto.validate()
            gatewayDevice = self.deviceRepository.get_by_uuid(dto.gatewayId)
            
            if gatewayDevice is None:
                return Response.fail("This device was not existed")
            
            dashboardEntity = self.dashboardRepository.getById(dashboardId)
            dashoard = Dashboard.to_domain(dashboardEntity)
            
            # Create chart
            chart = Chart.create_for_gateway(dashboardId=dashoard.model._id, userId=dashoard.model.userId, dto=dto)
            chartId = self.chartRepository.create(chart.model.to_primitive())
            
            # Update dashboard
            dashoard.add_chart_gateway(chartId)
            self.dashboardRepository.update(dashboardId, dashoard.model.to_primitive())
            
            return Response.success(True, "Create chart gateway successfully")
        
        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except CreatedExeception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, Create chart gatway faield")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
    
    def delete(self, dashboardId:str, chartId: str):
        try:
            dashboardEntity = self.dashboardRepository.getById(dashboardId)
            dashoard = Dashboard.to_domain(dashboardEntity)
            
            dashoard.remove_chart_gateway(chartId)
            
            self.dashboardRepository.update(dashboardId, dashoard.model.to_primitive())
            self.chartRepository.delete(chartId)
            
            return Response.success(data=True, message="Delete chart gateway successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete chart gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        
    def gets(self, dashboardId: str, userId: str, query: {}):
        try:
            attributes = self.attributeRepository.gets()
            chartEntites = self.chartRepository.get_charts_gateways(dashboardId, userId)
            
            responses = list(map(lambda c: map_chart_gateway_to_response(c, attributes), chartEntites))
            return Response.success(data = responses, message="Get chart responses successfully")
            
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        
    def get(self, dashboardId: str, chartId: str, query: {}):
        try:
            attributes = self.attributeRepository.gets()
            chartEntity = self.chartRepository.get_detail(dashboardId, chartId, query)
            
            response = map_chart_gateway_to_response(chartEntity, attributes)
            return Response.success(data = response, message="Get chart responses successfully")
        
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        