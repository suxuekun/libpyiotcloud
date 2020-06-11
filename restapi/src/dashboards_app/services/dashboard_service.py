

from dashboards_app.repositories.dashboard_repository import IDashboardRepository
from dashboards_app.dtos.dashboard_dto import DashboardDto
from dashboards_app.models.dashboard import Dashboard, DashboardModel
from shared.core.response import Response
from dashboards_app.dtos.dashboard_dto import DashboardDto
from schematics.exceptions import ValidationError, ModelValidationError
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards_app.utils.mapper_util import map_entities_to_summaries_response
from dashboards_app.dtos.chart_gateway_dto import ChartGatewayDto

class DashboardService:
    def __init__(self, dashboardRepository: IDashboardRepository):
        self.dashboardRepository = dashboardRepository
        self.tag = type(self).__name__

    def create(self, userId: str, dto: DashboardDto):
        try:
            dto.validate()
            dashboard = Dashboard.create(userId, dto)
            result = self.dashboardRepository.create(
                dashboard.model.to_primitive())
            return Response.success(True, "Create dashboard successfully")

        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except CreatedExeception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, Create dashboard wrong")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def updateNameAndOption(self, id: str, dto: DashboardDto):

        try:
            dto.validate()
            entity = self.dashboardRepository.getById(id)
            dashboard = Dashboard.to_domain(entity)
            dashboard.update_name_and_option(dto)
            self.dashboardRepository.update(id, dashboard.model.to_primitive())
            return Response.success(True, "Update dashboard successfully")

        except ModelValidationError as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail(str(e))

        except UpdatedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, Updated dashboard failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def get(self, id: str):

        try:
            entity = self.dashboardRepository.getById(id)
            entity["id"] = entity["_id"]
            entity.pop("_id")
            return Response.success(data=entity, message="Get dashboard detail successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets(self, userId: str):
        try:
            query = {
                "userId": userId
            }
            entities = self.dashboardRepository.get_summaried_dashboards(query = query)
            responses = map_entities_to_summaries_response(entities)
            return Response.success(data=responses, message="Get dashboards successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def delete(self, id):
        try:
            self.dashboardRepository.delete(id)
            return Response.success(data=True, message="Delete dashboards successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete dashboard failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        
    def addNewChartGateway(self, dashboardId: str, dto: ChartGatewayDto):
        try:
            dto.validate()
            entity = self.dashboardRepository.getById(dashboardId)
            dashoard = Dashboard.to_domain(entity)
            dashoard.add_chart_gateway(dto)
            self.dashboardRepository.update(dashboardId, dashoard.model.gateways.to_primitive())
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
        
    def deleteChartGateway(self, dashboardId: str, chartId: str):
        try:
            entity = self.dashboardRepository.getById(dashboardId)
            dashoard = Dashboard.to_domain(entity)
            dashoard.remove_chart_gateway(chartId)
            self.dashboardRepository.update(dashboardId, dashoard.model.gateways.to_primitive())
            return Response.success(data=True, message="Delete dashboards successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete chart gateway failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")    