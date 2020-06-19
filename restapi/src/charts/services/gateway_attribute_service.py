
from charts.repositories.gateway_attribute_repository import IGatewayAttributeRepository
from charts.models.gateway_attribute import FactoryGatewayAttribute, STORAGE_USAGE, COUNT_OF_ALERTS, ON_OFF_LINE, BAND_WIDTH
from shared.services.logger_service import LoggerService
from shared.core.response import Response
from  shared.utils.mapper_util import formart_id_with_entitites

class GatewayAttributeService:
    
    def __init__(self, gatewayAttributeRepo: IGatewayAttributeRepository):
        super().__init__()
        self.gatewayAttributeRepo = gatewayAttributeRepo
        self.tag = type(self).__name__
        
    def setup_attributes(self):
        try:
            isExisted = self.gatewayAttributeRepo.check_collection_existed()
            if isExisted:
                return False
            
            inputs = [
                FactoryGatewayAttribute.create(STORAGE_USAGE).to_primitive(),
                FactoryGatewayAttribute.create(COUNT_OF_ALERTS).to_primitive(),
                FactoryGatewayAttribute.create(ON_OFF_LINE).to_primitive(),
                FactoryGatewayAttribute.create(BAND_WIDTH).to_primitive()
            ]
            self.gatewayAttributeRepo.create_many(inputs)
            return True
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return False
        
    def gets(self):
        try:
            attributes = self.gatewayAttributeRepo.gets_summary()
            formart_id_with_entitites(attributes)
            return Response.success(data=attributes, message="Get attributes successully")
        except Exception as e:
            LoggerService().error(str(e), tag=self.tag)
            return Response.fail("Sorry, there is something wrong")