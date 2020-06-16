from payment.models.plan import Plan
from shared.simple_api.service import throw_bad_db_query
from shared.utils.timestamp_util import percent_of_month_left


#
#
# def prorate(current_plan_id,next_plan_id):
#     nextPlan =
#     currentPlan
#     _, remain, total = percent_of_month_left()
#     discount, prorate = payment_client._get_discounted_amount(nextPlan.price - currentPlan.price, remain, total)
#     res = {
#         'prorate': prorate,
#         'discount': discount,
#     }
#
#     return HttpResponse(toJson(res))
#
#
#
#
#
# def pay(request):
#     post = json.loads(request.body)
#     nonce = post.get('nonce')
#     uid = post.get('uid')
#
#     customer = getUserCustomer(uid)
#     cid = customer.bt_c_id
#     payment_token = getPyamentMethodToken(cid, nonce)
#     if not payment_token:
#         return HttpResponse('401', 401)
#
#     devices = post.get('devices')
#
#     bill = 0
#     for device in devices:
#         nextPlan = device.get('nextPlan')
#         promoCode = device.get('promoCode')
#         promocode = None
#         if (promoCode):
#             promocode = promoCode.get('code')
#         if nextPlan:
#             prorate = updateSubscription(device.get('id'), nextPlan.get('id'), promocode, payment_token)
#             print('device update', device.get('id'), nextPlan.get('id'), prorate)
#             bill += prorate
#     if (bill > 0):
#         res = makeTransaction(bill, payment_token)
#         print(res)
#         if res.is_success:
#             trans_id = res.transaction.id
#             billing = Billing(user_id=uid, bt_trans_id=trans_id, amount=bill)
#             billing.save()
#             return HttpResponse(toJson(res))
#         else:
#             return HttpResponse('500', 500)
#     return HttpResponse('OK')
#
#
# def getUserCustomer(uid):
#     customers = UserCustomer.objects.filter(user_id=uid)
#     customer = None
#     if len(customers) > 0:
#         customer = customers[0]
#     if not customer:
#         user = User.objects.get(pk=uid)
#         bt_customer = payment_client.create_customer({'first_name': user.username})
#         cid = bt_customer.id
#         customer = UserCustomer(user_id=uid, bt_c_id=cid)
#     return customer
#
#
# def getPyamentMethodToken(cid, nonce):
#     print("---", cid, nonce)
#     result = payment_client.create_payment_method(cid, nonce)
#
#     if result.is_success:
#         return result.payment_method.token
#     else:
#         return None
#
#
# def makeTransaction(amount, payment_method_token):
#     return payment_client.create_transaction(amount, payment_method_token, None, True)
#
#
# def updateSubscription(did, pid, promocode, payment_method_token):
#     prorate = 0
#
#     device = Device.objects.get(pk=did)
#     subscriptions = Subscription.objects.filter(device_id=did)
#
#     currentSub = None
#     nextSub = None
#
#     freePlan = Plan.objects.get(pk=1)
#     newPlan = Plan.objects.get(pk=pid)
#
#     for sub in subscriptions:
#         if sub.current:
#             currentSub = sub
#         else:
#             nextSub = sub
#
#     if (not currentSub):
#         currentSub = Subscription(user=device.user, device=device, plan=freePlan, current=True)
#         currentSub.save()
#     if (not nextSub):
#         nextSub = Subscription(user=device.user, device=device, plan=freePlan, current=False)
#         nextSub.save()
#
#     action = 0  # 0 create , 1 upgrade ,2 cancel
#     assign = 0  # 0 next change only, 1 Current = next
#     change_amount = 0
#
#     status = (not currentSub.plan.is_free(), not nextSub.plan.is_free(), not newPlan.is_free())
#
#     if status == (0, 0, 1):  # Free Free -> Paid Create Sub
#         action = 0
#         assign = 1
#         change_amount = newPlan.price
#     elif status == (1, 1, 0):  # Paid Paid -> Free  Cancel sub
#         action = 2
#         assign = 0
#         change_amount = 0
#
#     elif status == (1, 0, 1):  # Paid Free -> Paid , upgrade plan when previous cancel ,need recreate new sub
#         action = 0
#         assign = 0
#         change_amount = newPlan.price - currentSub.plan.price
#
#     elif status == (1, 1, 1):  # Paid Paid -> Paid change plan, update sub only
#         action = 1
#         assign = 0
#         change_amount = newPlan.price - currentSub.plan.price
#         if (change_amount > 0):
#             assign = 1
#
#     else:
#         action = -1
#         return 0
#
#     if (action == 0):
#         result = payment_client.create_subscription(newPlan.bt_plan_id, payment_method_token)
#         new_sub_id = result.subscription.id
#         nextSub.plan = newPlan
#         nextSub.bt_sub = new_sub_id
#         nextSub.save()
#     elif (action == 1):
#         options = {
#             'plan_id': newPlan.bt_plan_id
#         }
#         result = payment_client.update_subscription(nextSub.bt_sub, options)
#         nextSub.plan = newPlan
#         nextSub.save()
#     elif (action == 2):
#         result = payment_client.cancel_subscription(nextSub.bt_sub)
#         nextSub.bt_sub = None
#         nextSub.plan = newPlan
#         nextSub.save()
#
#     if (assign):
#         currentSub.plan = newPlan
#         currentSub.bt_sub = nextSub.bt_sub
#         currentSub.save()
#     if (change_amount > 0):
#         _, remain, total = percent_of_month_left()
#         _, prorate = payment_client._get_discounted_amount(change_amount, remain, total)
#     if (prorate > 0 and promocode):
#         try:
#             print("---promocode", promocode)
#             p = PromoCode.objects.get(code=promocode)
#         except:
#             pass
#         if (p and p.promo.type == "discount"):
#             prorate = (100 - p.promo.value) * prorate / 100
#             p.delete()
#     return round(prorate, 2)

from payment.core import payment_client

class PaymentService():
    def __init__(self,plan_repo,subscription_repo,transaction_repo,billing_address_service,promocode_service):
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.transaction_repo = transaction_repo
        self.billing_address_service = billing_address_service
        self.promocode_service = promocode_service
    def get_client_token(self):
        token = payment_client.generate_client_token()
        return token

    def _cancel_subscription(self,subscription):

        pass

    def _upgrade_subscription(self,subscription,plan):
        pass

    def _downgrade_subscription(self,subscription,plan):
        pass

    def change_subscription(self,subscription_id,plan_id):
        pass

    def checkout(self,):
        return None
    @throw_bad_db_query()
    def prorate(self,old_plan_id,new_plan_id,promocode,query):
        current_plan = Plan(self.plan_repo.getById(old_plan_id))
        current_plan.validate()
        next_plan = Plan(self.plan_repo.getById(new_plan_id))
        next_plan.validate()
        _, remain, total = percent_of_month_left()
        rate = 1

        plan_gap_amount = (next_plan.price - current_plan.price) * rate

        _discount, total_payable = payment_client._get_discounted_amount(next_plan.price, remain, total)
        _ , plan_rebate = payment_client._get_discounted_amount(current_plan.price, remain, total)
        prorate = total_payable - plan_rebate
        total_discount = plan_rebate
        promo_discount = 0.00
        if promocode:
            promoModel = self.promocode_service.get_by_code(promocode)
            if promoModel:
                payable,promo_discount= promoModel.calc(prorate)
                prorate = payable
                total_discount += promo_discount
        b = self.billing_address_service.get_or_create_one(query)

        res = {
            'price':next_plan.price,
            'total_payable': total_payable,
            'plan_rebate': plan_rebate,
            'total_discount': total_discount,
            'promo_discount':promo_discount,
            'prorate': prorate,
            'remaining_days':remain,
            'total_days':total,
            'gst':b.get_gst()
        }
        return res

