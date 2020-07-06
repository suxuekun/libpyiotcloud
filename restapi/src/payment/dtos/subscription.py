from schematics.types import ModelType, StringType
from payment.dtos.plan import PlanDTO
from payment.models.subscription import SubScriptionStatus, AbstractSubscription, AbstractSubscriptionHistory
from shared.simple_api.dto import BaseDTO


class SubscriptionItemDTO(BaseDTO):
    plan = ModelType(PlanDTO)

class CurrentSubscriptionDTO(SubscriptionItemDTO,AbstractSubscriptionHistory):
    pass

class NextSubscriptionDTO(SubscriptionItemDTO):
    pass

class SubscriptionDTO(BaseDTO,AbstractSubscription):
    current = ModelType(CurrentSubscriptionDTO)
    next = ModelType(NextSubscriptionDTO)
    # draft = ModelType(NextSubscriptionDTO)

    # def _check_draft(self,draft):
    #     if (not draft):
    #         self.draft = None

    def _normal_status(self):
        self.next = None
        # self._check_draft(self.draft)
    def _cancel_status(self):
        self.next = None
        pass
    # def _downgrade_status(self):
    #     pass
    transform_mapping = {
        SubScriptionStatus.NORMAL: _normal_status,
        SubScriptionStatus.CANCEL: _cancel_status,
        # SubScriptionStatus.DOWNGRADE: _downgrade_status,
    }
    def from_model(self,model_instance):
        super(SubscriptionDTO,self).from_model(model_instance)
        f = self.transform_mapping.get(self.status)
        if (f):
            f(self)
            self.validate()
        return self
    # def transform(self,raw):
    #     self.import_data(raw)
    #     self.validate()
    #     f = self.transform_mapping.get(self.status)
    #     if (f):
    #         f(self)
    #         self.validate()
    #     return self



