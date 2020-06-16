;(function(_global){
    var app = _global.app
    app
    .service('BraintreePayment', ['$http', 'Server', 'User' ,
        function($http,Server,User){
            var ret = {
                get:function(url){
                    return this.promise({
                        method:"GET",
                        url:url,
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
                get_promocodes:function(){
                    return this.get(Server.rest_api + '/payment/promocode/')
                },
                checkout:function(data){
                    $http.post(Server.rest_api + '/payment/checkout/',data)

                }
            };
            return ret;
        }]);

}(window))


