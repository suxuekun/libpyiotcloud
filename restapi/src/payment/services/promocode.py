from bson import ObjectId

from payment.models.plan import Plan
from payment.models.promocode import Promo
from shared.services.logger_service import LoggerService
from shared.simple_api.service import BaseSimpleApiService, BaseMongoService


class PromocodeService(BaseMongoService):
    def __init__(self,*args,**kwargs):
        super(PromocodeService,self).__init__(*args,**kwargs)
        self.create_dummy()
    def create_dummy(self):
        entityname = 'su-org.1592316898'
        promo_dummy = [
            {
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": '10 discount',
                "type": 'percent_discount',
                "period": 1,
                "value": "10"
            },{
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": '20 discount',
                "type": 'percent_discount',
                "period": 1,
                "value": "20"
            },{
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": '50 discount',
                "type": 'percent_discount',
                "period": 1,
                "value": "50"
            },{
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": '$5 discount',
                "type": 'discount',
                "period": 1,
                "value": "5"
            },{
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": '$10 discount',
                "type": 'discount',
                "period": 1,
                "value": "10"
            },{
                "createdAt": "1592186175",
                "modifiedAt": "1592186175",
                "name": '$20 discount',
                "type": 'discount',
                "period": 1,
                "value": "20"
            }
        ]

        promos = [Promo(x) for x in promo_dummy]

        dummy = [
            {
                "code": str(ObjectId()),
                "expire": '1592186175',
                "username": entityname,
                "info": promos[i].to_primitive(),
            } for i in range(len(promos)) for _ in range(2)
        ]
        self.repo.drop()


        [self.get_or_create_one(x) for x in dummy]

    def get_by_code(self,code):
        entity = self.model(self.repo.get_one({'code':code}),strict=False)
        entity.validate()
        return entity

    pass



