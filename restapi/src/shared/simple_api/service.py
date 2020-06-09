class BaseSimpleApiService():
    def __init__(self,model,repo,**kwargs):
        self.repo = repo
        self.model = model

    def list(self,filter = None):
        return []
    def get(self,id):
        return None
    def create(self,entity):
        return None
    def update(self,id,entity):
        return None
    def delete(self,id):
        return True#False

class BaseMongoService(BaseSimpleApiService):
    def list(self,filter = None):
        pass
    def get(self,id):
        pass
    def create(self,entity):
        pass
    def update(self,id,entity):
        pass
    def delete(self,id):
        pass

