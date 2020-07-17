from payment.core import payment_client
from payment.models.plan import Plan
from shared.services.logger_service import LoggerService
from shared.simple_api.service import BaseSimpleApiService, BaseMongoService, BaseS3Service, BaseFileService


class PlanService(BaseFileService):
    # def __init__(self,*args,**kwargs):
    #     super(PlanService,self).__init__(*args,**kwargs)
    #     # # self.create_dummy()
    #     # plans = payment_client.plans
    #     # print("--plans-- ",[plan.id for plan in plans])

    def get_free_plan(self):
        return self.model(self.repo.free,strict=False)

    def reload(self):
        return self.repo.reload()



