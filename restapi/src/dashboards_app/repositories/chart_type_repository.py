

from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.exceptions import CreatedExeception
from dashboards_app.models.chart_type import PIE_CHART, DONUT_CHART, LINE_CHART, BAR_CHART

class IChartTypeRepository(BaseRepository):
    
    
    def create_many(self, inputs):
        pass
    
    def gets_for_gateway(self):
        pass
    
    def gets_for_sensor(self):
        pass
    

class ChartTypeRepository(MongoBaseRepository, IChartTypeRepository):
    
    def __init__(self, mongoclient, db, collectionName):
        super().__init__(mongoclient, db, collectionName)
        
    def create_many(self, inputs):
        try:
            result = self.collection.insert_many(inputs)
            return True
        except Exception as e:
            print(e)
            raise CreatedExeception(str(e))
    
    def gets_for_gateway(self):
        names = [PIE_CHART, DONUT_CHART]
        query = {
            "name": {"$in": names}
        }
        return super().gets(query=query)
    
    def gets_for_sensor(self):
        names = [BAR_CHART, LINE_CHART]
        query = {
            "name": {"$in": names}
        }
        return super().gets(query=query)
    
   
    