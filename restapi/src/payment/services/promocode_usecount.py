from shared.simple_api.service import BaseMongoService


class PromocodeUseCountService(BaseMongoService):

    def add_usage(self,subscription_id,promocode):
        query={
            'subscription_id':subscription_id,
            'promocode':promocode
        }
        res = self.repo.update_one(query, {'$inc': {'count': 1}},upsert=True)
        return res
    pass