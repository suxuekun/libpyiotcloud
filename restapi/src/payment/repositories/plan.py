from shared.core.repository.base_s3 import S3Repository
from shared.core.repository.braintree_readonly import PaymentRepository
from shared.utils import dict_util


class PlanRepository(PaymentRepository):
    ID = "_id"
    def __init__(self,*args,**kwargs):
        super(PlanRepository,self).__init__(*args,**kwargs)
        self.reload()

    def reload(self):
        try:
            self.raw = self.payment_client.plans
            self._handler(self.raw)
            return self.gets()
        except Exception as e:
            print(e)
            return False

    def _make_plan(self,raw_plan):
        desc = raw_plan.description
        l = desc.split('\n')
        usage_limit = dict_util.pair_to_dict(l)
        res = {
            '_id':raw_plan.id,
            'bt_plan_id':raw_plan.id,
            'name':raw_plan.name,
            'price':raw_plan.price,
        }
        res.update(usage_limit)
        return res
    def _handler(self,raw):
        self.collection = list(map(self._make_plan,raw))
        self.collection.sort(key=lambda x: x.get('price'))
        self._make_index()

    @property
    def free(self):
        return self.getById('Free')

