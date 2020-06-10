

from dashboards_app.repositories.chart_type_repository import IChartTypeRepository
from shared.core.response import Response
from shared.core.exceptions import CreatedExeception, UpdatedException, QueriedByIdException, QueriedManyException, DeletedException
from shared.services.logger_service import LoggerService
from dashboards_app.models.chart_type import ChartType, PIE_CHART, DONUT_CHART, LINE_CHART, BAR_CHART
import json

class ChartTypeService:

    def __init__(self, chartTypeRepo: IChartTypeRepository):
        self.chartTypeRepo = chartTypeRepo
        self.tag = type(self).__name__

    def setup_chart_types(self):
       try:
            isExisted = self.chartTypeRepo.check_collection_existed()
            if isExisted:
                return False
            
            # Create charts types
            inputs = [
                ChartType.create(id = 0, name= PIE_CHART).model.to_primitive(),
                ChartType.create(id = 1, name=DONUT_CHART).model.to_primitive(),
                ChartType.create(id = 2, name=BAR_CHART).model.to_primitive(),
                ChartType.create(id = 3, name =LINE_CHART).model.to_primitive()
            ]
            self.chartTypeRepo.create_many(inputs)
            return True
       except Exception as e:
           LoggerService().error(str(e), tag=self.tag)
           return False

    def gets_for_sensor(self):
        try:
            response = self.chartTypeRepo.gets_for_sensor()
            return Response.success(data=response, message="Get chart types for sensor")
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")

    def gets_for_gateway(self):
        try:
            response = self.chartTypeRepo.gets_for_gateway()
            return Response.success(data=response, message="Get chart types for gateway")
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")
        
    
