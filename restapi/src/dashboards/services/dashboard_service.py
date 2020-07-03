

from dashboards.repositories.dashboard_repository import IDashboardRepository
from dashboards.models.dashboard import Dashboard, DashboardModel
from shared.core.response import Response
from dashboards.dtos.dashboard_dto import DashboardDto
from schematics.exceptions import ValidationError, ModelValidationError
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards.utils.mapper_util import map_entities_to_summaries_response, map_entity_to_summary_response


class RemovingChartParam:
    chartId: str
    dashboardId: str


class DashboardService:
    def __init__(self, dashboardRepository: IDashboardRepository):
        self.dashboardRepository = dashboardRepository
        self.tag = type(self).__name__

    def create(self, userId: str, dto: DashboardDto):
        try:
            dto.validate()
            dashboard = Dashboard.create(userId, dto)
            self.dashboardRepository.create(dashboard.model.to_primitive())
            return Response.success_without_data("Create dashboard successfully")

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
            return Response.success_without_data("Update dashboard successfully")

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
            response = map_entity_to_summary_response(entity)
            return Response.success(data=response, message="Get dashboard detail successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets(self, userId: str):
        try:
            query = {
                "userId": userId
            }
            entities = self.dashboardRepository.get_summaried_dashboards(
                query=query)
            responses = map_entities_to_summaries_response(entities)
            return Response.success(data=responses, message="Get dashboards successfully")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def delete(self, id):
        try:
            self.dashboardRepository.delete(id)
            return Response.success_without_data(message="Delete dashboards successfully")

        except DeletedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, delete dashboard failed")

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def remove_chart_gateway(self, dashboardId: str, chartId: str):
        try:
            entity = self.dashboardRepository.getById(dashboardId)
            dashboard = Dashboard.to_domain(entity)
            dashboard.remove_chart_gateway(chartId)

            self.dashboardRepository.update(
                dashboardId, dashboard.model.to_primitive())
            return True

        except UpdatedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

    def remove_chart_sensor(self, dashboardId: str, chartId: str):
        try:
            entity = self.dashboardRepository.getById(dashboardId)
            dashboard = Dashboard.to_domain(entity)
            dashboard.remove_chart_sensor(chartId)

            self.dashboardRepository.update(
                dashboardId, dashboard.model.to_primitive())
            return True

        except UpdatedException as e:
            LoggerService().error(str(e), tag=self.tag)
            return False

        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False
        
    #  Param chartWithDashboard
    def remove_many_charts_in_many_dashboards(self, chartWithDashboard: {}):
        try:
            dashboardIds = list(map(lambda chart: chart, chartWithDashboard))
            entities = self.dashboardRepository.gets_with_ids(dashboardIds)

            dashboards = list(map(lambda e: Dashboard.to_domain(e), entities))
            for dashboard in dashboards:
                dashboard.remove_chart_gateway(
                    chartWithDashboard.get(dashboard._id))

            self.dashboardRepository.update_many(dashboardIds, list(
                map(lambda d: d.model.to_primitive, dashboards)))
            return True
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False
