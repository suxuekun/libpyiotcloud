
from dashboards_app.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from dashboards_app.models.gateway_attribute import FactoryGatewayAttribute, STORAGE_USAGE, COUNT_OF_ALERTS, ON_OFF_LINE
from shared.services.logger_service import LoggerService
from shared.core.response import Response

class GatewayAttributeService:
    
    def __init__(self, gatewayAttributeRepo: IGatewayAttributeRepository):
        super().__init__()
        self.gatewayAttributeRepo = gatewayAttributeRepo
        self.tag = type(self).__name__
        
    def setup_attributes(self):
        try:
            isExisted = self.gatewayAttributeRepo.check_collection_existed()
            if isExisted:
                print("Check new")
                return False
            
            inputs = [
                FactoryGatewayAttribute.create(STORAGE_USAGE).to_primitive(),
                FactoryGatewayAttribute.create(COUNT_OF_ALERTS).to_primitive(),
                FactoryGatewayAttribute.create(ON_OFF_LINE).to_primitive()
            ]
            self.gatewayAttributeRepo.create_many(inputs)
            return True
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False
        
    def gets(self):
        try:
            results = self.gatewayAttributeRepo.gets_summary()
            return Response.success(data=results, message="Get attributes successully")
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")