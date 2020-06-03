
from pymongo import MongoClient  # MongoDB
from dashboards_app.app import DashboardsApp


class BootstrapApplicationService:
    __instance = None
    __mongoClient = None
    __app = None
    
    @staticmethod
    def get_instance():
        if BootstrapApplicationService.__instance == None:
            BootstrapApplicationService()
        return BootstrapApplicationService.__instance

    def __init__(self):
        if BootstrapApplicationService.__instance == None:
            CachedMongoClientService.__instance = self

    def set_mongo_client(self, mongoClient):
        self.__mongoClient = mongoClient

    def get_mongo_client(self):
        return self.__mongoClient

    def set_app_flask(self, app):
        self.__app = app

    def bootstap(self):

        # Init dashboards app
        dashboardsApp = DashboardsApp()
        dashboardsApp.build(__app)
   





    