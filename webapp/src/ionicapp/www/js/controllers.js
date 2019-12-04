angular.module('app.controllers', [])
  
.controller('homeCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {

}
])
   
.controller('devicesCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Devices', 'Token',     // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Devices, Token) {

    var server = Server.rest_api;

    $scope.devices = [];
    $scope.devices_counthdr = "No device registered" ;
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token()
    };

    $scope.submitTest = function(device) {

        console.log("devicename=" + device.devicename);
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': device.devicename,
            'deviceid': device.deviceid,
            'serialnumber': device.serialnumber
        };
       
        $state.go('configureDevice', device_param );
    };
    
    $scope.submitAdd = function() {

        $state.go('addDevice', $scope.data);
    };
    
    $scope.submitRefresh = function(livestatus) {

        console.log("refresh");
        
        // Fetch devices
        Devices.fetch($scope.data).then(function(res) {
            $scope.devices = res;
            $scope.data.token = User.get_token();
            if ($scope.devices.length !== 0) {
                $scope.devices_counthdr = $scope.devices.length.toString() + " devices registered";
                
                if (livestatus === true) {
                    console.log($scope.devices.length);
                    var indexy = 0;
                    for (indexy=0; indexy<$scope.devices.length; indexy++) {
                        console.log("indexy=" + indexy.toString() + " " + $scope.devices[indexy].devicename);
                        if ($scope.devices[indexy].devicestatus === undefined) {
                            $scope.devices[indexy].devicestatus = "Detecting...";
                        }
                        query_device(indexy, $scope.devices[indexy].devicename);
                    }
                }
                else {
                    var indexy = 0;
                    for (indexy=0; indexy<$scope.devices.length; indexy++) {
                        if ($scope.devices[indexy].heartbeat !== undefined) {
                            var heartbeat = new Date($scope.devices[indexy].heartbeat * 1000);
                            $scope.devices[indexy].devicestatus = "Last active: " + heartbeat;
                        }
                        else {
                            $scope.devices[indexy].devicestatus = "Last active: N/A";
                        }
                    }
                }
            }
            else {
                $scope.devices_counthdr = "No device registered";
            }
        });
    };
    
    query_device = function(index, devicename) {
        //
        // GET STATUS
        // - Request:
        //   GET /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { "status": string, "version": string } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + devicename + '/status',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            console.log(devicename + ": Online");
            $scope.devices[index].devicestatus = 'Online';    
        })
        .catch(function (error) {
            console.log(devicename + ": Offline");
            $scope.devices[index].devicestatus = 'Offline';
            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
        }); 
    };    
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Get/Delete Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
                $ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };    
    

    $scope.$on('$ionicView.enter', function(e) {
        //console.log("DEVICES enter ionicView REFRESH LIST");
        $scope.submitRefresh(false);
    });
    
    
    $scope.getStyle = function(devicestatus) {
        //console.log("getStyle " + devicestatus);
        if (devicestatus === "Online") {
            return 'item-online';
        }
        else if (devicestatus === "Offline") {
            return 'item-offline';
        }
        else if (devicestatus === "Detecting...") {
            return 'item-detecting';
        }
        return 'item-lastactive';
    };

}])
   
.controller('accountCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': "", //User.get_username(),
        'token': "",//User.get_token(),

        'fullname': 'Unknown',
        'email': 'Unknown',
        'phonenumber': 'Unknown',

        'subscription_type': 'Unknown',
        'subscription_credits': 'Unknown',
        
        'activeSection': 1,
    };

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
    };
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            
            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };

    get_subscription = function() {
        //
        // GET SUBSCRIPTION
        //
        // - Request:
        //   GET /account/subscription
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'GET',
            url: server + '/account/subscription',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log("get_subscription");
            console.log(result.data);

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
        //   {'status': 'OK', 'message': string, 'info': {'email': string, 'phone_number': string, 'name': string} }
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
            $scope.data.fullname = result.data.info.name;
            $scope.data.email = result.data.info.email;
            if (result.data.info.phone_number !== undefined) {
                $scope.data.phonenumber = result.data.info.phone_number;
            }
            else {
                $scope.data.phonenumber = "Unknown";
            }
            if (result.data.info.phone_number_verified !== undefined) {
                if (result.data.info.phone_number_verified === false) {
                    $scope.data.phonenumber +=  " (Unverified)";
                }
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    delete_account = function() {
        //
        // DELETE USER
        //
        // - Request:
        //   DELETE /user
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'DELETE',
            url: server + '/user',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.status === "OK") {
                $state.go('login');
            }
        })
        .catch(function (error) {
            handle_error(error);
        });        
    };
    

    $scope.$on('$ionicView.enter', function(e) {

        $scope.data.username = User.get_username();
        $scope.data.token = User.get_token();

        console.log("ACCOUNT ionicView get_profile");
        get_profile({
            'username': $scope.data.username,
            'token': $scope.data.token
        });


        if (($scope.data.username === "") || ($scope.data.username === undefined)) {

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


//    console.log("ACCOUNT get_profile");
//    get_profile();

//    console.log("ACCOUNT get_subscription");
//    get_subscription();


    $scope.submitBuycredits = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
     
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('order', device_param, {reload: true});   
    };
    
    $scope.submitDeleteaccount = function() {
        $ionicPopup.alert({
            title: 'Delete Account',
            template: 'Are you sure you want to delete your account?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.submitDeleteaccountAction();
                    }
                }
            ]            
        });            
    };    
    

    $scope.submitVerifynumber = function() {
        console.log("submitVerifynumber");

        // Handle invalid input        
        if ($scope.data.username === undefined) {
            $ionicPopup.alert({title: 'Verify Number Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Verify Number Error', template: 'Username is empty!'});
            return;
        }

        
        // 
        // VERIFY PHONE NUMBER
        // 
        // - Request:
        //   POST /user/verify_phone_number
        //   headers: {'Authorization': 'Bearer ' + token.access}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'POST',
            url: server + '/user/verify_phone_number',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $state.go('confirmPhoneNumber', {'username': $scope.data.username, 'token': $scope.data.token});
        })
        .catch(function (error) {
            handle_error(error);
        });
    };
    
    $scope.submitSavechanges = function() {
        console.log("submitSavechanges");
        
        // Handle invalid input
        if ($scope.data.username === undefined) {
            $ionicPopup.alert({title: 'Save Changes Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Save Changes Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.fullname === undefined) {
            $ionicPopup.alert({title: 'Save Changes Error', template: 'Name is empty!'});
            return;
        }
        else if ($scope.data.fullname.length === 0) {
            $ionicPopup.alert({title: 'Save Changes Error', template: 'Name is empty!'});
            return;
        }
        else if ($scope.data.phonenumber === undefined) {
            $ionicPopup.alert({title: 'Save Changes Error', template: 'Phone Number is empty!'});
            return;
        }
        else if ($scope.data.phonenumber.length === 0) {
            $ionicPopup.alert({title: 'Save Changes Error', template: 'Phone Number is empty!'});
            return;
        }
        else if ($scope.data.phonenumber === "Unknown") {
            $scope.data.phonenumber = "";
        }
        
        
        var param = { 'name': $scope.data.fullname };
        if ($scope.data.phonenumber.length > 0) {
            param.phone_number = $scope.data.phonenumber.split(" ")[0];   
        }
        
        // 
        // UPDATE USER INFO
        // 
        // - Request:
        //   POST /user
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: {'name': string, 'phone_number': string}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'POST',
            url: server + '/user',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Success',
                template: 'User profile changed successfully!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            get_profile({
                                'username': $scope.data.username,
                                'token': $scope.data.token
                            });
                        }
                    }
                ]
            });
        })
        .catch(function (error) {
            handle_error(error);
        });        
    };

    $scope.submitChangepassword = function() {
        console.log("submitChangepassword");
        $state.go('changePassword', {'username': $scope.data.username, 'token': $scope.data.token});
    };

    $scope.submitDeleteaccountAction = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        
        delete_account(); 
    };
}
])
   
.controller('orderCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

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
            'return_url': return_url,
            'cancel_url': cancel_url,
            'item_sku': $scope.data.id,
            'item_credits': $scope.data.points,
            'item_price': $scope.data.price,
        };


        //       
        // PAYPAL SETUP
        //
        // - Request:
        //   POST /account/payment/paypalsetup
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'approval_url': string, 'paymentId': string, 'token': string}
        //   {'status': 'NG', 'message': string}    
        //
        $http({
            method: 'POST',
            url: server + '/account/payment/paypalsetup',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param
        })
        .then(function (result) {
            console.log(result.data);
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
            if (error.data !== null) {
                console.log("ERROR: Paypal Setup failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Paypal Setup failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
                
                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
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
        //   GET /account/subscription
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'GET',
            url: server + '/account/subscription',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log("get_subscription");
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Payment Confirmation',
                template: 'Payment transaction was successful. Your new credit balance is ' + result.data.subscription.credits + '.',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            param = {
                                'username': $scope.data.username,
                                'token': $scope.data.token
                            };
                            $state.go('menu.account', param, {reload: true});   
                        }
                    }
                ]
            });
        })
        .catch(function (error) {
            if (error.data !== null) {
                console.log("ERROR: Get Subscription failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Get Subscription failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
                
                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
        }); 
    };

    verifyPayment = function(paypal_param) {
        //
        // PAYPAL VERIFY
        //
        // - Request:
        //   POST /account/payment/paypalverify
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'paymentId': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        console.log("paypalverify");
        console.log(paypal_param.payment);
        $http({
            method: 'POST',
            url: server + '/account/payment/paypalverify',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param.payment
        })
        .then(function (result) {
            console.log(result.data);
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
                
                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
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
        //   POST /account/subscription
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
            url: server + '/account/subscription',
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
        //   POST /account/payment/paypalverify
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'paymentId': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //        
        console.log("paypalverify");
        console.log(paypal_param.payment);
        $http({
            method: 'POST',
            url: server + '/account/payment/paypalverify',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param.payment
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
        //   POST /account/payment/paypalexecute
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'paymentId': string, 'payerId': string, 'token': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        console.log("paypalexecute");
        console.log(paypal_param);
        $http({
            method: 'POST',
            url: server + '/account/payment/paypalexecute',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: paypal_param.payment
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
    };

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
        
        
    };
    
    $scope.submitLogoutAction = function() {
        $scope.data.username = "";        
        $scope.data.token = "";        
        User.clear();
        $state.go('login');
    };
    
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
    };
    
    base64Encode = function(str) {
        return window.btoa(str);
    };
    
    urlEncode = function(str) {
        return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
    };

    jwtEncode = function(username, password) {

        // get time
        // https://www.epochconverter.com/
        iat = Math.floor(Date.now() / 1000); // epoch time in seconds
        exp = iat + 10; // plus 10 seconds
        console.log(iat);
        console.log(exp);

        // get JWT header
        headerData = JSON.stringify({ 
            "alg": "HS256", 
            "typ": "JWT"
        });

        // get JWT payload
        payloadData = JSON.stringify({
            "username": username,
            "password": password,
            "iat": iat,
            "exp": exp
        });

        // get JWT = header.payload.signature
        // https://jwt.io/
        secret = window.__env.jwtKey;
        header = urlEncode(base64Encode(headerData));
        payload = urlEncode(base64Encode(payloadData));
        signature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(header + "." + payload, secret)));

        jwt = header + "." + payload + "." + signature;
        return jwt;
    };
    
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


        console.log("login: " + $scope.data.username);

        // 
        // LOGIN
        // 
        // - Request:
        //   POST /user/login
        //   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password)}
        // 
        // - Response:
        //   {'status': 'OK', 'token': {'access': string, 'id': string, 'refresh': string} }
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/login',
            headers: {'Authorization': 'Bearer ' + jwtEncode($scope.data.username, $scope.data.password)},
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            console.log("login: OK " + new Date().getTime());
            // Handle successful
            console.log(result.data);

            var user_data = {
                'username': $scope.data.username,
                'token': result.data.token
            };
            
            User.set(user_data);
        
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };
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
        'name'        : $scope.name,
        'phonenumber' : $scope.phonenumber,
        'email'       : $scope.email,
    };
    
    base64Encode = function(str) {
        return window.btoa(str);
    };
    
    urlEncode = function(str) {
        return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
    };

    jwtEncode = function(username, password) {

        // get time
        // https://www.epochconverter.com/
        iat = Math.floor(Date.now() / 1000); // epoch time in seconds
        exp = iat + 10; // plus 10 seconds
        console.log(iat);
        console.log(exp);

        // get JWT header
        headerData = JSON.stringify({ 
            "alg": "HS256", 
            "typ": "JWT"
        });

        // get JWT payload
        payloadData = JSON.stringify({
            "username": username,
            "password": password,
            "iat": iat,
            "exp": exp
        });

        // get JWT = header.payload.signature
        // https://jwt.io/
        secret = window.__env.jwtKey;
        header = urlEncode(base64Encode(headerData));
        payload = urlEncode(base64Encode(payloadData));
        signature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(header + "." + payload, secret)));

        jwt = header + "." + payload + "." + signature;
        return jwt;
    };
    
    $scope.submit = function() {
        
        // Handle invalid input
        if ($scope.data.password.length === 0) {
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
        else if ($scope.data.name === undefined) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Name is invalid!'});
            return;
        }
        else if ($scope.data.name.length === 0) {
            $ionicPopup.alert({title: 'Signup Error', template: 'Name is empty!'});
            return;
        }

        
        // Display spinner
        var spinner = document.getElementsByClassName("spinner3");
        spinner[0].style.visibility = "visible";

 
        console.log(name);

        param = {
            'name': $scope.data.name,
            'email': $scope.data.email,
        };
        
        if ($scope.data.phonenumber !== undefined) {
            if ($scope.data.phonenumber.length !== 0) {
                param.phone_number = $scope.data.phonenumber;
            }
        }        
        
        $scope.data.username = $scope.data.email;
        
        
        console.log("signup: " + $scope.data.username);
        
        // 
        // SIGN-UP
        // 
        // - Request:
        //   POST /user/signup
        //   headers: {'Authorization': 'Bearer ' + jwtEncode(email, password), 'Content-Type': 'application/json'}
        //   data: { 'email': string, 'phone_number': string, 'name': string }
        //   // password should at least be 6 characters
        //   // phone_number is optional
        //   // phone_number should start with + followed by country code then number
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/signup',
            headers: {'Authorization': 'Bearer ' + jwtEncode($scope.data.username, $scope.data.password), 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            // Handle successful login
            console.log(result.data);
        
            $scope.data = {
                'username': $scope.data.username,
            };
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
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            return;
        });       
    };
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
            };
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
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            return;
        });
    };
    
    $scope.submitCancel = function() {
        $state.go('login');
    };   
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
    };
    
    base64Encode = function(str) {
        return window.btoa(str);
    };
    
    urlEncode = function(str) {
        return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
    };

    jwtEncode = function(username, password) {

        // get time
        // https://www.epochconverter.com/
        iat = Math.floor(Date.now() / 1000); // epoch time in seconds
        exp = iat + 10; // plus 10 seconds
        console.log(iat);
        console.log(exp);

        // get JWT header
        headerData = JSON.stringify({ 
            "alg": "HS256", 
            "typ": "JWT"
        });

        // get JWT payload
        payloadData = JSON.stringify({
            "username": username,
            "password": password,
            "iat": iat,
            "exp": exp
        });

        // get JWT = header.payload.signature
        // https://jwt.io/
        secret = window.__env.jwtKey;
        header = urlEncode(base64Encode(headerData));
        payload = urlEncode(base64Encode(payloadData));
        signature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(header + "." + payload, secret)));

        jwt = header + "." + payload + "." + signature;
        return jwt;
    };
    
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
        

        param = {
            'confirmationcode': $scope.data.confirmationcode,
        };


        console.log("confirm_forgot_password: " + $scope.data.username);

        //
        // CONFIRM FORGOT PASSWORD
        //
        // - Request:
        //   POST /user/confirm_forgot_password
        //   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password), 'Content-Type': 'application/json'}
        //   data: { 'confirmationcode': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/confirm_forgot_password',
            headers: {'Authorization': 'Bearer ' + jwtEncode($scope.data.username, $scope.data.password), 'Content-Type': 'application/json'},
            data: param
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
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            return;
        });
    };
    
    $scope.submitCancel = function() {
        $state.go('recover');
    };   
    
}])
   
.controller('changePasswordCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        
        'password': "",
        'newpassword': "",
        'newpassword2': ""
    };
    
    
    base64Encode = function(str) {
        return window.btoa(str);
    };
    
    urlEncode = function(str) {
        return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
    };

    jwtEncode = function(password, newpassword) {

        // get time
        // https://www.epochconverter.com/
        iat = Math.floor(Date.now() / 1000); // epoch time in seconds
        exp = iat + 10; // plus 10 seconds
        console.log(iat);
        console.log(exp);

        // get JWT header
        headerData = JSON.stringify({ 
            "alg": "HS256", 
            "typ": "JWT"
        });

        // get JWT payload
        payloadData = JSON.stringify({
            "username": password,
            "password": newpassword,
            "iat": iat,
            "exp": exp
        });

        // get JWT = header.payload.signature
        // https://jwt.io/
        secret = window.__env.jwtKey;
        header = urlEncode(base64Encode(headerData));
        payload = urlEncode(base64Encode(payloadData));
        signature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(header + "." + payload, secret)));

        jwt = header + "." + payload + "." + signature;
        return jwt;
    };    
    
    $scope.submit = function() {
        
        if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.password === undefined) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.password.length === 0) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.newpassword === undefined) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'New Password is empty!'});
            return;
        }
        else if ($scope.data.newpassword.length === 0) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'New Password is empty!'});
            return;
        }
        else if ($scope.data.newpassword.length < 6) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Password should at least be 6 characters!'});
            return;
        }
        else if ($scope.data.newpassword2 === undefined) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Confirm New Password is empty!'});
            return;
        }
        else if ($scope.data.newpassword2.length === 0) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Confirm New Password is empty!'});
            return;
        }
        else if ($scope.data.newpassword !== $scope.data.newpassword2) {
            $ionicPopup.alert({title: 'Change Password Error', template: 'Passwords do not match!'});
            return;
        }

        console.log("change password: " + $scope.data.username);


        // 
        // CHANGE PASSWORD
        // 
        // - Request:
        //   POST /user/change_password
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: {'token': jwtEncode(password, newpassword)}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/change_password',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: { 'token': jwtEncode($scope.data.password, $scope.data.newpassword) }
        })
        .then(function (result) {
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Success',
                template: 'Password changed successfully!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            User.clear();
                            $state.go('login');
                        }
                    }
                ]
            });
        })
        .catch(function (error) {
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Change Password Error', template: error.data.message});
            }
            else {
               $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };
    
    $scope.submitCancel = function() {
        $state.go('menu.account', {'username': $scope.data.username, 'token': $scope.data.token} );
    };
}])
   
.controller('confirmRegistrationCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'confirmationcode': $scope.confirmationcode
    };
    
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
            $ionicPopup.alert({title: 'Signup', template: 'Your account has been registered successfully!'});
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
    };
    
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
        };


        // 
        // CONFIRM REGISTRATION
        // 
        // - Request:
        //   POST /user/confirm_signup
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}        
        // 
        $http({
            method: 'POST',
            url: server + '/user/confirm_signup',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            // Handle successful
            console.log(result.data);
            $ionicPopup.alert({title: 'Confirm signup', template: 'Confirmation code resent successfully! Please chek your email!'});
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Confirm signup Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            return;
        });       
    };
    
    $scope.submitCancel = function() {
        $state.go('signup');
    };
    
}])
   
.controller('confirmPhoneNumberCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        
        'confirmationcode': ''
    };


    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("confirmationcode=" + $scope.data.confirmationcode);
        
        if ($scope.data.confirmationcode === undefined) {
            $ionicPopup.alert({title: 'Verify Phone Number Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode.length === 0) {
            $ionicPopup.alert({title: 'Verify Phone Number Error', template: 'Code is empty!'});
            return;
        }


        //
        // CONFIRM VERIFY PHONE NUMBER
        //
        // - Request:
        //   POST /user/confirm_verify_phone_number
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: {'confirmationcode': string}
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/confirm_verify_phone_number',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: { 'confirmationcode': $scope.data.confirmationcode }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({title: 'Verify phone number', template: 'Your phone number has been verified successfully!'});
            $state.go('menu.account', {'username': $scope.data.username, 'token': $scope.data.token} );
        })
        .catch(function (error) {
            console.log(error);
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Verify phone number', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'Verify phone number', template: 'Server is down!'});
            }
            return;
        });       
    };
    
    $scope.submitResend = function() {
        console.log("submitVerifynumber");
        
        
        // 
        // VERIFY PHONE NUMBER
        // 
        // - Request:
        //   POST /user/verify_phone_number
        //   headers: {'Authorization': 'Bearer ' + token.access}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'POST',
            url: server + '/user/verify_phone_number',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $state.go('confirmPhoneNumber', {'username': $scope.data.username, 'token': $scope.data.token});
        })
        .catch(function (error) {
            console.log(error);
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'Verify phone number', template: error.data.message});
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            return;
        });      
    };    
    
    $scope.submitCancel = function() {
        $state.go('menu.account', {'username': $scope.data.username, 'token': $scope.data.token} );
    };
}])
   
.controller('aboutCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    };
    
    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }            
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };
    
    
    // GET TERMS AND CONDITIONS
    $scope.getTermsAndConditions = function() {
        console.log("getTermsAndConditions");
        get_item("terms");
    };

    // GET PRIVACY STATEMENTS
    $scope.getPrivacyStatements = function() {
        console.log("getPrivacyStatements");
        get_item("privacy");
    };

    // GET LICENSE
    $scope.getLicense = function() {
        console.log("getLicense");
        get_item("license");
    };


    get_item = function(item) {
        console.log(item);
        //
        // GET FAQS/TERMS AND CONDITIONS/PRIVACY STATEMENTS/LICENSE
        //
        // - Request:
        //   GET /others/ITEM
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'ITEM': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/others/' + item,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({ title: 'Success', template: result.data[item],
                buttons: [{ text: "OK", type: 'button-positive' }]
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
}])
   
.controller('feedbackCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token(),        //$stateParams.token
        
        'feedback': {
            'feedback': '',
            'rating': 10,
            'contactme': false
        }
    };

    $scope.changeSection = function(s) {
        $scope.data.feedback.rating = s;
        console.log($scope.data.feedback.rating);
    };

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }            
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };
    
    
    // GET TERMS AND CONDITIONS
    $scope.sendFeedback = function() {
        if ($scope.data.feedback.feedback === undefined) {
            $ionicPopup.alert({title: 'Input error', template: 'Feedback is empty'});
            return;    
        }
        if ($scope.data.feedback.feedback.length === 0) {
            $ionicPopup.alert({title: 'Input error', template: 'Feedback is empty'});
            return;    
        }        
        console.log("sendFeedback");
        send_feedback();
    };


    send_feedback = function() {
        //
        // SEND FEEDBACK
        //
        // - Request:
        //   POST /others/feedback
        //   headers: headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'feedback': string, 'rating': int, 'contactme': boolean, 'recipient': string }
        //   // recipient is temporary for testing purposes only
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'POST',
            url: server + '/others/feedback',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: $scope.data.feedback
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({ title: 'Success', template: "Thank you for sending feedback!",
                buttons: [{ text: "OK", type: 'button-positive' }]
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
}])
   
.controller('helpSupportCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    };
    
    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }            
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };
    
    
    // GET TERMS AND CONDITIONS
    $scope.getFAQs = function() {
        console.log("getFAQs");
        get_item("faqs");
    };


    get_item = function(item) {
        console.log(item);
        //
        // GET FAQS/TERMS AND CONDITIONS/PRIVACY STATEMENTS/LICENSE
        //
        // - Request:
        //   GET /others/ITEM
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'ITEM': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/others/' + item,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({ title: 'Success', template: result.data[item],
                buttons: [{ text: "OK", type: 'button-positive' }]
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
}])
   
.controller('addDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'Devices', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, Devices, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),

        'devicename': "",
        'uuid': "",
        'serialnumber': "",
    };

    $scope.generate = function() {
        uuid = "PH80XXRRMMDDYYSS";
        serialnumber = "SSSSS";
        
        var today = new Date();
        month = today.getMonth() + 1;
        day = today.getDate();
        year = today.getFullYear() - 2000;
        month = ("0" + month).slice(-2);
        day = ("0" + day).slice(-2);
        year = ("0" + year).slice(-2);
        
        random = Math.floor(Math.random() * 256); // 0-255
        serialnumber = random.toString();
        serialnumber = ("0000" + serialnumber).slice(-5);
        
        random = random.toString(16);
        random = ("0" + random).slice(-2);
        
        uuid = uuid.replace("MM", month.toString());
        uuid = uuid.replace("DD", day.toString());
        uuid = uuid.replace("YY", year.toString());
        uuid = uuid.replace("SS", random.toString());
        uuid = uuid.toUpperCase();
        
        $scope.data.uuid = uuid;
        $scope.data.serialnumber = serialnumber;
        
        console.log(uuid);
        console.log(serialnumber);
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
        else if ($scope.data.uuid === undefined) {
            console.log("ERROR: Register Device UUID is undefined!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device UUID is undefined!");
            return;
        }
        else if ($scope.data.uuid.trim().length === 0) {
            console.log("ERROR: Register Device UUID is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device UUID is empty!");
            return;
        }
        else if ($scope.data.serialnumber === undefined) {
            console.log("ERROR: Register Device serial number is undefined!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device serial number is undefined!");
            return;
        }
        else if ($scope.data.serialnumber.trim().length === 0) {
            console.log("ERROR: Register Device serial number is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device serial number is empty!");
            return;
        }
        else if ($scope.data.devicename === undefined) {
            console.log("ERROR: Register Device devicename is undefined!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device devicename is undefined!");
            return;
        }
        else if ($scope.data.devicename.trim().length === 0) {
            console.log("ERROR: Register Device devicename is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register Device devicename is empty!");
            return;
        }
        
       
        param = {
            'deviceid': $scope.data.uuid,
            'serialnumber': $scope.data.serialnumber,
        };

        //
        // ADD DEVICE
        // 
        // - Request:
        //   POST /devices/device/<devicename>
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: {'deviceid': string, 'serialnumber': string}
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Success',
                template: 'Device added successfully!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            $state.go('menu.devices', {'username': $scope.data.username, 'token': $scope.data.token});
                        }
                    }
                ]
            });
        })
        .catch(function (error) {
            if (error.data !== null) {
                console.log("ERROR: Register Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

                if (error.status == 409) {
                    $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                else {
                    $ionicPopup.alert({ title: 'Error', template: 'Failed to add device!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }

                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
            }
            else {
                console.log("ERROR: Server is down!"); 
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{ text: 'OK', type: 'button-assertive' }] });
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
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter");
        $scope.data.uuid = "";
        $scope.data.serialnumber = "";
        $scope.data.devicename = "";
    });    
    
}])
   
.controller('viewDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName


function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'timestamp'   : $stateParams.timestamp,
        'heartbeat'   : $stateParams.heartbeat,
    };



    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!");
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    }; 


    // GET STATUS
    $scope.getDevice = function() {
        get_status();
    };

    get_status = function() {
        //
        // GET STATUS
        // - Request:
        //   GET /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { "status": string, "version": string } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/status',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({
                title: 'Device Status',
                template: 'Device is online - ' + result.data.value.status  + '!',
            });              
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    }; 
    
    
    // RESTART DEVICE/START DEVICE/STOP DEVICE
    $scope.setDevice = function(status) {
        console.log("devicename=" + $scope.data.devicename);

        set_status({ 'value': status }); 
    };
    
    set_status = function(param) {
        //
        // SET STATUS for RESTART DEVICE/START DEVICE/STOP DEVICE
        // - Request:
        //   POST /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'value': string }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/status',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device Status',
                template: 'Device is now ' + result.data.value  + '!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    
    // CONFIGURE DEVICE
    $scope.configureDevice = function() {
        console.log("configureDevice= " + $scope.data.devicename);
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber
        };
       
        $state.go('configureDevice', device_param);    
    };


    // DELETE DEVICE
    $scope.deleteDevice = function() {
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
                        $scope.deleteDeviceAction();
                    }
                }
            ]            
        });            
    };
    
    $scope.deleteDeviceAction = function() {
        console.log("deleteDeviceAction= " + $scope.data.devicename);
        
        //
        // DELETE DEVICE
        //
        // - Request:
        //   DELETE /devices/device/<devicename>
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $state.go('menu.devices', {'username': $scope.data.username, 'token': $scope.data.token});
        })
        .catch(function (error) {
            handle_error(error);
        });    
    };
    
    
    // EXIT PAGE
    $scope.exitPage = function() {
        var device_param = {
            'username': $scope.data.username,
            'token'   : $scope.data.token
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
}])
   
.controller('configureDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'devicestatus': 'Status: UNKNOWN',
        'deviceversion': 'UNKNOWN'
    };

    $scope.submitGPIO = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'Status: UNKNOWN') {
            return;
        }
        $state.go('deviceGPIO', $scope.data, {animate: false} );
    };   

    $scope.submitUART = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'Status: UNKNOWN') {
            return;
        }
        $state.go('deviceUART', $scope.data, {animate: false} );
    };    

    $scope.submitI2C = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'Status: UNKNOWN') {
            return;
        }
        $state.go('deviceI2C', $scope.data, {animate: false} );
    };    

    $scope.submitNotifications = function() {
        console.log("devicename=" + $scope.data.devicename);
        if ($scope.data.devicestatus === 'Status: UNKNOWN') {
            return;
        }
        $state.go('deviceNotifications', $scope.data, {animate: false} );
    };


    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                var heartbeat = new Date(error.data.heartbeat * 1000);
                $scope.data.devicestatus = "Last active: " + heartbeat;                
            }
            else {
                $scope.data.devicestatus = "Status: UNKNOWN";                
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };    


    // GET STATUS
    $scope.getStatus = function() {
        get_status();
    };

    get_status = function() {
        $scope.data.devicestatus = 'Status: Detecting...';
        //
        // GET STATUS
        // - Request:
        //   GET /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { "status": string, "version": string } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/status',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.devicestatus = 'Status: Online';
            $scope.data.deviceversion = result.data.value.version;
        })
        .catch(function (error) {
            handle_error(error);
            //$scope.data.devicestatus = 'Offline';
            $scope.data.deviceversion = 'UNKNOWN';
        }); 
    };   


    // GET DEVICE
    $scope.getDevice = function() {
        get_device();
    };  
    
    get_device = function() {
        //
        // GET DEVICE
        //
        // - Request:
        //   GET /devices/device/<devicename>
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'addI2CDeviceDetails': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey}}
        //   {'status': 'NG', 'message': string}
        //   
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);

            var timestamp = new Date(result.data.device.timestamp* 1000);
            var heartbeat = null;
            if (result.data.device.heartbeat !== undefined) {
                heartbeat = new Date(result.data.device.heartbeat* 1000);
            }
            else {
                heartbeat = "N/A";
            }
            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'serialnumber': result.data.device.serialnumber,
                'timestamp': timestamp,
                'heartbeat': heartbeat,
            };
            
            $state.go('viewDevice', device_param);
        })
        .catch(function (error) {
            handle_error(error);
        });         
    };


    // EXIT PAGE
    $scope.exitPage = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
   
    $scope.getStatus();
}])
   
.controller('deviceEthernetCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,

        'ipaddr': $scope.ipaddr,
        'subnet': $scope.subnet,
        'gateway': $scope.gateway,
        'macaddr': $scope.macaddr
    };
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            
            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
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

        if ($scope.data.devicestatus !== 'Online') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is offline!'});
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
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('configureDevice', device_param);
    };
    
}])
   
.controller('deviceGPIOCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.voltages = [
        { "id":0,  "label": "3.3 V"       },
        { "id":1,  "label": "5 V"         },
    ];

    $scope.directions = [
        { "id":0,  "label": "Input"       },
        { "id":1,  "label": "Output"      },
    ];

    $scope.modes_input = [
        { "id":0,  "label": "High Level"  },
        { "id":1,  "label": "Low Level"   },
        { "id":2,  "label": "High Edge"   },
        { "id":3,  "label": "Low Edge"    },
    ];

    $scope.modes_output = [
        { "id":0,  "label": "Level"       },
        { "id":1,  "label": "Pulse"       },
        { "id":2,  "label": "Clock"       },
    ];

    $scope.modes = $scope.modes_input;

    $scope.polarities = [
        { "id":0,  "label": "Positive"     },
        { "id":1,  "label": "Negative"     },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];
    
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,

        'activeSection': 1,
        'showNotification': 0,
        'voltageidx': $scope.voltages[0].id,

        'gpio': {
            'direction'   : $scope.directions[0].id,
            'mode'        : $scope.modes[0].id,
            'alert'       : $scope.alerts[0].id,
            'alertperiod' : 60,
            'polarity'    : $scope.polarities[0].id,
            'width'       : 1,
            'mark'        : 1,
            'space'       : 1,
        
            'notification': {
                'messages': [ 
                    { 'message': 'Hello World!', 'enable': true },
                    { 'message': 'Hi World!', 'enable': false },
                ],
                'endpoints' : {
                    'mobile': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'email': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'notification': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'modem': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'storage': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                }
            }
        },        
        
    };

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
        $scope.submitQuery();
    };

    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
    };


    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503 && showerror === true ) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }            
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };
    
   
    get_gpio_properties = function() {
        //
        // GET GPIO PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/gpio/<number>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      'direction': int,
        //      'mode': int,
        //      'alert': int,
        //      'alertperiod': int,
        //      'polarity': int,
        //      'width': int,
        //      'mark': int,
        //      'space': int,
        //      'notification': {
        //          'messages': [{ 'message': string, 'enable': boolean }, { 'message': string, 'enable': boolean }],
        //          'endpoints' : {
        //              'mobile': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': string, 'group': boolean}, ],
        //              },
        //              'email': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'notification': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'modem': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'storage': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //          }
        //      }
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/' + $scope.data.activeSection.toString() + '/properties',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);

            if (result.data.value.notification !== undefined) {
                $scope.data.gpio = result.data.value; 
            }
            else {
                $scope.data.gpio.direction   = result.data.value.direction;
                $scope.data.gpio.mode        = result.data.value.mode;
                $scope.data.gpio.alert       = result.data.value.alert;
                $scope.data.gpio.alertperiod = result.data.value.alertperiod;
                $scope.data.gpio.polarity    = result.data.value.polarity;
                $scope.data.gpio.width       = result.data.value.width;
                $scope.data.gpio.mark        = result.data.value.mark;
                $scope.data.gpio.space       = result.data.value.space;
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    set_gpio_properties = function() {
        //
        // SET GPIO PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/gpio/<number>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'direction': int,
        //      'mode': int,
        //      'alert': int,
        //      'alertperiod': int,
        //      'polarity': int,
        //      'width': int,
        //      'mark': int,
        //      'space': int,
        //      'notification': {
        //          'messages': [{ 'message': string, 'enable': boolean }, { 'message': string, 'enable': boolean }],
        //          'endpoints' : {
        //              'mobile': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': string, 'group': boolean}, ],
        //              },
        //              'email': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'notification': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'modem': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'storage': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //          }
        //      }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/' + $scope.data.activeSection.toString() + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.gpio
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'Device GPIO',
                template: 'GPIO ' + $scope.data.activeSection.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    

    get_gpio_voltage = function() {
        //
        // GET GPIO VOLTAGE
        //
        // - Request:
        //   GET /devices/device/<devicename>/gpio/voltage
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/voltage',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.voltageidx = result.data.value.voltage;
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };


    set_gpio_voltage = function() {
        //
        // SET GPIO VOLTAGE
        //
        // - Request:
        //   POST /devices/device/<devicename>/gpio/voltage
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: { 'voltage': int }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/voltage',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'voltage': $scope.data.voltageidx }
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };

    
/*    
    get_profile = function() {
        //        
        // GET USER INFO
        //
        // - Request:
        //   GET /user
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'info': {'email': string, 'phone_number': string, 'name': string} }
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

            if (result.data.info.email !== undefined) {
                $scope.data.gpio.notification.endpoints.email.recipients = result.data.info.email;
            }
    
            if (result.data.info.email_verified !== undefined) {
                $scope.data.gpio.notification.endpoints.email.enable = result.data.info.email_verified;
            }
    
            if (result.data.info.phone_number !== undefined) {
                $scope.data.gpio.notification.endpoints.mobile.recipients = result.data.info.phone_number;
                $scope.data.gpio.notification.endpoints.notification.recipients = result.data.info.phone_number;
            }
    
            if (result.data.info.phone_number_verified !== undefined) {
                $scope.data.gpio.notification.endpoints.mobile.enable = result.data.info.phone_number_verified;
                $scope.data.gpio.notification.endpoints.notification.enable = result.data.info.phone_number_verified;
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };
*/

/*
    get_gpio = function() {
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
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/' + $scope.data.gpionumber.toString(),
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
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
        //   POST /devices/device/<devicename>gpio
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'value': string }
        //
        // - Response:
        //  { 'status': 'OK', 'message': string, 'value': string }
        //  { 'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/' + $scope.data.gpionumber.toString(),
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device GPIO',
                template: 'GPIO was set successfully!',
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
*/

    $scope.submit = function() {

/*
        if ($scope.data.devicestatus !== 'Online') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is offline!'});
            return;
        }
*/
        
        set_gpio_properties();
        set_gpio_voltage();
    };

    $scope.submitQuery = function() {
        
/*
        if ($scope.data.devicestatus !== 'Online') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is offline!'});
            return;
        }
*/

        get_gpio_properties();
        get_gpio_voltage();
    };

    $scope.submitDeviceList = function() {
        console.log("hello");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('configureDevice', device_param);
    };
    
    
    $scope.submitQuery();
    //get_profile();  
}])
   
.controller('deviceUARTCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.baudrates = [
        { "id":0,  "label": "110"     },
        { "id":1,  "label": "150"     },
        { "id":2,  "label": "300"     },
        { "id":3,  "label": "1200"    },
        { "id":4,  "label": "2400"    },
        { "id":5,  "label": "4800"    },
        { "id":6,  "label": "9600"    },
        { "id":7,  "label": "19200"   },
        { "id":8,  "label": "31250"   },
        { "id":9,  "label": "38400"   },
        { "id":10, "label": "57600"   },
        { "id":11, "label": "115200"  },
        { "id":12, "label": "230400"  },
        { "id":13, "label": "460800"  },
        { "id":14, "label": "921600"  },
        { "id":15, "label": "1000000" }
    ];

    $scope.parities = [
        { "id":0, "label": "None" },
        { "id":1, "label": "Odd"  },
        { "id":2, "label": "Even" }
    ];     

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'activeSection': 1,
        'showNotification': 0,
        
        'uart': {
            'baudrate': $scope.baudrates[0].id,
            'parity': $scope.parities[0].id,
            'notification': {
                'messages': [ 
                    { 'message': 'Hello World!', 'enable': true }, 
                ],
                'endpoints' : {
                    'mobile': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'email': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'notification': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'modem': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                    'storage': {
                        'recipients': '',
                        'enable': false,
                        'recipients_list': [],
                    },
                }
            }
        },
    };

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
        $scope.submitQuery();
    };
    
    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
    };

    
    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }            
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };
 
 
    get_uart_properties = function() {
        //
        // GET UART PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/uart/<number>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': 
        //     { 
        //      'baudrate': int,
        //      'parity': int,
        //      'notification': {
        //          'messages': [{ 'message': string, 'enable': boolean }, ...],
        //          'endpoints' : {
        //              'mobile': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': string, 'group': boolean}, ],
        //              },
        //              'email': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'notification': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'modem': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'storage': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //          }
        //      }
        //     }
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/uart/' + $scope.data.activeSection.toString() + '/properties',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value.notification !== undefined) {
                $scope.data.uart = result.data.value;
            }
            else {
                $scope.data.uart.baudrate = result.data.value.baudrate;
                $scope.data.uart.parity = result.data.value.parity;
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    set_uart_properties = function() {
        //
        // SET UART PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/uart/<number>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'baudrate': int,
        //      'parity': int,
        //      'notification': {
        //          'messages': [{ 'message': string, 'enable': boolean }, ...],
        //          'endpoints' : {
        //              'mobile': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': string, 'group': boolean}, ],
        //              },
        //              'email': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'notification': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'modem': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //              'storage': {
        //                  'recipients': string, // can be multiple items separated by comma
        //                  'enable': boolean,
        //                  //'recipients_list': [{'to': '', 'group': boolean}, ],
        //              },
        //          }
        //      }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/uart/' + $scope.data.activeSection.toString() + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.uart
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device UART',
                template: 'UART ' + $scope.data.activeSection.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

/*
    get_profile = function() {
        //        
        // GET USER INFO
        //
        // - Request:
        //   GET /user
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'info': {'email': string, 'phone_number': string, 'name': string} }
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
            

            if (result.data.info.email !== undefined) {
                $scope.data.uart.notification.endpoints.email.recipients = result.data.info.email;
            }
    
            if (result.data.info.email_verified !== undefined) {
                $scope.data.uart.notification.endpoints.email.enable = result.data.info.email_verified;
            }
    
            if (result.data.info.phone_number !== undefined) {
                $scope.data.uart.notification.endpoints.mobile.recipients = result.data.info.phone_number;
                $scope.data.uart.notification.endpoints.notification.recipients = result.data.info.phone_number;
            }
    
            if (result.data.info.phone_number_verified !== undefined) {
                $scope.data.uart.notification.endpoints.mobile.enable = result.data.info.phone_number_verified;
                $scope.data.uart.notification.endpoints.notification.enable = result.data.info.phone_number_verified;
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
*/

    $scope.submit = function() {
        
        set_uart_properties();
    };
    
    $scope.submitQuery = function() {

        get_uart_properties();
    };

    $scope.submitDeviceList = function() {
        console.log("hello");
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('configureDevice', device_param);
    };

    $scope.submitQuery();
    //get_profile();
}])
   
.controller('deviceI2CCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
    };

    $scope.sensors = [];
    $scope.sensors_counthdr = "No I2C device registered";
   
    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Add I2C Device Details failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }            
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };
    
    
    // GET I2C DEVICES
    $scope.getI2CSensors = function() {
        console.log("getI2CSensors");
        get_i2c_sensors();
    };

    get_i2c_sensors = function() {
        //
        // GET I2C SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/sensors',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No I2C device registered" ;
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 I2C device registered";
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " I2C devices registered";
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    // DELETE I2C SENSOR
    $scope.deleteI2CSensor = function(sensor) {
        console.log("deleteI2CSensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_i2c_sensor(sensor);
                    }
                }
            ]            
        });
    };
    
    delete_i2c_sensor = function(sensor) {
        //
        // DELETE I2C SENSOR
        //
        // - Request:
        //   DELETE /devices/device/<devicename>/i2c/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.getI2CSensors();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };



    // ADD I2C DEVICES    
    $scope.addI2CDevice = function() {
        console.log("addI2CDeviceDetails");
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('addI2CDevice', device_param);        
    };


    $scope.$on('$ionicView.enter', function(e) {
        $scope.getI2CSensors();
    });


    // EXIT PAGE
    $scope.submitDeviceList = function() {
        console.log("submitDeviceList");

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('configureDevice', device_param);
    };
}])
   
.controller('addI2CDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.manufacturers = [
        { "id":0,  "name": "Adafruit", "default": false },
        { "id":1,  "name": "DF Robot", "default": false },
        { "id":2,  "name": "Electronic Dollar Store", "default": true },
    ];

    $scope.devicemodels_ada = [{ "id":0,  "model": "N/A" }];
    $scope.devicemodels_dfr = [{ "id":0,  "model": "N/A" }];
    $scope.devicemodels_eds = [
        { "id":0,  "model": "BEEP", 
            "name": "Piezoelectric Beeper", 
            "desc": "Beeps a MIDI tone",
            "link": "https://electricdollarstore.com/beep.html" },

        { "id":1,  "model": "DIGI", 
            "name": "Digit Display",        
            "desc": "2-digit seven segment display",  
            "link": "https://electricdollarstore.com/dig2.html" },

        { "id":2,  "model": "LED",  
            "name": "RGB LED",
            "desc": "LED brightness control capable",  
            "link": "https://electricdollarstore.com/led.html"  },

        { "id":3,  "model": "POT",  
            "name": "Potentiometer",
            "desc": "Input range device",  
            "link": "https://electricdollarstore.com/pot.html"  },

        { "id":4,  "model": "TEMP", 
            "name": "Temperature Sensor",   
            "desc": "Input thresholded device",   
            "link": "https://electricdollarstore.com/temp.html" },
    ];
    $scope.devicemodels = $scope.devicemodels_eds;
 
 
    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
     
        'i2c': {
            'manufacturerid'     : $scope.manufacturers[2].id,
            'devicemodelid'      : $scope.devicemodels[0].id,

            'manufacturer' : $scope.manufacturers[2].name,
            'model'        : $scope.devicemodels[0].model,
            'name'  : $scope.devicemodels[0].name,
            'desc'  : $scope.devicemodels[0].desc,
            'link'  : $scope.devicemodels[0].link,
        }
    };


    $scope.submitAdd = function() {
        console.log("submitAdd");
        
        if ($scope.data.i2c.manufacturerid != 2) {
            $ionicPopup.alert({ title: 'Error', template: 'Selected choice is invalid!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }
        
        $scope.data.i2c.manufacturer = $scope.manufacturers[$scope.data.i2c.manufacturerid].name;
        $scope.data.i2c.model        = $scope.devicemodels[$scope.data.i2c.devicemodelid].model,
        $scope.data.i2c.name         = $scope.devicemodels[$scope.data.i2c.devicemodelid].name,
        $scope.data.i2c.desc         = $scope.devicemodels[$scope.data.i2c.devicemodelid].desc,
        $scope.data.i2c.link         = $scope.devicemodels[$scope.data.i2c.devicemodelid].link,
        
        $state.go('addI2CDeviceDetails', $scope.data);        
    };
    
    
    // EXIT PAGE
    $scope.submitDeviceList = function() {
        console.log("submitDeviceList");

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('deviceI2C', device_param);
    };    
}])
   
.controller('addI2CDeviceDetailsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;
 
    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
     
        'i2c'         : $stateParams.i2c,
        
        'sensorname' : $stateParams.i2c.model + ' 1',
        'sensor' : {
            'manufacturer': $stateParams.i2c.manufacturer,
            'model': $stateParams.i2c.model,
            'address': 0xFF,
        }
    };


    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Add I2C Device Details failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status == 409) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };


    // ADD I2C SENSOR
    $scope.addI2CSensor = function() {
        
        if ($scope.data.sensorname === undefined) {
            console.log("ERROR: Add I2C Sensor name is empty!");
            alert("ERROR: Add I2C Sensor name is empty!");
            return;
        }        
        else if ($scope.data.sensorname.length === 0) {
            console.log("ERROR: Add I2C Sensor name is empty!");
            alert("ERROR: Add I2C Sensor name is empty!");
            return;
        }
        else if ($scope.data.sensor.address === undefined) {
            console.log("ERROR: Add I2C Sensor address is empty!");
            alert("ERROR: Add I2C Sensor address is empty!");
            return;
        }        
        else if ($scope.data.sensor.address.length === 0) {
            console.log("ERROR: Add I2C Sensor address is empty!");
            alert("ERROR: Add I2C Sensor address is empty!");
            return;
        }        
        
        console.log("addI2CSensor");
        
        console.log($scope.data.sensorname);
        console.log($scope.data.sensor.manufacturer);
        console.log($scope.data.sensor.model);
        console.log($scope.data.sensor.address);

        sensor_param = $scope.data.sensor;
        add_i2c_sensor(sensor_param);
    };
    
    add_i2c_sensor = function(sensor_param) {
        //
        // ADD I2C SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'address': int, 'manufacturer': string, 'model': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/sensors/sensor/' + $scope.data.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
            data: sensor_param
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({ title: 'Success', template: 'Sensor added successfully!',
                buttons: [{ text: 'OK', type: 'button-positive',
                    onTap: function(e) {
                        $state.go('deviceI2C', {
                            'username': $scope.data.username, 
                            'token': $scope.data.token, 
                            'devicename': $scope.data.devicename, 
                            'devicestatus': $scope.data.devicestatus, 
                            'deviceid': $scope.data.deviceid, 
                            'serialnumber': $scope.data.serialnumber, 
                        });
                    }
                }]
            });
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    
    // EXIT PAGE
    $scope.submitDeviceList = function() {
        console.log("submitDeviceList");

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('deviceI2C', device_param);
    };    
}])
   
.controller('deviceNotificationsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

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
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
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

    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
            // TODO: replace alert with ionic alert
            alert("ERROR: Control Device failed with " + error.status + " " + error.statusText +"! " + error.data.message);
            
            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
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
        //   data: { 'recipient': string, 'message': string, 'options': string }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/notification',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
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
 

        if ($scope.data.devicestatus !== 'Online') {
            $ionicPopup.alert({title: 'Device Error', template: 'Device is offline!'});
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
                'recipient': $scope.data.recipient,
                'message': $scope.data.message
            };
            set_notifications(param);      
        }
        else {
            // sms
            var param = {
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
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        $state.go('configureDevice', device_param);
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
    };
    
//    $scope.items_master = []; // items retrieved from database
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
    
    // Filter by devices
    $scope.devices = [ "All devices" ];
    $scope.deviceidx = 0;
    
    // Filter by directions
    $scope.directions = [ "Both directions", "To", "From" ];
    $scope.directionidx = 0;
    
    // Filter by topics
    $scope.topics = [ "All topics", 
        "get_status", 
        "set_status",
        "get_ip",
        "get_subnet",
        "get_gateway",
        "get_mac",
        "get_gpio",
        "set_gpio",
        "get_rtc",
        "write_uart",
        "trigger_notifications"
    ];
    $scope.topicidx = 0;

    // Filter by date    
    $scope.date = {
        'begin': "",
        'end': ""
    };
    
    
    
    $scope.applyFilter = function(deviceidx, directionidx, topicidx) {

        var devicename = null;
        var deviceid = null;
        var direction = null;
        var topic = null;
        var datebegin = 0;
        var dateend = 0;
        
        if (deviceidx) {
            devicename = $scope.devices[deviceidx];
        }
        if (directionidx) {
            direction = $scope.directions[directionidx];
        }
        if (topicidx) {
            topic = $scope.topics[topicidx];
        }
        
        if ($scope.date.begin !== undefined && $scope.date.begin !== "") {
            console.log($scope.date.begin);
            datebegin = new Date($scope.date.begin).valueOf() / 1000;
            if (isNaN(datebegin)) {
                datebegin = 0;
            }
            console.log(datebegin);
             
            
            if ($scope.date.end !== undefined && $scope.date.end !== "") {
                console.log($scope.date.end);
                dateend = new Date($scope.date.end).valueOf() / 1000;
                if (isNaN(dateend)) {
                    dateend = 0;
                }
                console.log(dateend);
            }
        }

        Histories.fetch_filtered($scope.data, devicename, direction, topic, datebegin, dateend).then(function(res) {
            $scope.items = res;
            $scope.data.token = User.get_token();
        }); 
    };
    
    
    $scope.submitRefresh = function() {
    
        Devices.fetch($scope.data).then(function(res) {
            var i;
            for (i=0; i<res.length; i++) {
                var result = $scope.devices.includes(res[i].devicename);
                if (result === false) {
                    $scope.devices.push(res[i].devicename);
                }
            }
            $scope.data.token = User.get_token();
        });
    
        Histories.fetch($scope.data).then(function(res) {
            $scope.items = res;
            $scope.data.token = User.get_token();
        }); 
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("DEVICES enter ionicView REFRESH LIST");
        $scope.submitRefresh();
    });    
}])
 