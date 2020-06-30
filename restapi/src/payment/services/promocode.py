from bson import ObjectId

from payment.models.plan import Plan
from shared.services.logger_service import LoggerService
from shared.simple_api.service import BaseSimpleApiService, BaseMongoService, BaseS3Service

class AbstractPromocodeService(BaseSimpleApiService):
    def __init__(self,usecount_service,*args,**kwargs):
        super(AbstractPromocodeService,self).__init__(*args,**kwargs)
        self.usecount_service = usecount_service

    def verify(self,code,subscription_id,plan_id,create_time):
        model_instance = self.get(code)
        verify = self._verify(model_instance,subscription_id,plan_id,create_time)
        if verify:
            return model_instance
        return None

    def _verify(self,model_instance,subscription_id,plan_id,create_time):
        if not model_instance:
            return False
        if not model_instance.allow_plan(plan_id):
            return False
        '''
        currently no checking for new user
        '''
        if not model_instance.within_validity(create_time):
            return False
        query = {
            'promocode':model_instance._id,
            'subscription_id':subscription_id,
        }
        record = self.usecount_service.get_or_create_one(query)
        if (record.get_count() >= model_instance.max_usage):
            return False
        return True

    def add_promocode_usage(self,subscription_id,promocode):
        self.usecount_service.add_usage(subscription_id,promocode)

    def list_valid_code(self,subscription_id,plan_id,create_time):
        l = self.list()
        filtered_list = list(filter(lambda x:x and self._verify(x,subscription_id,plan_id,create_time),l))
        return filtered_list


class PromocodeS3Service(BaseS3Service,AbstractPromocodeService):
    pass


class PromocodeService(BaseMongoService,PromocodeS3Service):
    pass



