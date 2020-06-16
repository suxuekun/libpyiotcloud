from shared.core.model import BaseModel


class BaseDTO(BaseModel):
    MODEL = None
    def transform(self,raw):
        self.import_data(raw)
        self.validate()
        return self

    def from_model(self,model_instance):
        self.import_data(model_instance.to_primitive())

    def to_model(self):
        if self.MODEL:
            return self.MODEL(self.to_primitive())
        else:
            return self


