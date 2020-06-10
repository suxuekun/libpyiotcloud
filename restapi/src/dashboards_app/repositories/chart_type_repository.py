

from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository
from shared.core.exceptions import CreatedExeception
from dashboards_app.models.chart_type import PIE_CHART, DONUT_CHART, LINE_CHART, BAR_CHART

class IChartTypeRepository(BaseRepository):
    def check_collection_existed(self) -> bool:
        pass
    
    def create_many(self, inputs):
        pass
    
    def gets_for_gateway(self):
        pass
    
    def gets_for_sensor(self):
        pass
    

class ChartTypeRepository(MongoBaseRepository, IChartTypeRepository):
    
    def __init__(self, mongoclient, db, collectionName:str):
        super().__init__(mongoclient=mongoclient, db=db, collectionName=collectionName)
        
    def check_collection_existed(self):
        return self.collectionName in self.db.list_collection_names()
    
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
    
   
    