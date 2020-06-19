from flask_restful import Resource
from payment.services import billing_address_service
from shared.middlewares.request import informations
from shared.middlewares.request.permission.base import getRequest
from shared.middlewares.response import make_error_response, http4xx
from shared.simple_api.resource import PostMixin, throw_bad_request
from shared.wrapper.response import IotHttpResponseWrapper


class BillingAddressResource(Resource,PostMixin):
    service = billing_address_service
    wrapper_class = IotHttpResponseWrapper
    @throw_bad_request
    def get(self):
        request = getRequest()
        # entityname = informations.get_entityname(request)
        query = informations.get_entityname_query(request)
        data = self.service.get_or_create_one(query)
        res = self.to_api_data(data)
        if res:
            return self.to_result(res)
        else:
            return make_error_response(http4xx.DATA_NOT_FOUND)

    @throw_bad_request
    def post(self):
        request = getRequest()
        raw = request.get_json()
        query = informations.get_entityname_query(request)
        entity = self.service.get_one(query)
        entity.import_data(raw)
        entity.validate()
        res = self.service.update(str(entity._id), entity)
        return self.to_result(res)