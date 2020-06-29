from functools import wraps

from schematics.exceptions import ValidationError


class BaseSimpleApiService():
    def __init__(self,model,repo,**kwargs):
        self.repo = repo
        self.model = model
    def rawlist(self,filter = None):
        return []
    def list(self,filter = None):
        return []
    def get(self,id):
        return None
    def create(self,raw):
        return None
    def update(self,id,raw):
        return None
    def delete(self,id):
        return True#False

def throw_bad_db_query(ret=None):
    def atholder(f):
        @wraps(f)
        def func(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as _:
                print(_)
                return ret
        return func
    return atholder

class BaseReadOnlyService(BaseSimpleApiService):
    @throw_bad_db_query()
    def get_one(self, query):
        raw = self.repo.get_one(query)
        if not raw:
            return None
        entity = self.model(raw, strict=False, validate=True)
        return entity

    @throw_bad_db_query()
    def rawlist(self, filter=None):
        l = self.list(filter)
        if l:
            return [x.to_primitive() for x in l]
        return l

    @throw_bad_db_query()
    def list(self, filter=None):
        raws = self.repo.gets(filter)
        if not raws:
            return []
        entities = [self.model(raw, strict=False, validate=True) for raw in raws]
        return entities

    @throw_bad_db_query()
    def get(self, id):
        raw = self.repo.getById(id)
        if not raw:
            return None
        entity = self.model(raw, strict=False, validate=True)
        return entity

class BaseS3Service(BaseReadOnlyService):
    pass

class BaseFileService(BaseReadOnlyService):
    pass


class BaseMongoService(BaseSimpleApiService):
    @throw_bad_db_query()
    def get_one(self,query):
        raw = self.repo.get_one(query)
        if not raw:
            return None
        entity = self.model(raw, strict = False,validate=True)
        return entity

    @throw_bad_db_query()
    def get_or_create_one(self, query):
        result = self.repo.get_one(query)
        if (not result):
            instance = self.model(query)
            result_id = self.create(instance)
            instance._id = result_id
            return instance
        entity = self.model(result, strict = False,validate=True)
        return entity

    @throw_bad_db_query()
    def rawlist(self,filter = None):
        l = self.list(filter)
        if l:
            return [x.to_primitive() for x in l]
        return l

    @throw_bad_db_query()
    def list(self,filter = None):
        raws = self.repo.gets(filter)
        if not raws:
            return []
        entities = [self.model(raw, strict=False, validate=True) for raw in raws]
        return entities

    @throw_bad_db_query()
    def get(self,id):
        raw = self.repo.getById(id)
        if not raw:
            return None
        entity = self.model(raw, strict = False,validate=True)
        return entity

    @throw_bad_db_query()
    def create(self,model_instance):
        entity = model_instance
        entity.validate()
        inserted_id = self.repo.create(entity.to_primitive())
        return inserted_id

    @throw_bad_db_query()
    def update(self,id,model_instance):
        raw_entity = self.repo.getById(id)
        entity = self.model(raw_entity,strict=False)
        entity.import_data(model_instance.to_primitive())
        entity.validate()
        res = self.repo.update(id, entity.to_primitive())
        return res

    @throw_bad_db_query(False)
    def delete(self,id):
        res = self.repo.delete(id)
        return res

