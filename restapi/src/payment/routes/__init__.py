import flask_cors
from flask import Blueprint
from flask_restful import Api

from payment.routes.billing_address import BillingAddressResource
from payment.routes.checkout import CheckoutResource, CancelSubscriptionResource
from payment.routes.plan import PlanResource, PlanListResource, PlanReloadResource
from payment.routes.promocode import PromocodeListResource, PromocodeResource
from payment.routes.prorate import ProrateResource
from payment.routes.subscription import SubscriptionResource, SubscriptionListResource
from payment.routes.token import TokenResource
from payment.routes.transaction import TransactionListResource, TransactionResource
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required

print('---payment_blueprint---')

payment_blueprint = Blueprint('payment_blueprint', __name__)

@payment_blueprint.before_request
@default_middleware
@login_required({
    'excludes':[{
        'endpoint':'payment_blueprint.planlist',
        'method':'GET',
    },{
        'endpoint':'payment_blueprint.plan',
        'methods':['GET'],
    },{
        'endpoint':'payment_blueprint.plan_reload',
        'methods':['GET'],
    }]
})
def payment_middleware_func():
    pass
#
# @payment_blueprint.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     print(response.headers)
#     return response


api =Api(payment_blueprint)
# PlanApi(api,prefix="plan")
# SubscriptionApi(api,prefix="subscription")
'''
7. billing address
    A. get billing address             - GET    /payment/billing_address/
    B. create billing address          - POST   /payment/billing_address/
'''
api.add_resource(BillingAddressResource,'/billing_address/')
'''
1. Plan:
    A. Get Plans                       - GET    /payment/plan/
    B. Get Plan Detail                 - GET    /payment/plan/{id}/
'''
api.add_resource(PlanListResource,'/plan/',endpoint='planlist')
api.add_resource(PlanResource,'/plan/<id>/',endpoint='plan')
api.add_resource(PlanReloadResource,'/plan_reload/',endpoint='plan_reload')
'''
3. Promocode
    A. get user promocodes             - GET    /payment/promocode/
    B. get user promocode              - GET    /payment/promocode/{id}/
'''

api.add_resource(PromocodeListResource,'/promocode/',endpoint='promocodelist')
api.add_resource(PromocodeResource,'/promocode/<code>/',endpoint='promocode')
'''
2. Subscription
    A. Get Subscriptions               - GET    /payment/subscription/
    B. Get Subscription Detail         - GET    /payment/subscription/{id}/
'''
api.add_resource(SubscriptionListResource ,'/subscription/',endpoint='subscriptionlist')
api.add_resource(SubscriptionResource,'/subscription/<id>/',endpoint='subscription')
'''
8. transaction history
    A. GET transactions                - GET    /payment/transaction/
    B. GET transactions Detail         - GET    /payment/transaction/{id}/
'''
api.add_resource(TransactionListResource ,'/transaction/',endpoint='transactionlist')
api.add_resource(TransactionResource,'/transaction/<id>/',endpoint='transaction')
'''
5 payment_blueprint5 Calculation Prorate
A. prorate                         - POST   /payment/prorate/calc/
'''
api.add_resource(ProrateResource,'/prorate/calc/',endpoint='prorate_calc')

'''
6. payment setup and checkout
A. get client token                - GET    /payment/client_token/ 
B. checkout                        - POST   /payment/checkout/
C. cancel subscription             - pOST   /payment/cancel_subscription/
'''
api.add_resource(TokenResource,'/client_token/',endpoint='client_token')
api.add_resource(CheckoutResource,'/checkout/',endpoint='checkout')
api.add_resource(CancelSubscriptionResource,'/cancel_subscription/',endpoint="cancel_subscription")
#
# api.add_resource(PlanListResource,'/plan/')
# api.add_resource(PlanResource,'/plan/<id>/')
# api.add_resource(OtherPlanResourced,'/plan/<int:id>/somthinbg/')