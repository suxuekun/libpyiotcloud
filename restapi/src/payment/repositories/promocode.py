from shared.core.repository.base_s3 import S3Repository
from shared.simple_api.repo import SimpleMongoBaseRepository
from shared.utils.pretty_print_util import pretty_print
from shared.utils.timestamp_util import timestamp_from_date_string


def _parse_time(time_string):
    '''
    ' default_format = '%m/%d/%Y'  7/1/2017    year 2017 month 7 day 1
    '''
    if (time_string):
        return timestamp_from_date_string(time_string)
    else:
        return None

def _parse_value(value_string):
    try:
        if '%' == value_string[-1]:
            return float(value_string[:-1])
        return value_string
    except Exception as e:
        print(e)
        return None



class PromoCodeRepository(SimpleMongoBaseRepository):
    pass

class S3PromoCodeRepository(S3Repository):
    '''
    ['id', 'name', 'discount type', 'discount value', 'sms', 'email', 'notification', 'storage', 'description', 'validity start', 'validity end', 'coverage period', 'applicable plans', 'max usage']
    ['PD05', '5% discount', 'price', '5%', '0', '0', '0', '0', 'get 5% discount for current month', '7/1/2020','7/31/2020', '1', 'Basic10 Upsize30 Supersize50', '1']
    '''
    ID = "_id"
    def _make_promocode(self,raw):
        line = raw.split(',')
        if len(line)<8:
            return None
        # print ('line',line)
        id = line[0]
        name = line[1]
        type = line[2]
        value = _parse_value(line[3])
        sms = line[4]
        email = line[5]
        notification = line[6]
        storage = line[7]

        remark = line[8]
        start = line[9]
        end = line[10]
        period = line[11]
        plans = line[12]
        max_usage = line[13]
        item = {
            "_id":id,
            'name':name,
            'type':type,
            'value':value,
            'start':_parse_time(start),# change format
            'end':_parse_time(end),# change format
            'sms':sms,
            'email':email,
            'notification':notification,
            'storage':storage,
            'remark':remark,
            'period':period,
            'plans':plans.split(' '),
            'max_usage':max_usage
        }
        # pretty_print(item)
        if (value):
            return item
        return None

    def _handler(self,raw):
        # print(raw)
        l = [x for x in raw.decode('UTF-8').replace("\r\n","\n").split('\n')]
        self.collection = [self._make_promocode(x) for x in l[1:]]
        self.collection = list(filter(lambda x:x is not None,self.collection))
        self._make_index()

    pass
