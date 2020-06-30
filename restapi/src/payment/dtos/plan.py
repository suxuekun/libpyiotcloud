from payment.models.plan import Usage, AbstractPlan, Plan
from shared.simple_api.dto import BaseDTO


class PlanDTO(BaseDTO,AbstractPlan):
    MODEL = Plan
    pass