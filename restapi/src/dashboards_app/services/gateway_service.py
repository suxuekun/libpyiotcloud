


from dashboards_app.models.dashboard import Dashboard
from shared.core.response import Response
from shared.services.logger_service import LoggerService
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from schematics.exceptions import ValidationError, ModelValidationError
from dashboards_app.repositories.dashboard_repository import IDashboardRepository
from dashboards_app.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards_app.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from dashboards_app.models.dashboard import ChartModel
from dashboards_app.models.gateway_attribute import GatewayAttributeModel
from dashboards_app.utils.mapper_util import map_charts_gateway_to_response

class GatewayService:
    def __init__(self, dashboardRepository: IDashboardRepository, gatewayRepository: IGatewayAttributeRepository):
        self.dashboardRepository = dashboardRepository
        self.gatewayRepository = gatewayRepository
        self.tag = type(self).__name__
    
    def add(self, dashboardId: str, dto: ChartGatewayDto):
        try:
            dto.validate()
            entity = self.dashboardRepository.getById(dashboardId)
            dashoard = Dashboard.to_domain(entity)
            dashoard.add_chart_gateway(dto)
            self.dashboardRepository.update(dashboardId, dashoard.model.to_primitive())
            return Response.success(data=True, message="Add new dashboard successfully")
        
        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except UpdatedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, Add gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        
    def delete(self, dashboardId: str, chartId: str):
        try:
            entity = self.dashboardRepository.getById(dashboardId)
            dashoard = Dashboard.to_domain(entity)
            dashoard.remove_chart_gateway(chartId)
            self.dashboardRepository.update(dashboardId, dashoard.model.to_primitive())
            return Response.success(data=True, message="Delete chart gateway successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete chart gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")  
    

    def gets(self, dashboardId: str, query = None):
        try:
            print(dashboardId)
            chartGateways = self.dashboardRepository.get_charts_gateways(dashboardId=dashboardId)
            print(chartGateways)
            attributes = self.gatewayRepository.gets()
            responses = list(map(lambda c: map_charts_gateway_to_response(c, attributes), chartGateways))
            return Response.success(data = responses, message="Get chart responses successfully")
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")  
    

    
        
      

        