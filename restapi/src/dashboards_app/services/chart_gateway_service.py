
from dashboards_app.repositories.dashboard_repository import IDashboardRepository
from dashboards_app.repositories.chart_repository import IChartRepository
from dashboards_app.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards_app.models.dashboard import Dashboard
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards_app.models.chart import Chart
from shared.core.response import Response
from schematics.exceptions import ValidationError, ModelValidationError
from dashboards_app.utils.mapper_util import map_charts_gateway_to_response
from dashboards_app.repositories.gateway_attribute_repository import IGatewayAttributeRepository

class ChartGatewayService:
    
    def __init__(self, dashboardRepository: IDashboardRepository, 
                 chartRepository: IChartRepository,
                 attributeRepository: IGatewayAttributeRepository):
        self.dashboardRepository = dashboardRepository
        self.chartRepository = chartRepository
        self.attributeRepository = attributeRepository
        self.tag = type(self).__name__
        
    def create(self, dashboardId: str, dto: ChartGatewayDto):
        try:
            dto.validate()
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
            print(dashboardEntity)
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
        
    def gets(self, dashboardId: str):
        try:
            attributes = self.attributeRepository.gets()
            chartEntites = self.chartRepository.get_charts_gateways(dashboardId)
            responses = list(map(lambda c: map_charts_gateway_to_response(c, attributes), chartEntites))
            return Response.success(data = responses, message="Get chart responses successfully")
            
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        
    def get(self, dashboardId: str, chartId: str):
        try:
            attributes = self.attributeRepository.gets()
            chartEntity = self.chartRepository.get_detail(dashboardId, chartId)
            response = map_charts_gateway_to_response(chartEntity, attributes)
            return Response.success(data = response, message="Get chart responses successfully")
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        