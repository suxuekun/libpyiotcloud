
'''
you need to create your won service to save real data
this is only a dummy service
'''
class BulkService():
    def __init__(self,*args,**kwargs):
        super(BulkService,self).__init__(*args,**kwargs)
        self.tag = type(self).__name__
        self._dummy_data = [{
            'id':'1',
            'attr':'this is object1'
        },{
            'id': '2',
            'attr': 'this is object2'
        }]
    def list(self,list_filter = None):
        return self._dummy_data

    def get(self, id):
        return self._dummy_data[int(id)-1]


    def create(self, entity):
        new_id = 3
        entity['id'] = new_id
        self._dummy_data.push(entity)
        return new_id

    def update(self, id, entity):
        self._dummy_data[int(id) - 1].update(entity)
        return id

    def delete(self, id):
        del self._dummy_data[int(id)-1]
        return True

buld_service = BulkService()



