;(function(_global){
    var app = angular.module('payments.service', [])
    app
    .service('BraintreePayment', ['$http', 'Server', 'User' ,
        function($http,Server,User){
            var ret = {
                get:function(url,params){
                    return this.promise({
                        method:"GET",
                        url:url,
                        params:params,
                    })
                },
                post:function(url,data){
                    return this.promise({
                        method:"POST",
                        url:url,
                        data:data,
                    })
                },
                promise:function(options){
                    options.headers = User.get_auth_header()
                    var promise = $http(options)
                    return promise
                },
                get_client_token:function(){
                    return this.get(Server.rest_api + '/payment/client_token/')
                },
                get_subscriptions:function(){
                    return this.get(Server.rest_api + '/payment/subscription/')
                },
                get_plans:function(){
                    return this.get(Server.rest_api + '/payment/plan/')
                },
                get_transactions:function(){
                    return this.get(Server.rest_api + '/payment/transaction/')
                },
                get_promocodes:function(params){
                    return this.get(Server.rest_api + '/payment/promocode/',params)
                },
                verify_promocode:function(data){
                    return this.post(Server.rest_api + '/payment/promocode_verify/',data)
                },
                get_billing_address:function(){
                    return this.get(Server.rest_api + '/payment/billing_address/')
                },
                save_billing_address:function(data){
                    return this.post(Server.rest_api + '/payment/billing_address/',data)
                },
                prorate:function(old_plan_id,new_plan_id,promocode){
                    var option = {
                        old_plan_id:old_plan_id,
                        new_plan_id:new_plan_id,
                    }
                    if (promocode){
                        option.promocode = promocode
                    }
                    return this.get(Server.rest_api + '/payment/prorate/calc/',option)
                },
                checkout:function(data){
                    return this.post(Server.rest_api + '/payment/checkout/',data)
                },
                cancel_subscription:function(data){
                    return this.post(Server.rest_api + '/payment/cancel_subscription/',data)
                },
            };
            return ret;
        }]);

}(window))


