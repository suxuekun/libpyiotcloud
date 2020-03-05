/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('payments', [])

.service('Payments', ['$http', 'Server', 'User', 'Token', function($http, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch_paypal_payments: function(userdata) {
            
            console.log(userdata);
            
            //
            // GET PAYPAL TRANSACTIONS
            //
            // - Request:
            //   GET /account/payment/paypal
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   { 'status': 'OK', 'message': string, 'transactions': [{'id': string, 'amount': float, 'time': string, 'credits': int}, ...]}
            //   { 'status': 'NG', 'message': string}
            //
            return $http({
                method: 'GET',
                url: server + '/account/payment/paypal',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                // Handle successful login
                console.log(result.data);
                
                for (var indexy=0; indexy<result.data.transactions.length; indexy++) {
                    let timestamp = new Date(result.data.transactions[indexy].timestamp * 1000); 
                    result.data.transactions[indexy].timestamp = "" + timestamp;
                }
                
                return result.data.transactions;
            })
            .catch(function (error) {
                // Handle failed login
                if (error.data !== null) {
                    console.log("ERROR: Login failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                }
                return [];
            });
        },
        
    };
    
    return ret;
}]);
