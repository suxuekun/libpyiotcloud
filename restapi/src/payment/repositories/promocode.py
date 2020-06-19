from shared.core.repository.base_s3 import S3Repository
from shared.simple_api.repo import SimpleMongoBaseRepository

def _parse_value(v):
    pass

class PromoCodeRepository(SimpleMongoBaseRepository):
    pass

class S3PromoCodeRepository(S3Repository):
    # MAPPING = {
    #     'username':('username',None),
    #     'info':{
    #         'type':('discount type',None),
    #         'value':('discount value',_parse_value),
    #         'remark':('description',None)
    #     },
    # }
    def _make_promocode(self,raw):
        line = raw.split(',')
        if len(line)<8:
            return None
        # print ('line',line)
        id = line[0]
        name = line[1]
        type = line[2]
        value = line[3]
        remark = line[4]
        start = line[5]
        end = line[6]
        plans = line[7]
        return {
            "_id":id,
            'info':{
                'name':name,
                'type':type,
                'value':value,
                'expire':end,# do somethings
                'remark':remark,
            }
        }
    def _handler(self,raw):
        # print(raw)
        l = [x for x in raw.decode('UTF-8').replace("\r\n","\n").split('\n')]
        self.collection = [self._make_promocode(x) for x in l]
        self.collection = filter(lambda x:x is not None,self.collection)
        self._make_index()
        print('--promo--')
        [print(x) for x in self.collection]
        print(self.index)
    pass
