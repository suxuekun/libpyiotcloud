from shared.simple_api.repo import SimpleMongoBaseRepository


class PromoCodeUseCountRepository(SimpleMongoBaseRepository):
    def update_one(self,*args,**kwargs):
        res = self.collection.update_one(*args,**kwargs)
        return res.matched_count
    pass