from functools import wraps
from shared.core.base_repository import BaseRepository
from shared.utils import dict_util


def catch_throw_exception(excep=None):
    def atholder(func):
        @wraps(func)
        def f(*args,**kwargs):
            try:
                func(*args,**kwargs)
            except Exception as e:
                print(e)
                raise excep(str(e))
        return f
    return atholder

class ReadOnlyRepo(BaseRepository):
    ID = "id"
    def __init__(self, raw,*args,**kwargs):
        self.raw = raw
        self.collection = None
        self.index = None
        if (self.raw):
            self._handler(self.raw)

    def reload(self):
        self._handler(self.raw)
        pass

    def _handler(self,raw):
        # make collection and index here
        pass

    def _make_index(self):
        self.index = dict_util.list_to_index_dict(self.collection,self.ID)

    def getById(self, id: str):
        return self.index.get(id)

    def _cast_object_without_objectId(self, data):
        data["_id"] = str(data["_id"])
        return data

    def gets(self, query=None):
        if query:
            l = dict_util.filter_list_of_dict(self.collection)
        else:
            l = list(self.collection)
        return l

    def get_one(self, query):
        l = self.gets(query)
        return l[0]