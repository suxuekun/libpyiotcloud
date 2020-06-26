
'''
you need to create your won service to save real data
this is only a dummy service
'''
from bson import ObjectId

from example_module.models.bulk import BulkSomthingModel


class BulkService():
    def __init__(self,*args,**kwargs):
        super(BulkService,self).__init__(*args,**kwargs)
        self.tag = type(self).__name__
        self._dummy_data = [BulkSomthingModel.get_mock_object(overrides={"_id":str(ObjectId())}) for _ in range(10)]

    def _filter(self,id):
        print (id,ObjectId(id))
        entity = None
        l = list(filter(lambda x: str(x._id) == id, self._dummy_data))
        print (len(l))
        if (l and len(l)):
            entity = l[0]
        return entity
    def rawlist(self,list_filter = None):
        return self._dummy_data

    def list(self,list_filter = None):
        return self._dummy_data

    def get(self, id):
        entity = self._filter(id)
        return entity


    def create(self, raw):
        new_id = ObjectId()
        entity = BulkSomthingModel(raw)
        entity._id = new_id
        entity.validate()
        self._dummy_data.push(entity)
        return new_id

    def update(self, id, raw):
        entity = self._filter(id)
        entity.import_data(raw)
        entity.validate()
        return True

    def delete(self, id):
        del self._dummy_data[int(id)-1]
        return True

bulk_service = BulkService()



