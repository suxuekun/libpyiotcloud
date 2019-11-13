angular.module('app.controllers', [])
  
.controller('homeCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {

}
])
   
.controller('devicesCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Devices',     // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Devices) {

    var server = Server.rest_api;

    $scope.devices = [];

    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    };

    $scope.showHelp = false;

    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };

    $scope.submitTest = function(devicename) {

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': devicename
        };
       
        $state.go('controlDevice', device_param );
    };

    $scope.submitAdd = function() {

        $state.go('registerDevice', $scope.data);
    };
    
    $scope.submitRefresh = function() {

        // Fetch devices
        Devices.fetch($scope.data).then(function(res) {
            $scope.devices = res;
            if ($scope.devices.length === 0) {        
                //$ionicPopup.alert({
                //    title: 'Query Devices',
                //    template: 'No devices registered!',
                //});
            }
            $scope.data.token = User.get_token();
        });
    };
    
    $scope.submitView = function(device) {
        console.log("view" + device.devicename);
        
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicename=" + device.devicename);

        //
        // GET DEVICE
        //
        // - Request:
        //   GET /devices/device/<devicename>
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey}}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'GET',
            url: server + '/devices/device/' + device.devicename,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            update_token(result);
            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'devicecert': result.data.device.cert,
                'devicepkey': result.data.device.pkey,
                'deviceca': result.data.device.ca
            };
            $state.go('viewDevice', device_param);
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: View Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: View Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        }); 
    };

    $scope.submitDelete = function(device) {
        $ionicPopup.alert({
            title: 'Delete Device',
            template: 'Are you sure you want to delete this device?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.submitDeleteAction(device);
                    }
                }
            ]            
        });            
    };
    
    $scope.submitDeleteAction = function(device) {
        console.log("delete");
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicename=" + device.devicename);

        var device_param = {
            'username': $scope.data.username,
            'devicename': device.devicename
        };       
        
        //
        // DELETE DEVICE
        //
        // - Request:
        //   DELETE /devices/device
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'DELETE',
            url: server + '/devices/device',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: device_param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            update_token(result);
            $scope.submitRefresh();
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Delete Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Delete Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        });         
    };
    
    //console.log("DEVICES username=" + User.get_username());
    //console.log("DEVICES token=" + User.get_token());
    // Send HTTP request to REST API
    //$scope.submitRefresh();
    //console.log($scope.devices);
    
    
    $scope.$on('$ionicView.enter', function(e) {
        //console.log("DEVICES enter ionicView REFRESH LIST");
        $scope.submitRefresh();
    });
    
}])
   
.controller('accountCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),

        'fullname': 'Unknown',
        'email': 'Unknown',
        'mobile': 'Unknown',

        'subscription_type': 'Unknown',
        'subscription_credits': 'Unknown',
        
        'activeSection': 1,
    };

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
    };
    
    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };

    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Server is down!");
        }
    };

    get_subscription = function() {
        //
        // GET SUBSCRIPTION
        //
        // - Request:
        //   GET /user/subscription
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'GET',
            url: server + '/user/subscription',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log("get_subscription");
            console.log(result.data);
            update_token(result);
            
            $scope.data.subscription_type = result.data.subscription.type;
            $scope.data.subscription_credits = result.data.subscription.credits;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    get_profile = function() {
        //        
        // GET USER INFO
        //
        // - Request:
        //   GET /user
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'info': {'email': string, 'family_name': string, 'given_name': string} }
        //   {'status': 'NG', 'message': string}
        //         
        $http({
            method: 'GET',
            url: server + '/user',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log("ACCOUNT OK");
            console.log(result.data);
            update_token(result);
            $scope.data.fullname = result.data.info.given_name + " " + result.data.info.family_name;
            $scope.data.email = result.data.info.email;
            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    $scope.$on('$ionicView.enter', function(e) {

        if (($scope.data.username !== User.get_username()) && 
            ($scope.data.token !== User.get_token())) {

            $scope.data.username = User.get_username();
            $scope.data.token = User.get_token();

            console.log("ACCOUNT ionicView get_profile");
            get_profile({
                'username': $scope.data.username,
                'token': $scope.data.token
            });
        }

        console.log("ACCOUNT ionicView get_subscription");
        get_subscription();

    });


    console.log("ACCOUNT get_profile");
    get_profile();

    console.log("ACCOUNT get_subscription");
    get_subscription();


    $scope.submitBuycredits = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
     
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('order', device_param, {reload: true});   
    };
}
])
   
.controller('orderCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;

    $scope.credits = [
        {
            "id": "CREDS500USD5", "points": "500", "price": "1",
            "label": "500 credits - $1",
        },
        {
            "id": "CREDS1000USD9", "points": "1000", "price": "9",
            "label": "1000 credits - $9",
        },
        {
            "id": "CREDS5000USD40", "points": "5000", "price": "40",
            "label": "5000 credits - $40",
        },
        {
            "id": "CREDS10000USD70", "points": "10000", "price": "70",
            "label": "10000 credits - $70",
        },
    ];


    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        
        'id': $scope.credits[0].id,
        'price': $scope.credits[0].price,
        'label': $scope.credits[0].label,
        'points': $scope.credits[0].points,
    };


    $scope.submitCancel = function() {
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('menu.account', device_param, {reload: true});   
    };
    
    $scope.submitBuycredits = function() {
        
        //var spinner = document.getElementsByClassName("spinner");
        //spinner[0].style.visibility = "visible";
        
        for (var i=0; i<$scope.credits.length; i++) {
            if ($scope.data.id === $scope.credits[i].id) {
                $scope.data.price = $scope.credits[i].price;
                $scope.data.label = $scope.credits[i].label;
                $scope.data.points = $scope.credits[i].points;
                break;
            }
        }
        console.log(
            "id=" + $scope.data.id + " " +
            "points=" + $scope.data.points + " " +
            "price=" + $scope.data.price
            );
        
        $ionicPopup.alert({
            title: 'Subscription',
            template: 'You have selected to buy ' + 
                $scope.data.points + ' credits at $' + $scope.data.price + ' USD. ' +
                'Would you like to proceed payment via Paypal?',
                
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        console.log("YES!");
                        process_payment_paypal();
                    }
                }
            ]
        });
    };
    
    process_payment_paypal = function() {

        console.log("process_payment_paypal");

        var host_url = server; //"http://localhost:8100"; 
        var return_url = host_url + '/#/page_payment_confirmation?' + 'username=' + 
            $scope.data.username + '&access=' + $scope.data.token.access + '&credits=' + $scope.data.points;
        var cancel_url = host_url + '/#/page_payment_confirmation?' + 'username=' + 
            $scope.data.username + '&access=' + $scope.data.token.access;

        console.log(return_url);
        console.log(cancel_url);

        var paypal_param = {
            'payment': {
                'return_url': return_url,
                'cancel_url': cancel_url,
                'item_sku': $scope.data.id,
                'item_credits': $scope.data.points,
                'item_price': $scope.data.price,
            }
        };


        //       
        // PAYPAL SETUP
        //
        // - Request:
        //   POST /user/payment/paypalsetup
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'payment': {'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string} }
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'approval_url': string, 'paymentId': string, 'token': string}
        //   {'status': 'NG', 'message': string}    
        //
        $http({
            method: 'POST',
            url: server + '/user/payment/paypalsetup',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            console.log(result.data.approval_url);
            console.log(result.data.paymentId);
            console.log(result.data.token);

            var win = window.open(result.data.approval_url,"_blank",
                'height=600,width=800,left=100,top=100,resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=no,directories=no,status=no',replace=false);

            var timer = setInterval(function() {
                if (win.closed) {
                    clearInterval(timer);
                    verifyPayment({ 
						"payment": {
							"paymentId": result.data.paymentId
						} 
					});
                }
            }, 1000);

            //window.open(result.data.approval_url);
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Paypal Setup failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Paypal Setup failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        });
        
        // TODO Update database credits
    };

    getSubscription = function() {
        //
        // GET SUBSCRIPTION
        //
        // - Request:
        //   GET /user/subscription
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'GET',
            url: server + '/user/subscription',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log("get_subscription");
            console.log(result.data);
            update_token(result);

            $ionicPopup.alert({
                title: 'Payment Confirmation',
                template: 'Payment transaction was successful. Your new credit balance is ' + result.data.subscription.credits + '.',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            $state.go('menu.account', param, {reload: true});   
                        }
                    }
                ]
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    verifyPayment = function(paypal_param) {
        //
        // PAYPAL VERIFY
        //
        // - Request:
        //   POST /user/payment/paypalverify
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'payment': {'paymentId': string} }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/user/payment/paypalverify',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            if (result.data.status === "OK") {
                getSubscription();
            }
            else {
                $ionicPopup.alert({
                    title: 'Payment Confirmation',
                    template: 'Payment transaction was not successful. Please try again!',
                    buttons: [
                        {
                            text: 'OK',
                            type: 'button-positive',
                            onTap: function(e) {
                            }
                        }
                    ]
                });
            }
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                console.log("ERROR: Paypal Verification failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Paypal Setup Verification with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
            window.close();
        });
    };
}])
   
.controller('paymentConfirmationCtrl', ['$scope', '$stateParams', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $ionicPopup, $http, Server) {

    var server = Server.rest_api;
    var spinner = document.getElementsByClassName("spinner2");
    
    $scope.data = {
        'token': {'access': ''},
        'credits': ''
    }    
        
    function GetURLParameter(sParam) {
        var sPageURL = window.location.href.substring(1);
        try {
            var sPageParameters = sPageURL.split('?');
            if (sPageParameters !== null) {
                var sURLVariables = sPageParameters[1].split('&');
                if (sURLVariables !== null) {
                    for (var i = 0; i < sURLVariables.length; i++) {
                        var sParameterName = sURLVariables[i].split('=');
                        if (sParameterName[0] == sParam) {
                            return sParameterName[1];
                        }
                    }
                }
            }
        }
        catch(err) {
        }
        return null;
    }

    function GetURLParameters() {
        var username = GetURLParameter('username');
        var access = GetURLParameter('access');
        var credits = GetURLParameter('credits');
        var payment_paymentId = GetURLParameter('paymentId');
        var payment_token = GetURLParameter('token');
        var payment_PayerID = GetURLParameter('PayerID');

        if (username !== null && access !== null) {
            $scope.data.token.access = access;
            if (credits !== null) {
                $scope.data.credits = credits;
            }

            params = { 
                "username": username
            };
            if (payment_token !== null) {
                params.payment = {
                    "token": payment_token
                };
            }
            if (payment_paymentId !== null && payment_PayerID !== null) {
                params.payment.paymentId = payment_paymentId;
                params.payment.PayerID = payment_PayerID;
            }
            return params;
        }
        return null;
    }

    function setSubscription(param) {
        //
        // SET SUBSCRIPTION
        //
        // - Request:
        //   POST /user/subscription
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'credits': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid}}
        //   {'status': 'NG', 'message': string}        
        //  
        console.log("set_subscription");
        console.log(param);
        $http({
            method: 'POST',
            url: server + '/user/subscription',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.status === "OK") {
                spinner[0].style.visibility = "hidden";
                
                $ionicPopup.alert({
                    title: 'Payment Confirmation',
                    template: 'The payment transaction has been verified. ' + 
                        param.credits + ' credits has been successfully added to your account! ' + 
                        'Your new credit balance is ' + result.data.subscription.credits + '.',
                    buttons: [
                        {
                            text: 'OK',
                            type: 'button-positive',
                            onTap: function(e) {
                                window.close();
                            }
                        }
                    ]
                });
            }
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                console.log("ERROR: Set Subscription failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Paypal Set Subscription with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
            window.close();
        }); 
    }

    function verifyPayment(paypal_param) {
        //
        // PAYPAL VERIFY
        //
        // - Request:
        //   POST /user/payment/paypalverify
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'payment': {'paymentId': string} }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //        
        console.log("paypalverify");
        console.log(paypal_param);
        $http({
            method: 'POST',
            url: server + '/user/payment/paypalverify',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.status === "OK") {
                setSubscription({ 'credits': $scope.data.credits });
            }
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                console.log("ERROR: Paypal Verification failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Paypal Setup Verification with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
            window.close();
        });
    }

    function executePayment(paypal_param) {
        //
        // PAYPAL EXECUTE
        //
        // - Request:
        //   POST /user/payment/paypalexecute
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'payment': {'paymentId': string, 'payerId': string, 'token': string} }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        console.log("paypalexecute");
        console.log(paypal_param);
        $http({
            method: 'POST',
            url: server + '/user/payment/paypalexecute',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.status === "OK") {
                verifyPayment(paypal_param);
            }
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                console.log("ERROR: Paypal Execution failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Paypal Setup Execution with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
            window.close();
        });
    }

    spinner[0].style.visibility = "visible";
    paypal_param = GetURLParameters();
    if (paypal_param !== null) {
        console.log("GetURLParameters: ");
        console.log(paypal_param);
        console.log(paypal_param.payment);

        if (paypal_param.payment.PayerID !== undefined) {
            console.log("Customer approved the transaction!");
            executePayment(paypal_param);
        }
        else {
            console.log("Customer cancelled the transaction! token=" + paypal_param.payment.token);
            window.close();
        }
    }
}])
   
.controller('menuCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, User) {

    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    }

    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter ionicView");
        if ($scope.data.username === "") {
            $scope.data.username = User.get_username();
        }
        if ($scope.data.token === "") {
            $scope.data.token = User.get_token();
        }
    });

    //$scope.$on('$ionicView.leave', function(e) {
    //    console.log("leave ionicView");
    //});

    //console.log("MENU " + $scope.data.username);
    //console.log("MENU " + User.get_username());

    $scope.submitLogout = function() {
        
        $ionicPopup.alert({
            title: 'Log out',
            template: 'Are you sure you want to log out?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.submitLogoutAction();
                    }
                }
            ]            
        });            
        
        
    }
    
    $scope.submitLogoutAction = function() {
        $scope.data.username = "";        
        $scope.data.token = "";        
        User.clear();
        $state.go('login');
    }
    
}

  
  
])
   
.controller('loginCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $scope.username,
        'password': $scope.password
    }
    
    $scope.submit = function() {
        
        //console.log("username=" + $scope.data.username);
        //console.log("password=" + $scope.data.password);

        // Handle invalid input        
        if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Login Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.password.length === 0) {
            $ionicPopup.alert({title: 'Login Error', template: 'Password is empty!'});
            return;
        }


        // Display spinner
        var spinner = document.getElementsByClassName("spinner");
        spinner[0].style.visibility = "visible";

 
        console.log("login: " + new Date().getTime());


        // 
        // LOGIN
        // 
        // - Request:
        //   POST /user/login
        //   { 'username': string, 'password': string }
        // 
        // - Response:
        //   {'status': 'OK', 'token': {'access': string, 'id': string, 'refresh': string} }
        //   {'status': 'NG', 'message': string}
        //         
        $http({
            method: 'POST',
            url: server + '/user/login',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            console.log("login: OK " + new Date().getTime());
            // Handle successful
            console.log(result.data);

            var user_data = {
                'username': $scope.data.username,
                'token': result.data.token
            }
            
            User.set(user_data);
        
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Login Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Login Error', template: 'Server is down!'});
            }
        });
    }
}])
   
.controller('signupCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $scope.username,
        'password': $scope.password,
        'password2': $scope.password2,
        'email': $scope.email,
        'givenname': $scope.givenname,
        'familyname': $scope.familyname
    }
    
    $scope.submit = function() {
        // Handle invalid input        
        if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.password.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.password.length < 6) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Password should be at least 6 characters!'});
            return;
        }        
        else if ($scope.data.password2 !== $scope.data.password) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Passwords do not match!'});
            return;
        }
        else if ($scope.data.email === undefined) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Email is invalid!'});
            return;
        }        
        else if ($scope.data.email.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Email is empty!'});
            return;
        }        
        else if ($scope.data.givenname === undefined) {
            $ionicPopup.alert({title: 'Signup Error', template: 'First name is invalid!'});
            return;
        }        
        else if ($scope.data.familyname === undefined) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Last name is invalid!'});
            return;
        }        
        else if ($scope.data.givenname.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'First name is empty!'});
            return;
        }        
        else if ($scope.data.familyname.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Last name is empty!'});
            return;
        }
        
        
        // Display spinner
        var spinner = document.getElementsByClassName("spinner3");
        spinner[0].style.visibility = "visible";
 
 
        // 
        // SIGN-UP
        // 
        // - Request:
        //   POST /user/signup
        //   { 'username': string, 'password': string, 'email': string, 'givenname': string, 'familyname': string }
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'POST',
            url: server + '/user/signup',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            // Handle successful login
            console.log(result.data);
        
            $scope.data = {
                'username': $scope.data.username,
            }
            $state.go('confirmRegistration', $scope.data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Signup Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Signup Error', template: 'Server is down!'});
            }
            return;
        });       
    }
}])
   
.controller('recoverCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'email': $scope.email
    }
    
    $scope.submit = function() {
        console.log("email=" + $scope.data.email);

        // Handle invalid input
        if ($scope.data.email === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Email is empty!'});
            return;
        }          
        else if ($scope.data.email.trim().length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Email is empty!'});
            return;
        }


        // Display spinner
        var spinner = document.getElementsByClassName("spinner5");
        spinner[0].style.visibility = "visible";
        

        //
        // FORGOT PASSWORD
        //
        // - Request:
        //   POST /user/forgot_password
        //   { 'email': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'username': string}
        //   {'status': 'NG', 'message': string}         
        //         
        $http({
            method: 'POST',
            url: server + '/user/forgot_password',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            // Handle successful login
            console.log(result.data);
            
            $scope.data = {
                'username': result.data.username
            }
            $state.go('resetPassword', $scope.data);            
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed login
            console.log(error);
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Recovery Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Recovery Error', template: 'Server is down!'});
            }
            return;
        });
    }
    
    $scope.submitCancel = function() {
        $state.go('login');
    }    
}])
   
.controller('resetPasswordCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'confirmationcode': $scope.confirmationcode,
        'password': $scope.password,
        'password2': $scope.password2
    }
    
    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("confirmationcode=" + $scope.data.confirmationcode);
        console.log("password=" + $scope.data.password);
        
        // Handle invalid input        
        if ($scope.data.username === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.username.trim().length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode.trim().length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.password === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.password.trim().length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.password.trim().length < 6) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Password should be at least 6 characters!'});
            return;
        } 
        else if ($scope.data.password2 !== $scope.data.password) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Passwords do not match!'});
            return;
        } 


        // Display spinner
        var spinner = document.getElementsByClassName("spinner6");
        spinner[0].style.visibility = "visible";
        

        //
        // CONFIRM FORGOT PASSWORD
        //
        // - Request:
        //   POST /user/confirm_forgot_password
        //   { 'username': string, 'confirmationcode': string, 'password': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/confirm_forgot_password',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            // Handle successful
            console.log(result.data);
            $ionicPopup.alert({title: 'Recovery', template: 'Recovery completed!'});
            $state.go('login');            
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed
            console.log(error);
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Recovery Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Recovery Error', template: 'Server is down!'});
            }
            return;
        });
    }
    
    $scope.submitCancel = function() {
        $state.go('recover');
    }    
    
}])
   
.controller('confirmRegistrationCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'confirmationcode': $scope.confirmationcode
    }
    
    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("confirmationcode=" + $scope.data.confirmationcode);
        
        // Handle invalid input        
        if ($scope.data.confirmationcode === undefined) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Code is empty!'});
            return;
        }


        // Display spinner
        var spinner = document.getElementsByClassName("spinner4");
        spinner[0].style.visibility = "visible";


        // 
        // CONFIRM SIGN-UP
        // 
        // - Request:
        //   POST /user/confirm_signup
        //   { 'username': string, 'confirmationcode': string }
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'POST',
            url: server + '/user/confirm_signup',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            // Handle successful
            console.log(result.data);
            $ionicPopup.alert({title: 'Signup', template: 'Registration completed!'});
            $state.go('login');
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed
            console.log(error);
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Signup Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Signup Error', template: 'Server is down!'});
            }
            return;
        });       
    }
    
    $scope.submitResend = function() {
        console.log("username=" + $scope.data.username);

        // Handle invalid input        
        if ($scope.data.username === undefined) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Username is empty!'});
            return;
        }

        var param = {
            'username': $scope.data.username
        }


        // 
        // RESEND CONFIRMATION CODE
        // 
        // - Request:
        //   POST /user/resend_confirmation_code
        //   { 'username': string }
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}        
        // 
        $http({
            method: 'POST',
            url: server + '/user/resend_confirmation_code',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            // Handle successful
            console.log(result.data);
            $ionicPopup.alert({title: 'Signup', template: 'Confirmation code resent successfully! Please chek your email!'});
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Signup Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Signup Error', template: 'Server is down!'});
            }
            return;
        });       
    }
    
    $scope.submitCancel = function() {
        $state.go('signup');
    }    
    
}])
   
.controller('settingsCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {


}])
   
.controller('helpCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {


}])
   
.controller('registerDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'Devices', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, Devices, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),        
        'devicename': $scope.devicename
    };
    
    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };

    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicename=" + $scope.data.devicename);

        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: Register Device username is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device username is empty!");
            return;
        }
        else if ($scope.data.token.length === 0) {
            console.log("ERROR: Register Device token is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device token is empty!");
            return;
        }
        else if ($scope.data.devicename.trim().length === 0) {
            console.log("ERROR: Register Device devicename is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device devicename is empty!");
            return;
        }
        
        device_param = {
            'devicename': $scope.data.devicename
        };
        
        //        
        // ADD DEVICE
        // 
        // - Request:
        //   POST /devices/device
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/devices/device',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: device_param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            update_token(result);

            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'devicecert': result.data.device.cert,
                'devicepkey': result.data.device.pkey,
                'deviceca': result.data.device.ca
            };
            
            $ionicPopup.alert({
                title: 'Register Device',
                template: 'Device registered successfully!'
            });            
//            alert("Device registered successfully!");

            $state.go('viewDevice', device_param);
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Register Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Register Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        });         
    };
    
    $scope.submitDeviceList = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
}])
   
.controller('viewDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName


function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'deviceid': $stateParams.deviceid,
        'devicecert': $stateParams.devicecert,
        'devicepkey': $stateParams.devicepkey,
        'deviceca': $stateParams.deviceca
    };
    
    $scope.submitTest = function() {
        console.log("submitTest= " + $scope.data.devicename);
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        };
       
        $state.go('controlDevice', device_param);    
    };


    $scope.submitDelete = function() {
        $ionicPopup.alert({
            title: 'Delete Device',
            template: 'Are you sure you want to delete this device?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.submitDeleteAction();
                    }
                }
            ]            
        });            
    };
    
    $scope.submitDeleteAction = function() {
        console.log("submitDelete= " + $scope.data.devicename);
        
        var device_param = {
            'devicename': $scope.data.devicename
        };


        //
        // DELETE DEVICE
        //
        // - Request:
        //   DELETE /devices/device
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'DELETE',
            url: server + '/devices/device',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: device_param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            update_token(result);
            $state.go('menu.devices', device_param);                
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Delete Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Delete Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        });    
    };
    
    $scope.submitDeviceList = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
}])
   
.controller('controlDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': 'UNKNOWN'
    };

    $scope.submitEthernet = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'UNKNOWN') {
            return;
        }
        $state.go('deviceEthernet', $scope.data, {animate: false} );
    };

    $scope.submitGPIO = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'UNKNOWN') {
            return;
        }
        $state.go('deviceGPIO', $scope.data, {animate: false} );
    };   

    $scope.submitUART = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'UNKNOWN') {
            return;
        }
        $state.go('deviceUART', $scope.data, {animate: false} );
    };    

    $scope.submitRTC = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'UNKNOWN') {
            return;
        }
        $state.go('deviceRTC', $scope.data, {animate: false} );
    };    

    $scope.submitNotifications = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'UNKNOWN') {
            return;
        }
        $state.go('deviceNotifications', $scope.data, {animate: false} );
    };

    $scope.submitNotYetSupported = function() {
        if ($scope.data.devicestatus === 'UNKNOWN') {
            return;
        }
        $ionicPopup.alert({title: 'Error', template: 'Feature is not yet supported!'});
    };

    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                console.log("Before " + $scope.data.token.access);
                $scope.data.token = result.data.new_token;
                console.log("After " + $scope.data.token.access);
            }
        }    
    };
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            //alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            //alert("ERROR: Server is down!");
        }
    };    

    query_device = function(param) {
        $scope.data.devicestatus = 'Detecting...';
        //
        // GET STATUS
        // - Request:
        //   GET /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/status',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            
            $scope.data.devicestatus = 'RUNNING';
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.devicestatus = 'NOT RUNNING';
        }); 
    };   

    restart_device = function(param) {
        //
        // SET STATUS
        // - Request:
        //   POST /devices/device/status
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string, 'value': string }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/status',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $ionicPopup.alert({
                title: 'Device Status',
                template: 'Device was restarted successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };   
    
    $scope.submitRestart = function() {
        console.log("devicename=" + $scope.data.devicename);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        var param = {
            'devicename': $scope.data.devicename,
            'value': 'restart'
        };

        restart_device(param); 
    };
    
    $scope.submitStatus = function() {
        console.log("devicename=" + $scope.data.devicename);

        var param = {
            'devicename': $scope.data.devicename
        };

        query_device(param); 
    };
    
    $scope.submitView = function() {
        //console.log("username=" + $scope.data.username);
        //console.log("token=" + $scope.data.token);
        //console.log("devicename=" + $scope.data.devicename);

        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: View Device username is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: View Device username is empty!");
            return;
        }
        else if ($scope.data.token.length === 0) {
            console.log("ERROR: View Device token is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: View Device token is empty!");
            return;
        }
        else if ($scope.data.devicename.trim().length === 0) {
            console.log("ERROR: View Device devicename is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: View Device devicename is empty!");
            return;
        }


        //
        // GET DEVICE
        //
        // - Request:
        //   GET /devices/device/<devicename>
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey}}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            update_token(result);

            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'devicecert': result.data.device.cert,
                'devicepkey': result.data.device.pkey,
                'deviceca': result.data.device.ca
            };
            
            $state.go('viewDevice', device_param);
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Register Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Register Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        });         
    };  
 
    $scope.submitDeviceList = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
   
    $scope.submitStatus();
}])
   
.controller('deviceEthernetCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,

        'ipaddr': $scope.ipaddr,
        'subnet': $scope.subnet,
        'gateway': $scope.gateway,
        'macaddr': $scope.macaddr
    };
    
    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };

    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Server is down!");
        }
    };
    
    get_ip = function(param) {
        //
        // GET IP
        //
        // - Request:
        //   GET /devices/device/<devicename>/ip
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/' + 'ip',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $scope.data.ipaddr = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.ipaddr = 'Unknown';
        }); 
    };
    
    get_subnet = function(param) {
        //
        // GET SUBNET
        //
        // - Request:
        //   GET /devices/device/<devicename>/subnet
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/' + 'subnet',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $scope.data.subnet = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.subnet = 'Unknown';
        }); 
    };

    get_gateway = function(param) {
        //
        // GET GATEWAY
        //
        // - Request:
        //   GET /devices/device/<devicename>/gateway
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/' + 'gateway',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $scope.data.gateway = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.gateway = 'Unknown';
        }); 
    };

    get_mac = function(param) {
        //
        // GET MAC
        //
        // - Request:
        //   GET /devices/device/<devicename>/mac
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/' + 'mac',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $scope.data.macaddr = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.macaddr = 'Unknown';
        }); 
    };

    
    $scope.submit = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("ipaddr=" + $scope.data.ipaddr);
        console.log("subnet=" + $scope.data.subnet);
        console.log("gateway=" + $scope.data.gateway);
        console.log("macaddr=" + $scope.data.macaddr);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        var param = {
            'devicename': $scope.data.devicename,
        };
        
        // TODO Send REST API
        get_ip(param);
        get_subnet(param);
        get_gateway(param);
        get_mac(param);
    };

    $scope.submitDeviceList = function() {
        console.log("hello");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        };
        $state.go('controlDevice', device_param);
    };
    
}])
   
.controller('deviceGPIOCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        
        'gpionumber': $scope.gpionumber,
        'gpiovalue': $scope.gpiovalue,
        'gpiovalueset': $scope.gpiovalueset
    };

    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Server is down!");
        }
    };
    
    get_gpio = function(param) {
        // 
        // GET GPIO
        // 
        // - Request:
        //   GET /devices/device/<devicename>/gpio/<number>
        //   headers: {'Authorization': 'Bearer ' + token.access}
        // 
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/gpio/' + param.number,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            if (result.data.value === 1) {
                $scope.data.gpiovalue = "High";
                $scope.data.gpiovalueset = true;
            }
            else {
                $scope.data.gpiovalue = "Low";
                $scope.data.gpiovalueset = false;
            }
            
            $ionicPopup.alert({
                title: 'Device GPIO',
                template: 'GPIO was queried successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.gpiovalue = 'Unknown';
        }); 
    };

    set_gpio = function(param) {
        //        
        // SET GPIO
        //
        // - Request:
        //   POST /devices/device/gpio
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string, 'number': string, 'value': string }
        //
        // - Response:
        //  { 'status': 'OK', 'message': string, 'value': string }
        //  { 'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/gpio',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $ionicPopup.alert({
                title: 'Device GPIO',
                template: 'GPIO was set successfully!',
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    $scope.submitGet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("gpionumber=" + $scope.data.gpionumber);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        // Handle invalid input
        if ($scope.data.gpionumber === undefined) {
            console.log("ERROR: GPIO number is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: GPIO number is empty!");
            return;
        }

        var param = {
            'devicename': $scope.data.devicename,
            'number': $scope.data.gpionumber.toString()
        };

        get_gpio(param);
    };

    $scope.submitSet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("gpionumber=" + $scope.data.gpionumber);
        console.log("gpiovalueset=" + $scope.data.gpiovalueset);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        // Handle invalid input
        if ($scope.data.gpionumber === undefined) {
            console.log("ERROR: GPIO number is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: GPIO number is empty!");
            return;
        }

        gpiovalueset = 0;
        if ($scope.data.gpiovalueset == true) {
            gpiovalueset = 1;
        }
        var param = {
            'devicename': $scope.data.devicename,
            'number': $scope.data.gpionumber.toString(),
            'value': gpiovalueset.toString()
        };

        set_gpio(param);
    };
  
  
    $scope.submitDeviceList = function() {
        console.log("hello");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        };
        $state.go('controlDevice', device_param);
    };
  
}])
   
.controller('deviceUARTCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        
        'message': $scope.message
    };
    
    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };

    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Server is down!");
        }
    };
 
    set_uart = function(param) {
        //
        // SET UART
        //
        // - Request:
        //   POST /devices/device/uart
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string, 'value': string }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/uart',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $ionicPopup.alert({
                title: 'Device UART',
                template: 'Message was written to UART successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    $scope.submit = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("message=" + $scope.data.message);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        var param = {
            'devicename': $scope.data.devicename,
            'value': $scope.data.message
        };

        set_uart(param);
    };

    $scope.submitDeviceList = function() {
        console.log("hello");
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        };
        $state.go('controlDevice', device_param);
    };

}])
   
.controller('deviceRTCCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        
        'epoch': $scope.epoch,
        'datetime' : $scope.datetime,
        'datetimeset' : $scope.datetimeset
    };
    
    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };

    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Server is down!");
        }
    };
    
    get_rtc = function(param) {
        //
        // GET RTC
        //
        // - Request:
        //   GET /devices/device/<devicename>/rtc
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string }
        //   { 'status': 'NG', 'message': string}        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + param.devicename + '/rtc',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $scope.data.epoch = result.data.value;

            var myDate = new Date(result.data.value*1000);
            $scope.data.datetime = myDate.toLocaleString();

            $ionicPopup.alert({
                title: 'Device RTC',
                template: 'RTC was queried successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.epoch = 'Unknown';
            $scope.data.datetime = 'Unknown';
        }); 
    };
    
    set_rtc = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/devices/device/rtc',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $ionicPopup.alert({
                title: 'Device RTC',
                template: 'RTC was set successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    $scope.submitGet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("datetime=" + $scope.data.datetime);
        console.log("epoch=" + $scope.data.epoch);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }
        
        var param = {
            'devicename': $scope.data.devicename
        };

        get_rtc(param);
    };
    
    $scope.submitSet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("datetimeset=" + $scope.data.datetimeset);

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        var seconds = Math.round((new Date()).getTime() / 1000);
        console.log(seconds);
        
        var param = {
            'username': $scope.data.username,
            'devicename': $scope.data.devicename,
            'value': seconds
        };

        set_rtc(param);
    };  

    $scope.submitDeviceList = function() {
        console.log("hello");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        };
        $state.go('controlDevice', device_param);
    };
    
}])
   
.controller('deviceNotificationsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User) {

    var server = Server.rest_api;

    $scope.countrycodes = [
        {   "id": "China +86",          "code": "+86"   },
        {   "id": "India +91",          "code": "+91"   },
        {   "id": "Philippines +63",    "code": "+63"   },
        {   "id": "Singapore +65",      "code": "+65"   },
        {   "id": "Taiwan +886",        "code": "+886"  },
        {   "id": "United Kingdom +44", "code": "+44"   },
        {   "id": "United States +1",   "code": "+1"    },
        {   "id": "Vietnam +84",        "code": "+84"   },
    ];

    $scope.smsoptions = [
        {   "id": "AWS Pinpoint",       "code": "0"     },
        {   "id": "AWS SNS",            "code": "1"     },
        {   "id": "Twilio",             "code": "2"     },
        {   "id": "Nexmo",              "code": "3"     },
    ];


    $scope.data = {
        'username': $stateParams.username,
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        
        'recipient': "",
        'message': $scope.message,
        
        'activeSection' : 1,
        'emailaddress'  : $scope.emailaddress,
        'smsphonenumber': $scope.smsphonenumber,
        'smscountrycode': $scope.countrycodes[2].code,
        'smscountryid'  : $scope.countrycodes[2].id,
        'smsoptionsid': $scope.smsoptions[0].code,
    };


    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
    };

    update_token = function(result) {
        if (result !== null) {
            if (result.data.new_token !== undefined) {
                console.log("New Token exists!");
                User.set({
                    'username': $scope.data.username,
                    'token': result.data.new_token
                });
                $scope.data.token = result.data.new_token;
            }
        }    
    };
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
        }
        else {
            console.log("ERROR: Server is down!"); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Server is down!");
        }
    };    

    set_notifications = function(param) {
        //
        // SET NOTIFICATION
        //
        // - Request:
        //   POST /devices/device/notification
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'devicename': string, 'recipient': string, 'message': string, 'options': string }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/notification',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            update_token(result);
            $ionicPopup.alert({
                title: 'Device Notifications',
                template: 'Notifications was triggered successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    $scope.submit = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("message=" + $scope.data.message);
 

        if ($scope.data.devicestatus !== 'RUNNING') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is NOT RUNNING!'});
            return;
        }

        if ($scope.data.activeSection == 1) {
            // email
            console.log("emailaddress=" + $scope.data.emailaddress);
            $scope.data.recipient = $scope.data.emailaddress;
        }
        else {
            // sms
            console.log("smscountrycode=" + $scope.data.smscountrycode);
            console.log("smsphonenumber=" + $scope.data.smsphonenumber);
            $scope.data.recipient = $scope.data.smscountrycode + $scope.data.smsphonenumber;
            console.log("recipient=" + $scope.data.recipient);
            console.log("smsoptionsid=" + $scope.data.smsoptionsid);
        }


        if ($scope.data.activeSection == 1) {
            // email
            var param = {
                'devicename': $scope.data.devicename,
                'recipient': $scope.data.recipient,
                'message': $scope.data.message
            };
            set_notifications(param);      
        }
        else {
            // sms
            var param = {
                'devicename': $scope.data.devicename,
                'recipient': $scope.data.recipient,
                'message': $scope.data.message,
                'options': $scope.data.smsoptionsid // TESTING ONLY
            };
            set_notifications(param);      
        }
    };  
    
    $scope.submitDeviceList = function() {
        console.log("hello");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        };
        $state.go('controlDevice', device_param);
    };
    
}])
   
.controller('historyCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Devices', 'Histories', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Devices, Histories) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    }
    
    $scope.items_master = []; // items retrieved from database
    $scope.items = []; // items to be shown
/*    
        {
            "direction": "To",
            "deviceid" : "1234567890",
            "devicename": "ft900device1",
            "topic": "get_gpio",
            "payload": { "number": "10"},
            "datetime": "datetime"
        },
    ];
*/    
    
    $scope.devices = [ "All devices" ];
    $scope.deviceidx = 0;
    
    $scope.updateSelection = function(idx) {
        $scope.items = [];
        $scope.deviceidx = idx;
        
        console.log($scope.devices[$scope.deviceidx]);
        var i;
        
        if ($scope.deviceidx !== 0) {
            for (i=0; i<$scope.items_master.length; i++) {
                if ($scope.devices[$scope.deviceidx] === $scope.items_master[i].devicename) {
                    $scope.items.push($scope.items_master[i]);
                }
            }
        }
        else {
            $scope.items = $scope.items_master;        
        }
    };
    
    
    $scope.submitRefresh = function() {
    
        var user_data = {
            'token': User.get_token()        //$stateParams.token
        };
    
        Histories.fetch(user_data).then(function(res) {
            $scope.items_master = res;
            $scope.data.token = User.get_token();

            console.log(res);
            var i;
            for (i=0; i<res.length; i++) {
                var result = $scope.devices.includes(res[i].devicename);
                if (result === false) {
                    $scope.devices.push(res[i].devicename);
                }
            }
            console.log($scope.devices);
            
            $scope.updateSelection($scope.deviceidx);
        }); 
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("DEVICES enter ionicView REFRESH LIST");
        $scope.submitRefresh();
    });    
}])
 