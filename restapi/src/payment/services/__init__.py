from payment.core import payment_client
from payment.models.billing_address import BillingAddress
from payment.models.customer import UserCustomer
from payment.models.plan import Plan
from payment.models.promocode import PromoCode
from payment.models.promocode_usecount import Promocode_Usecount
from payment.models.subscription import Subscription
from payment.models.transaction import Transaction
from payment.repositories import subscription_repo, plan_repo, billing_address_repo, device_repo, \
    transaction_repo, customer_repo, promocode_usecount_repo, s3_promocode_repo
from payment.services.billing_address import BillingAddressService
from payment.services.customer import CustomerServiceService
from payment.services.payment import PaymentService
from payment.services.plan import PlanService
from payment.services.promocode import PromocodeS3Service
from payment.services.promocode_usecount import PromocodeUseCountService
from payment.services.subscription import SubscriptionService
from payment.services.transaction import TransactionService

plan_service = PlanService(Plan, plan_repo)
billing_address_service = BillingAddressService(BillingAddress,billing_address_repo)
customer_service = CustomerServiceService(UserCustomer,customer_repo)
promocode_usecount_service = PromocodeUseCountService(Promocode_Usecount,promocode_usecount_repo)
promocode_service = PromocodeS3Service(model=PromoCode,repo=s3_promocode_repo,usecount_service=promocode_usecount_service)

transaction_service = TransactionService(model=Transaction,
                                         repo=transaction_repo,
                                         billing_address_service=billing_address_service,
                                         customer_service=customer_service)
subscription_service = SubscriptionService(model=Subscription,
                                           repo=subscription_repo,
                                           device_repo=device_repo,
                                           plan_service = plan_service,
                                           payment_client=payment_client)

# complex service allow to register other simple service
payment_service = PaymentService(plan_repo=plan_repo,
                                 subscription_repo=subscription_repo,
                                 transaction_repo = transaction_repo,
                                 billing_address_service=billing_address_service,
                                 promocode_service = promocode_service,
                                 customer_service = customer_service,
                                 plan_service = plan_service)

if __name__ == "__main__":
    subscription_service.create(Subscription.get_mock_object().to_primitive())
