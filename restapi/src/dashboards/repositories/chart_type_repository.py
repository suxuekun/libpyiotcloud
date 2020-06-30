

from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.exceptions import CreatedExeception
from dashboards.models.chart_type import PIE_CHART, DONUT_CHART, LINE_CHART, BAR_CHART

class IChartTypeRepository(BaseRepository, IMongoBaseRepository):
    
    def gets_for_gateway(self):
        pass
    
    def gets_for_sensor(self):
        pass

class ChartTypeRepository(MongoBaseRepository, IChartTypeRepository):
    
    def __init__(self, mongoclient, db, collectionName):
        super().__init__(mongoclient, db, collectionName)
       
    def gets(self, query=None, projection=None):
        cursors = self.collection.find(query, projection)
        results = list(cursors)
        return results
        
    def gets_for_gateway(self):
        names = [PIE_CHART, DONUT_CHART, BAR_CHART]
        query = {
            "name": {"$in": names}
        }
        
        projection = {
            "parrentId": 0
        }
        return self.gets(query=query, projection=projection)
    
    def gets_for_sensor(self):
        names = [BAR_CHART, LINE_CHART]
        query = {
            "name": {"$in": names}
        }
        
        projection = {
            "parrentId": 0
        }
        return self.gets(query=query, projection=projection)
    
   
    