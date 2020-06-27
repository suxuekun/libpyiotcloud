import os

from payment.core import payment_client
from payment.repositories.billing_address import BillingAddressRepository
from payment.repositories.customer import CustomerRepository
from payment.repositories.device import DeviceRepository
from payment.repositories.plan import PlanRepository
from payment.repositories.promocode import PromoCodeRepository, S3PromoCodeRepository
from payment.repositories.subscription import SubscriptionRepository
from payment.repositories.transaction import TransactionRepository
from payment.repositories.webhook import WebhookRepository
from rest_api_config import config
from s3_client import s3_client
from shared.client.db.mongo.default import DefaultMongoDB
from shared.client.db.mongo.test import TestMongoDB

payment_db = DefaultMongoDB()#TestMongoDB()

# will config later in config file
PLAN_COLLECTION = "payment_plan"
PROMOCODE_S3 = os.environ['AWS_S3_FILE_PROMOCODE']
PORMOCODE_COLLECTION = "payment_promocode"

SUBSCRIPTION_COLLECTION = 'payment_subscription'
BILLING_ADDRESS_COLLECTION = 'payment_billing_address'
TRANSACTION_COLLECTION = "payment_transaction"
USER_CUSTOMER = 'payment_user_customer'
WEBHOOK = 'payment_webhook'

webhook_repo = WebhookRepository(payment_db,WEBHOOK)

device_repo = DeviceRepository(payment_db,config.CONFIG_MONGODB_TB_DEVICES)

customer_repo = CustomerRepository(payment_db,USER_CUSTOMER)

# will change to s3
plan_repo = PlanRepository(payment_client,PLAN_COLLECTION)

subscription_repo = SubscriptionRepository(payment_db,SUBSCRIPTION_COLLECTION)

promocode_repo = PromoCodeRepository(payment_db,PORMOCODE_COLLECTION)
s3_promocode_repo = S3PromoCodeRepository(s3_client,PROMOCODE_S3)

billing_address_repo = BillingAddressRepository(payment_db,BILLING_ADDRESS_COLLECTION)

transaction_repo = TransactionRepository(payment_db,TRANSACTION_COLLECTION)





