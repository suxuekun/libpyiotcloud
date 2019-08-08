angular.module('app.controllers', [])
  
.controller('homeCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {


}])
   
.controller('devicesCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Devices',     // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Devices) {

    var server = Server.rest_api;
    
    $scope.devices = [];

    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    }


    $scope.submitTest = function(devicename) {

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': devicename
        }
       
        $state.go('controlDevice', device_param );
    }

    $scope.submitAdd = function() {

        $state.go('menu.registerDevice', $scope.data);
    }
    
    $scope.submitRefresh = function() {

        Devices.fetch($scope.data).then(function(res) {
            $scope.devices = res;
            if ($scope.devices.length === 0) {        
                //$ionicPopup.alert({
                //    title: 'Query Devices',
                //    template: 'No devices registered!',
                //});
            }
        });

/*
        // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/devices',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            $scope.devices = Devices.devices;//result.data.devices;
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Login failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Login failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Server is down!");
            }
            
            $scope.devices = [];
        });
*/
    }
    
    $scope.submitView = function(device) {
        console.log("view" + device.devicename);
        
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicename=" + device.devicename);

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': device.devicename
        }        
        
        // Send HTTP request to REST API
        $http({
            method: 'PATCH', // Should be GET but GET is not working
            url: server + '/devices/device',
            headers: {'Content-Type': 'application/json'},
            data: device_param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'devicecert': result.data.device.cert,
                'devicepkey': result.data.device.pkey,
                'deviceca': result.data.device.ca
            }
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
    }

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
    }
    
    $scope.submitDeleteAction = function(device) {
        console.log("delete");
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicename=" + device.devicename);

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': device.devicename
        }        
        
        // Send HTTP request to REST API
        $http({
            method: 'DELETE',
            url: server + '/devices/device',
            headers: {'Content-Type': 'application/json'},
            data: device_param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
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
    }
    
    //console.log("DEVICES username=" + User.get_username());
    //console.log("DEVICES token=" + User.get_token());
    // Send HTTP request to REST API
    //$scope.submitRefresh();
    //console.log($scope.devices);
    
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("DEVICES enter ionicView REFRESH LIST");
        $scope.submitRefresh();
    });
    
}])
   
.controller('accountCtrl', ['$scope', '$stateParams', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $http, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),

        'fullname': 'Unknown',
        'email': 'Unknown',
        'subscription': 'FREE'
    }

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
    }  
    
    get_profile = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log("ACCOUNT OK");
            console.log(result.data);
            
            $scope.data.fullname = result.data.info.given_name + " " + result.data.info.family_name;
            $scope.data.email = result.data.info.email;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    } 

    $scope.$on('$ionicView.enter', function(e) {
        console.log("ACCOUNT enter ionicView");
        
        
        if ($scope.data.username !== "" || $scope.data.token !== "") {
            $scope.data.username = User.get_username();
            $scope.data.token = User.get_token();
            
            get_profile({
                'username': $scope.data.username,
                'token': $scope.data.token
            });
        }
    });


    get_profile({
        'username': $scope.data.username,
        'token': $scope.data.token
    });



    $scope.submitUpgrade = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
    }
}
])
   
.controller('menuCtrl', ['$scope', '$stateParams', '$state', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, User) {

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

    console.log("MENU " + $scope.data.username);
    console.log("MENU " + User.get_username());

    $scope.submitLogout = function() {
        
        $scope.data.username = "";        
        $scope.data.token = "";        
        User.clear();
        $state.go('login');
    }
}

  
  
])
   
.controller('loginCtrl', ['$scope', '$stateParams', '$state', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, Server, User) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $scope.username,
        'password': $scope.password
    }
    
    $scope.submit = function() {
        
        console.log("username=" + $scope.data.username);
        console.log("password=" + $scope.data.password);

        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: Login username is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Login username is empty!");
            return;
        }
        else if ($scope.data.password.trim().length === 0) {
            console.log("ERROR: Login password is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Login password is empty!");
            return;
        }
 
        // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user/login',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);

            var user_data = {
                'username': $scope.data.username,
                'token': result.data.token
            }
            
            User.set(user_data);
        
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            // Handle failed login
            if (error.data !== null) {
                console.log("ERROR: Login failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Login failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
            }
            else {
                console.log("ERROR: Login failed because server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Login failed because server is down!");
            }
        });
    }
}])
   
.controller('signupCtrl', ['$scope', '$stateParams', '$state', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, Server) {

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
        console.log("username=" + $scope.data.username);
        console.log("password=" + $scope.data.password);
        console.log("password2=" + $scope.data.password2);
        console.log("email=" + $scope.data.email);
        console.log("givenname=" + $scope.data.givenname);
        console.log("familyname=" + $scope.data.familyname);
        
        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: Signup username is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup username is empty!");
            return;
        }
        else if ($scope.data.password.trim().length === 0) {
            console.log("ERROR: Signup password is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup password is empty!");
            return;
        }
        else if ($scope.data.password.trim().length < 6) {
            console.log("ERROR: Signup password should be at least 6 characters!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup password should be at least 6 characters!");
            return;
        }        
        else if ($scope.data.password2 !== $scope.data.password) {
            console.log("ERROR: Signup confirm password does not match!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup confirm password does not match!");
            return;
        }
        else if ($scope.data.email === undefined) {
            console.log("ERROR: Signup email is invalid!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup email is invalid!");
            return;
        }        
        else if ($scope.data.email.trim().length === 0) {
            console.log("ERROR: Signup email is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup email is empty!");
            return;
        }        
        else if ($scope.data.givenname.trim().length === 0) {
            console.log("ERROR: Signup firstname is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup firstname is empty!");
            return;
        }        
        else if ($scope.data.familyname.trim().length === 0) {
            console.log("ERROR: Signup lastname is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Signup lastname is empty!");
            return;
        }
        
        
         // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user/signup',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
        
            $scope.data = {
                'username': $scope.data.username,
            }
            $state.go('confirmRegistration', $scope.data);
        })
        .catch(function (error) {
            // Handle failed login
            console.log(error);
            if (error.data !== null) {
                console.log("ERROR: Signup failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Signup failed with " + error.status + " " + error.statusText + "! " + error.data.message);
            }
            else {
                console.log("ERROR: Signup failed because server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Signup failed because server is down!");
            }
            return;
        });       
    }
}])
   
.controller('recoverCtrl', ['$scope', '$stateParams', '$state', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'email': $scope.email
    }
    
    $scope.submit = function() {
        console.log("email=" + $scope.data.email);

        // Handle invalid input
        if ($scope.data.email === undefined) {
            console.log("ERROR: Account Recover email is invalid!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Account Recover email is invalid!");
            return;
        }          
        else if ($scope.data.email.trim().length === 0) {
            console.log("ERROR: Account Recover email is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Account Recover email is empty!");
            return;
        }

         // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user/forgot_password',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            
            $scope.data = {
                'username': result.data.username
            }
            $state.go('resetPassword', $scope.data);            
        })
        .catch(function (error) {
            // Handle failed login
            console.log(error);
            if (error.data !== null) {
                console.log("ERROR: Account Recover failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Account Recover failed with " + error.status + " " + error.statusText + "! " + error.data.message);
            }
            else {
                console.log("ERROR: Account Recover failed because server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Account Recover failed because server is down!");
            }
            return;
        });
    }
}])
   
.controller('resetPasswordCtrl', ['$scope', '$stateParams', '$state', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, Server) {

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
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: Reset Password username is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Reset Password username is empty!");
            return;
        }
        else if ($scope.data.confirmationcode.trim().length === 0) {
            console.log("ERROR: Reset Password code is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Reset Password code is empty!");
            return;
        }
        else if ($scope.data.password.trim().length === 0) {
            console.log("ERROR: Reset Password password is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Reset Password password is empty!");
            return;
        }
        else if ($scope.data.password.trim().length < 6) {
            console.log("ERROR: Reset Password password should be at least 6 characters!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Reset Password password should be at least 6 characters!");
            return;
        } 
        else if ($scope.data.password2 !== $scope.data.password) {
            console.log("ERROR: Reset Password confirm password does not match!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Reset Password confirm password does not match!");
            return;
        } 

         // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user/confirm_forgot_password',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            alert("Recovery completed!");
            $state.go('login');            
        })
        .catch(function (error) {
            // Handle failed login
            console.log(error);
            if (error.data !== null) {
                console.log("ERROR: Reset Password failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Reset Password failed with " + error.status + " " + error.statusText + "! " + error.data.message);
            }
            else {
                console.log("ERROR: Reset Password failed because server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Reset Password failed because server is down!");
            }
            return;
        });
    }
}])
   
.controller('confirmRegistrationCtrl', ['$scope', '$stateParams', '$state', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, Server) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'confirmationcode': $scope.confirmationcode
    }
    
    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("confirmationcode=" + $scope.data.confirmationcode);
        
        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: Confirm registration code is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Username is empty!");
            return;
        }
        else if ($scope.data.confirmationcode.trim().length === 0) {
            console.log("ERROR: Confirm registration code is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Confirm registration code is empty!");
            return;
        }

         // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user/confirm_signup',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            alert("Registration completed!");
            $state.go('login');
        })
        .catch(function (error) {
            // Handle failed login
            console.log(error);
            if (error.data !== null) {
                console.log("ERROR: Confirm registration failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Confirm registration failed with " + error.status + " " + error.statusText + "! " + error.data.message);
            }
            else {
                console.log("ERROR: Confirm registration failed because server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Confirm registration failed because server is down!");
            }
            return;
        });       
    }
    
    $scope.submitResend = function() {
        console.log("username=" + $scope.data.username);

        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: Confirm registration code is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Username is empty!");
            return;
        }

        var param = {
            'username': $scope.data.username
        }
        
         // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/user/resend_confirmation_code',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);
            alert("Confirmation code resent successfully! Please chek your email!");
        })
        .catch(function (error) {
            // Handle failed login
            console.log(error);
            if (error.data !== null) {
                console.log("ERROR: Confirm registration failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Confirm registration failed with " + error.status + " " + error.statusText + "! " + error.data.message);
            }
            else {
                console.log("ERROR: Confirm registration failed because server is down!"); 
                // TODO: replace alert with ionic alert
                alert("ERROR: Confirm registration failed because server is down!");
            }
            return;
        });       
    }    
}])
   
.controller('helpCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {


}])
   
.controller('settingsCtrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {


}])
   
.controller('registerDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, Devices) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,        
        'devicename': $scope.devicename
    }
    
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
        else if ($scope.data.token.trim().length === 0) {
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
        
        // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/devices/device',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);

            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'devicecert': result.data.device.cert,
                'devicepkey': result.data.device.pkey,
                'deviceca': result.data.device.ca
            }
            
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
    }
}])
   
.controller('viewDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName


function ($scope, $stateParams, $state, $http, $ionicPopup, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,
        'deviceid': $stateParams.deviceid,
        'devicecert': $stateParams.devicecert,
        'devicepkey': $stateParams.devicepkey,
        'deviceca': $stateParams.deviceca
    }
    
    $scope.submitTest = function() {
        console.log("submitTest= " + $scope.data.devicename);
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        }
       
        $state.go('controlDevice', device_param);    
    }


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
    }
    
    $scope.submitDeleteAction = function() {
        console.log("submitDelete= " + $scope.data.devicename);
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        }
       
        // Send HTTP request to REST API
        $http({
            method: 'DELETE',
            url: server + '/devices/device',
            headers: {'Content-Type': 'application/json'},
            data: device_param
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);

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
    }
    
    $scope.submitDeviceList = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        }
        $state.reload('menu.devices');
        $state.go('menu.devices', device_param, {reload: true});
   }
}])
   
.controller('controlDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,
        'status': 'UKNOWN'
    }

    $scope.submitEthernet = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceEthernet', $scope.data, {animate: false} );
    }

    $scope.submitGPIO = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceGPIO', $scope.data, {animate: false} );
    }    

    $scope.submitUART = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceUART', $scope.data, {animate: false} );
    }    

    $scope.submitRTC = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceRTC', $scope.data, {animate: false} );
    }    

    $scope.submitNotifications = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceNotifications', $scope.data, {animate: false} );
    }
    
    
    
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
    }     

    query_device = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST',
            url: server + '/devices/device/status',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            $scope.data.status = 'RUNNING';
        })
        .catch(function (error) {
            handle_error(error);
            
            $scope.data.status = 'NOT RUNNING';
            
            //$ionicPopup.alert({
            //    title: 'Device Status',
            //    template: 'Device is not running!',
            //});            
        }); 
    }    

    restart_device = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'PUT',
            url: server + '/devices/device/status',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Device Status',
                template: 'Device was restarted successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    }    
    
    $scope.submitRestart = function() {
        console.log("devicename=" + $scope.data.devicename);

        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'value': 'restart'
        }

        restart_device(param); 
    }
    
    $scope.submitStatus = function() {
        console.log("devicename=" + $scope.data.devicename);

        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        }

        query_device(param); 
    }
    
    $scope.submitView = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicename=" + $scope.data.devicename);

        // Handle invalid input        
        if ($scope.data.username.trim().length === 0) {
            console.log("ERROR: View Device username is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: View Device username is empty!");
            return;
        }
        else if ($scope.data.token.trim().length === 0) {
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
        
        // Send HTTP request to REST API
        $http({
            method: 'PATCH',
            url: server + '/devices/device',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            // Handle successful login
            console.log(result.data);

            var device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': result.data.device.devicename,
                'deviceid': result.data.device.deviceid,
                'devicecert': result.data.device.cert,
                'devicepkey': result.data.device.pkey,
                'deviceca': result.data.device.ca
            }
            
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
    }    
    
    $scope.submitStatus();
}])
   
.controller('deviceEthernetCtrl', ['$scope', '$stateParams', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $http, $ionicPopup, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,

        'ipaddr': $scope.ipaddr,
        'subnet': $scope.subnet,
        'gateway': $scope.gateway,
        'macaddr': $scope.macaddr
    }
    
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
    }
    
    get_ip = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST', // Should be GET but GET is not working
            url: server + '/devices/device/ip',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.ipaddr = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.ipaddr = 'Unknown';
        }); 
    }
    
    get_subnet = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST', // Should be GET but GET is not working
            url: server + '/devices/device/subnet',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.subnet = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.subnet = 'Unknown';
        }); 
    }

    get_gateway = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST', // Should be GET but GET is not working
            url: server + '/devices/device/gateway',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.gateway = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.gateway = 'Unknown';
        }); 
    }

    get_mac = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST', // Should be GET but GET is not working
            url: server + '/devices/device/mac',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.macaddr = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
            $scope.data.macaddr = 'Unknown';
        }); 
    }

    
    $scope.submit = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("ipaddr=" + $scope.data.ipaddr);
        console.log("subnet=" + $scope.data.subnet);
        console.log("gateway=" + $scope.data.gateway);
        console.log("macaddr=" + $scope.data.macaddr);

        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
        }
        
        // TODO Send REST API
        get_ip(param);
        get_subnet(param);
        get_gateway(param);
        get_mac(param);
    }
    
}])
   
.controller('deviceGPIOCtrl', ['$scope', '$stateParams', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $http, $ionicPopup, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,
        
        'gpionumber': $scope.gpionumber,
        'gpiovalue': $scope.gpiovalue,
        'gpiovalueset': $scope.gpiovalueset
    }
    
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
    }
    
    get_gpio = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST', // Should be GET but GET is not working
            url: server + '/devices/device/gpio',
            headers: {'Content-Type': 'application/json'},
            data: param
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
    }

    set_gpio = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'PUT',
            url: server + '/devices/device/gpio',
            headers: {'Content-Type': 'application/json'},
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
    }

    $scope.submitGet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("gpionumber=" + $scope.data.gpionumber);

        // Handle invalid input
        if ($scope.data.gpionumber === undefined) {
            console.log("ERROR: GPIO number is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: GPIO number is empty!");
            return;
        }

        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'number': $scope.data.gpionumber.toString()
        }

        get_gpio(param);
    }

    $scope.submitSet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("gpionumber=" + $scope.data.gpionumber);
        console.log("gpiovalueset=" + $scope.data.gpiovalueset);

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
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'number': $scope.data.gpionumber.toString(),
            'value': gpiovalueset.toString()
        }

        set_gpio(param);
   }
}])
   
.controller('deviceUARTCtrl', ['$scope', '$stateParams', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $http, $ionicPopup, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,
        
        'message': $scope.message
    }
    
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
    }    
 
    set_uart = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'PUT',
            url: server + '/devices/device/uart',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Device UART',
                template: 'Message was written to UART successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    } 

    $scope.submit = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("message=" + $scope.data.message);

        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'value': $scope.data.message
        }

        set_uart(param);
    }
}])
   
.controller('deviceRTCCtrl', ['$scope', '$stateParams', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $http, $ionicPopup, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,
        
        'epoch': $scope.epoch,
        'datetime' : $scope.datetime,
        'datetimeset' : $scope.datetimeset
    }
    
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
    }
    
    get_rtc = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'POST', // Should be GET but GET is not working
            url: server + '/devices/device/rtc',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.epoch = result.data.value;

            var myDate = new Date(result.data.value*1000);
            $scope.data.datetime = myDate.toLocaleString()

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
    }
    
    set_rtc = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'PUT',
            url: server + '/devices/device/rtc',
            headers: {'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            $ionicPopup.alert({
                title: 'Device RTC',
                template: 'RTC was set successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    }
    
    $scope.submitGet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("datetime=" + $scope.data.datetime);
        console.log("epoch=" + $scope.data.epoch);
        
        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename
        }

        get_rtc(param);
    }    
    
    $scope.submitSet = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("datetimeset=" + $scope.data.datetimeset);

        var seconds = Math.round((new Date).getTime() / 1000);
        console.log(seconds);
        
        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'value': seconds
        }

        set_rtc(param);
    }    
    
}])
   
.controller('deviceNotificationsCtrl', ['$scope', '$stateParams', '$http', '$ionicPopup', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $http, $ionicPopup, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': $stateParams.username,
        'token': $stateParams.token,
        'devicename': $stateParams.devicename,
        
        'recipient': $scope.recipient,
        'message': $scope.message
    }
    
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
    }     

    set_notifications = function(param) {
        // Send HTTP request to REST API
        $http({
            method: 'PUT',
            url: server + '/devices/device/notification',
            headers: {'Content-Type': 'application/json'},
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
    }

    $scope.submit = function() {
        console.log("devicename=" + $scope.data.devicename);
        console.log("recipient=" + $scope.data.recipient);
        console.log("message=" + $scope.data.message);
        
        var param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'recipient': $scope.data.recipient,
            'message': $scope.data.message
        }

        set_notifications(param);      
    }    
}])
 