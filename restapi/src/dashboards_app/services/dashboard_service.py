

from dashboards_app.repositories.dashboard_repository import IDashboardRepository
from dashboards_app.dtos.dashboard_dto import DashboardDto
from dashboards_app.models.dashboard import Dashboard, DashboardModel
from shared.core.response import Response
from dashboards_app.dtos.dashboard_dto import DashboardDto
from schematics.exceptions import ValidationError, ModelValidationError
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException
from shared.services.logger_service import LoggerService
from dashboards_app.utils.mapper_util import map_entities_to_summaries_response
class DashboardService:
    def __init__(self, dashboardRepository: IDashboardRepository):
        self.dashboardRepository = dashboardRepository

    def create(self, dto: DashboardDto):
        try:
            dto.validate()
            dashboard = Dashboard.create(dto)
            result = self.dashboardRepository.create(
                dashboard.model.to_primitive())
            return Response.success(True, "Create dashboard successfully")

        except ModelValidationError as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail(str(e))
        
        except CreatedExeception as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, Create dashboard wrong")
        
        except Exception as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, there is something wrong")

    def updateNameAndOption(self, id: str, dto: DashboardDto):

        try:
            print("Update ne ")
            entity = self.dashboardRepository.getById(id)
            print(entity)
            dashboard = Dashboard.toDomain(entity)
            print("Domain ne ")
            print(dashboard.model.to_primitive())
            dashboard.updateNameAndOption(dto)
            self.dashboardRepository.update(id, dashboard.model.to_primitive())
            return Response.success(True, "Update dashboard successfully")
        
        except ModelValidationError as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail(str(e))
        
        except UpdatedException as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, Updated dashboard failed")
        
        except Exception as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, there is something wrong")
            
    def getDashboardDetail(self, id: str):
        
        try:
            entity = self.dashboardRepository.getById(id)
            entity["id"] = entity["_id"]
            entity.pop("_id")
            return Response.success(data=entity, message="Get dashboard detail successfully")
        
        except QueriedByIdException as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, get dashboard detail wrong") 
            
        except Exception as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, there is something wrong")
        
    def getDashboards(self, query={}):
        
        try:
            entities = self.dashboardRepository.get_summaried_dashboards()
            responses = map_entities_to_summaries_response(entities)
            return Response.success(data=responses, message="Get dashboards successfully")
        
        except QueriedManyException as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, there is something wrong") 
        
        except Exception as e:
            LoggerService.get_instance().error(str(e))
            return Response.fail("Sorry, there is something wrong")