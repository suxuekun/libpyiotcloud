from payment.models.plan import Plan
from shared.services.logger_service import LoggerService
from shared.simple_api.service import BaseSimpleApiService, BaseMongoService


class PlanService(BaseMongoService):
    def __init__(self,*args,**kwargs):
        super(PlanService,self).__init__(*args,**kwargs)
        self.create_dummy()

    def get_free_plan(self):
        return self._free
    def create_dummy(self):
        querys = [
            {
                'bt_plan_id': '',
                'name': 'Free Plan',

            },
            {
                'bt_plan_id': 'Basic10',
                'name': 'Plan B',

            },
            {
                'bt_plan_id': '',
                'name': 'Plan C',

            },
            {
                'bt_plan_id': '',
                'name': 'Plan D',

            },
        ]
        dummy = [
            {
                'bt_plan_id': '',
                'name': 'Free Plan',
                'price': "0",
                'period': 0,
                'currency': '',
                'sms': '0',
                'email': 30,
                'notification': 100,
                'storage': 50,
            },
            {
                'bt_plan_id': 'Basic10',
                'name': 'Plan B',
                'price': "10",
                'period': 1,
                'currency': 'USD',
                'sms': '5',
                'email': 100,
                'notification': 1000,
                'storage':1000,
            },
            {
                'bt_plan_id': '',
                'name': 'Plan C',
                'price': "30",
                'period': 1,
                'currency': 'USD',
                'sms': '20',
                'email': 1000,
                'notification': 100000,
                'storage': 3000,
            },
            {
                'bt_plan_id': '',
                'name': 'Plan D',
                'price': "50",
                'period': 1,
                'currency': 'USD',
                'sms': '30',
                'email': 10000,
                'notification': 1000000,
                'storage': 10000,
            },

        ]
        # plans = [Plan(x) for x in dummy]
        entities = [self.get_or_create_one(x) for x in dummy]
        self._free = entities[0]


    pass
    # def __init__(self,*args,**kwargs):
    #     super(PlanService,self).__init__(*args,**kwargs)
    #     self.tag = type(self).__name__
    # def list(self,list_filter = None):
    #     # result = self.repo.gets(list_filter)
    #     # data = [self.model(i).to_primitive() for i in result]
    #     return []
    #
    # def get(self, id):
    #     # try:
    #     #     result = self.repo.getById(id)
    #     #     data = self.model(result)
    #     #     data.validate()
    #     #     return data.to_primitive()
    #     # except Exception as _:
    #     #     LoggerService().error(str(_), tag=self.tag)
    #     return None
    #
    # def create(self, entity):
    #     pass
    #
    # def update(self, id,entity):
    #     pass
    #
    # def delete(self, id):
    #     pass


