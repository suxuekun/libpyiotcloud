from schematics.types import StringType, IntType

from shared.core.model import MongoIdMixin, BaseModel


class Promocode_Usecount(BaseModel,MongoIdMixin):
    promocode = StringType()
    subscription_id = StringType()
    count = IntType(default=0)

    def get_count(self):
        return self.count if self.count else 0