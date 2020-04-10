angular.module('app.controllers', [])
  
.controller('homeCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;

    $scope.oauthorization_code = null;
    $scope.waiting_login = false;
    $scope.win = null;
    $scope.timer = null;
    $scope.runtime_max = 120;
    $scope.savetokens = false;
    
    // Support for Login via social accounts like Facebook, Google, Amazon
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
                            return (sParameterName[1].split('#'))[0];
                        }
                    }
                }
            }
        }
        catch(err) {
        }
        return null;
    }

    // Support for Login via social accounts like Facebook, Google, Amazon
    // This will be called during the completion of the OAuth authorization code
    // Once called, it retrieves the code from the url parameters, together with the stateid random number
    // and then retrieves the tokens using the code
    // Once the token is retrieved, it saves it to the backend database
    // and then closes the window
    function GetURLParameters() {
        var state_id = GetURLParameter('state');
        $scope.oauthorization_code = GetURLParameter('code');

        if ($scope.savetokens) {
            if ($scope.oauthorization_code !== null && state_id !== null) {
                // successful login via social idp
                if (window.__env.apiUrl === "localhost") {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, state_id, window.__env.clientId, 'http://localhost:8100');
                    //$scope.login_idp($scope.oauthorization_code, 'http://localhost:8100');
                }
                else {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, state_id, window.__env.clientId, server);
                    //$scope.login_idp($scope.oauthorization_code, server);
                }
            }
            else if ($scope.oauthorization_code !== null) {
                // successful login via social idp
                if (window.__env.apiUrl === "localhost") {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, 0, window.__env.clientId, 'http://localhost:8100');
                }
                else {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, 0, window.__env.clientId, server);
                }
            }
            else if (state_id !== null) {
                // error login via social idp
                let error = GetURLParameter('error');
                if (error !== null) {
                    $scope.login_idp_storetoken(state_id, {});
                }
            }
            else {
                // regular login, do nothing
            }
        }
        else {
            if ($scope.oauthorization_code !== null && state_id !== null) {
                // successful login via social idp
                $scope.login_idp_storecode(state_id, $scope.oauthorization_code);
            }
            else if (state_id !== null) {
                // failed login via social idp
                let error = GetURLParameter('error');
                if (error !== null) {
                    $scope.login_idp_storecode(state_id, "");
                }
            }
            else {
                // regular login, do nothing
            }    
        }
    }

    // Support for Login via social accounts like Facebook, Google, Amazon
    // "The /oauth2/token endpoint only supports HTTPS POST. 
    //  The user pool client makes requests to this endpoint directly and not through the system browser."    
    $scope.get_tokens_from_oauthcode = function(oauthorization_code, state_id, client_id, redirect_uri, spinner=null) {
        //
        // GET TOKENS
        // - Request:
        //   POST 'https://' + window.__env.oauthDomain + '/oauth2/token'
        //   headers: {'Content-Type': 'application/x-www-form-urlencoded' }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //
        
        url = 'https://' + window.__env.oauthDomain + '/oauth2/token';
        data = 'grant_type=authorization_code' + '&client_id=' + client_id + '&code=' + oauthorization_code + '&redirect_uri=' + redirect_uri;
        //console.log(url);
        //console.log(data);
        
        $http({
            method: 'POST',
            url: url,
            headers: {'Content-Type': 'application/x-www-form-urlencoded' },
            data: data
        })
        .then(function (result) {
            console.log(result.data);

            if ($scope.savetokens) {
                // Set username and tokens
                if (state_id !== 0) {
                    $scope.login_idp_storetoken(state_id, { 'id': result.data.id_token, 'refresh': result.data.refresh_token, 'access': result.data.access_token });
                }
                else {
                    let user_data = {
                        'username': 'SocialIDPLogin',
                        'token': { 'id': result.data.id_token, 'refresh': result.data.refresh_token, 'access': result.data.access_token },
                        'name': 'SocialIDPLogin'
                    };
                    User.set(user_data);
                    $state.go('menu.devices', user_data);
                }
            }
            else {
                $scope.get_profile({ 'id': result.data.id_token, 'refresh': result.data.refresh_token, 'access': result.data.access_token }, spinner);
            }
        })
        .catch(function (error) {
            if ($scope.savetokens) {
                // Handle failed
                if (error.data !== null) {
                    console.log(error.status + " " + error.statusText);
                    $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
                }
                else {
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
            }
            else {
                spinner[0].style.visibility = "hidden";
                $scope.waiting_login = false;
                
                if (error.data !== null) {
                    console.log(error.status + " " + error.statusText);
                    $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
                }
                else {
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
            }
        }); 
    };

    // Support for Login via social accounts like Facebook, Google, Amazon
    // When user clicks on the login via social accounts, 
    // a new window is opened which handles getting of the authorization code (OAuth process)
    // The specified callback url will be called containing the authorization.
    // Given the authorization code, the app requests for the tokens.
    $scope.getOAuthCode = function(socialidp=null) {
        
        // "The /login endpoint only supports HTTPS GET. 
        //  The user pool client makes this request through a system browser. 
        //  System browsers for JavaScript include Chrome or Firefox. 
        //  Android browsers include Custom Chrome Tab. iOS browsers include Safari View Control."        
        if (true) {
            var state = Math.floor(Math.random() * 8999999999 + 1000000000);
            
            var url = "https://" + window.__env.oauthDomain + "/login";
            url += "?client_id=" + window.__env.clientId;
            url += "&response_type=code";
            url += "&scope=email+openid+phone+aws.cognito.signin.user.admin";
            url += "&state=" + state;
            if (socialidp !== null) {
                url += "&identity_provider=" + socialidp;
            }
            
            if (window.__env.apiUrl === "localhost") {
                url += '&redirect_uri=http://localhost:8100';
            }
            else {
                url += '&redirect_uri=' + server;
            }
            
            $scope.win = window.open(url,"_blank",
                'width=1000,height=475,left=100,top=100,resizable=no,scrollbars=no,toolbar=no,menubar=no,location=no,directories=no,status=no,titlebar=no',replace=false);
            if ($scope.win !== null) {
                // Display spinner
                var spinner = document.getElementsByClassName("spinner");
                spinner[0].style.visibility = "visible";
                $scope.waiting_login = true;
                var runtime = 0;
                
                $scope.timer = setInterval(function() {
                    if ($scope.win.closed) {
                        //console.log("exited");
                        runtime = 0;
                        clearInterval($scope.timer);
                        $scope.timer = null;
                        
                        if ($scope.savetokens) {
                            $scope.login_idp_querytoken(spinner, state.toString());
                        }
                        else {
                            $scope.login_idp_querycode(spinner, state.toString());
                        }
                    }
                    else {
                        runtime += 1;
                        console.log(runtime);
                        if (runtime >= $scope.runtime_max) {
                            $scope.win.close();
                            $scope.win = null;
                            
                            spinner[0].style.visibility = "hidden";
                            $scope.waiting_login = false;
                            
                            runtime = 0;
                            clearInterval($scope.timer);
                            $scope.timer = null;
                            
                            $ionicPopup.alert({ title: 'Error', template: 'Login with social account timed out!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }
                    }
                }, 1000);
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Cannot open a new window! Check if popup window is blocked!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
    };



    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_storetoken = function(id, token) {
        // 
        // LOGIN IDP STORE TOKEN
        // 
        // - Request:
        //   POST /user/login/idp/token/<id>
        //   headers: {'Content-Type': 'application/json'}
        //   data: {'token': json_obj}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/login/idp/token/' + id,
            headers: {'Content-Type': 'application/json'},
            data: {'token': token}
        })
        .then(function (result) {
            console.log(result.data);
            window.close();
        })
        .catch(function (error) {
            window.close();
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


    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_querytoken = function(spinner, id) {
        // 
        // LOGIN IDP QUERY TOKEN
        // 
        // - Request:
        //   GET /user/login/idp/token/<id>
        //   headers: {'Content-Type': 'application/json'}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'GET',
            url: server + '/user/login/idp/token/' + id,
            headers: {'Content-Type': 'application/json'},
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            console.log(result.data);

            if (result.data.token !== undefined) {
                if (result.data.token.access === undefined) {
                    $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    return;
                }
                
                var user_data = {
                    'username': result.data.username,
                    'token': result.data.token,
                    'name': result.data.name,
                };
                
                User.set(user_data);
                $state.go('menu.devices', user_data);
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed due to cancellation or timeout!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
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


    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_storecode = function(id, code) {
        // 
        // LOGIN IDP STORE CODE
        // 
        // - Request:
        //   POST /user/login/idp/code/<id>
        //   headers: {'Content-Type': 'application/json'}
        //   data: {'code': string}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/login/idp/code/' + id,
            headers: {'Content-Type': 'application/json'},
            data: {'code': code}
        })
        .then(function (result) {
            console.log(result.data);

            $scope.oauthorization_code = null;
            window.close();
        })
        .catch(function (error) {
            $scope.oauthorization_code = null;
            window.close();

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

    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_querycode = function(spinner, id) {
        // 
        // LOGIN IDP QUERY CODE
        // 
        // - Request:
        //   GET /user/login/idp/code/<id>
        //   headers: {'Content-Type': 'application/json'}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'GET',
            url: server + '/user/login/idp/code/' + id,
            headers: {'Content-Type': 'application/json'},
        })
        .then(function (result) {
            console.log(result.data);

            // Handle failed login
            if (result.data.code === "") {
                spinner[0].style.visibility = "hidden";
                $scope.waiting_login = false;
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                return;
            }
            
            //$scope.oauthorization_code = result.data.code;
            if (window.__env.apiUrl === "localhost") {
                $scope.get_tokens_from_oauthcode(result.data.code, id, window.__env.clientId, 'http://localhost:8100', spinner);
            }
            else {
                $scope.get_tokens_from_oauthcode(result.data.code, id, window.__env.clientId, server, spinner);
            }
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            // Handle failed
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed due to cancellation!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };

    $scope.get_profile = function(token, spinner) {
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
            headers: {'Authorization': 'Bearer ' + token.access}
        })
        .then(function (result) {
            console.log("ACCOUNT OK");
            console.log(result.data);
            
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;

            let user_data = {
                'username': result.data.info.username,
                'token': token,
                'name': result.data.info.name
            };
            User.set(user_data);
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }); 
    };
    
    // Support for Login via social accounts like Facebook
    $scope.$on('$ionicView.enter', function(e) {
        $scope.oauthorization_code = null;
        $scope.waiting_login = false;
        $scope.win = null;
        $scope.timer = null;
        $scope.runtime_max = 120;
        $scope.savetokens = false;        
        GetURLParameters();
    });
    
    $scope.$on('$ionicView.beforeLeave', function(e) {
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            $scope.timer = null;
        }
    });
    
}
])
   
.controller('home2Ctrl', ['$scope', '$stateParams', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams) {


}])
   
.controller('devicesCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', 'DeviceGroups',     // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices, DeviceGroups) {

    var server = Server.rest_api;

    $scope.devices = [];
    $scope.devicegroups = [];
    $scope.devices_counthdr = "No device registered" ;
    $scope.activeSection = parseInt($stateParams.activeSection, 10);
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        
        'devices_filter': "",
    };
    

    $scope.changeActiveSection = function(s) {
        $scope.activeSection = s;
        $scope.submitRefresh();
    };
    
    $scope.viewDevice = function(device) {

        if ($scope.activeSection === 1) {
            // DEVICE
            console.log("devicename=" + device.devicename);
            let device_param = {
                'username': User.get_username(),
                'token': User.get_token(),
                'devicename': device.devicename,
                'deviceid': device.deviceid,
                'serialnumber': device.serialnumber,
                'devicestatus': "Status: UNKNOWN",
                'deviceversion': "UNKNOWN",
                'location': "UNKNOWN"
            };
    
            if (device.heartbeat !== undefined) {
                let heartbeat = new Date(device.heartbeat * 1000);
                device_param.devicestatus = "Last active: " + heartbeat;    
            }
            if (device.version !== undefined) {
                device_param.deviceversion = device.version;    
            }
            if (device.location !== undefined) {
                device_param.location = device.location;    
            }
    
            $state.go('device', device_param, {reload:true} );
        }
        else {
            // DEVICE GROUP
            let device_param = {
                'username': User.get_username(),
                'token': User.get_token(),
                'devicegroupname': device.groupname
            };
            $state.go('deviceGroup', device_param, {reload:true} );
        }
    };
    
    $scope.submitAdd = function() {

        var device_param = {
            'username': User.get_username(),
            'token': User.get_token()
        };
        
        if ($scope.activeSection === 1) {
            $state.go('addDevice', device_param);
        }
        else {
            $state.go('addDeviceGroup', device_param);
        }
    };
    
    
    $scope.submitSearch = function(keyEvent) {
        if (keyEvent.which === 13) {
            $scope.submitRefresh();
        }
    };

    $scope.getDiffString = function(currdate, devicedate) {
        let diffString = "";
        let diff = currdate-devicedate;

        //console.log(diff);
        if (diff < 60) {
            diffString = diff + " second";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
            // just make it online
            if (diff < 10) {
                diffString = "Online";
            }
        }
        else if (diff < 3600) {
            diff = parseInt(diff/60, 10);
            diffString = diff + " minute";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
        }
        else if (diff < 86400) {
            diff = parseInt(diff/3600, 10);
            diffString = diff + " hour";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
        }
        else if (diff < 604800) {
            /*
            diff = parseInt(diff/86400, 10);
            diffString = diff + " day";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
            */
            let devicedatetime = new Date(devicedate * 1000);
            let currdatetime = new Date(currdate * 1000);
            diff = currdatetime.getDate()-devicedatetime.getDate();
            if (diff === 1) {
                diffString = "Yesterday";
            }
            else if (diff === 7) {
                diffString = "1 week ago";
            }
            else {
                diffString = devicedatetime.toLocaleString('en-us', {  weekday: 'long' });
            }
        }
        else if (diff < 2419200) {
            /*
            diff = parseInt(diff/604800, 10);
            diffString = diff + " week";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
            */
            let devicedatetime = new Date(devicedate * 1000);
            //console.log(devicedatetime);
            diffString = devicedatetime.toLocaleString('en-us', {  month: 'long', day: 'numeric' });
        }
        else if (diff < 29030400) {
            diff = parseInt(diff/2419200, 10);
            diffString = diff + " month";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
        }
        else {
            diff = parseInt(diff/29030400, 10);
            diffString = diff + " year";
            if (diff > 1) {
                diffString += "s";
            }
            diffString += " ago";
        }
        
        //let heartbeat = new Date(devicedate * 1000);
        //diffString += " (" + heartbeat + ")";
        if (diffString !== "Online") {
            diffString = "Last active: " + diffString;
        }
        return diffString;
    };

    $scope.submitRefresh = function(livestatus=false) {

        if ($scope.activeSection === 1) {
            // DEVICES
            
            // Fetch devices
            Devices.fetch($scope.data, $scope.data.devices_filter).then(function(res) {
                $scope.devices = res;
                $scope.data.token = User.get_token();
                if ($scope.devices.length !== 0) {
                    if ($scope.devices.length === 1) {
                        $scope.devices_counthdr = $scope.devices.length.toString() + " device registered";
                    }
                    else {
                        $scope.devices_counthdr = $scope.devices.length.toString() + " devices registered";
                    }
                    
                    let currdate = parseInt(new Date().valueOf()/ 1000, 10);
                    console.log(currdate);
                    
                    if (livestatus === true) {
                        //console.log($scope.devices.length);
                        let indexy = 0;
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            //console.log("indexy=" + indexy.toString() + " " + $scope.devices[indexy].devicename);
                            
                            if ($scope.devices[indexy].heartbeat !== undefined) {
                                $scope.devices[indexy].devicestatus = $scope.getDiffString(currdate, $scope.devices[indexy].heartbeat);
                            }
                            else {
                                $scope.devices[indexy].devicestatus = "Last active: N/A";
                            }
                            
                            query_device(indexy, $scope.devices[indexy].devicename);
                        }
                    }
                    else {
                        let indexy = 0;
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].heartbeat !== undefined) {
                                $scope.devices[indexy].devicestatus = $scope.getDiffString(currdate, $scope.devices[indexy].heartbeat);
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
                
                // TEST CODE ONLY
                //register_device_token("1234", "GCM");
                //register_device_token("5678", "APNS");
            })
            .catch(function (error) {
                console.log("Devices.fetch failed!!!");
                handle_error(error);
            }); 
        }
        else {
            // DEVICE GROUPS
            
            // Fetch devicegroups
            DeviceGroups.fetch($scope.data).then(function(res) {
                $scope.devicegroups = res;
                $scope.data.token = User.get_token();
                if ($scope.devicegroups.length !== 0) {
                    if ($scope.devicegroups.length === 1) {
                        $scope.devices_counthdr = $scope.devicegroups.length.toString() + " device group registered";
                    }
                    else {
                        $scope.devices_counthdr = $scope.devicegroups.length.toString() + " device groups registered";
                    }
                }
                else {
                    $scope.devices_counthdr = "No device group registered";
                }
            })
            .catch(function (error) {
                console.log("DeviceGroups.fetch failed!!!");
                handle_error(error);
            }); 
        }
    };
    
    
    base64Encode = function(str) {
        return window.btoa(str);
    };
    
    urlEncode = function(str) {
        return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
    };

    jwtEncode = function(devicetoken, service) {

        // get time
        // https://www.epochconverter.com/
        iat = Math.floor(Date.now() / 1000); // epoch time in seconds
        exp = iat + 10; // plus 10 seconds
        //console.log(iat);
        //console.log(exp);

        // get JWT header
        headerData = JSON.stringify({ 
            "alg": "HS256", 
            "typ": "JWT"
        });

        // get JWT payload
        payloadData = JSON.stringify({
            "username": devicetoken,
            "password": service,
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
    
    register_device_token = function(devicetoken, service) {
        // 
        // REGISTER DEVICE TOKEN
        // 
        // - Request:
        //   POST /mobile/devicetoken
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: {'token': jwtEncode(devicetoken, service)}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/mobile/devicetoken',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: { 'token': jwtEncode(devicetoken, service) }
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            console.log(error);
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
            //console.log(devicename + ": Online");
            $scope.devices[index].devicestatus = 'Online';    
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };    
    
    handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Get Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
                //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };    
    

    $scope.$on('$ionicView.enter', function(e) {
        $scope.devices = [];
        $scope.devicegroups = [];
        $scope.devices_counthdr = "No device registered" ;
        $scope.activeSection = 1;
        
        //console.log($state.params);
        //console.log($stateParams);
        if ($state.params.activeSection !== undefined) {
            $scope.activeSection = parseInt($state.params.activeSection, 10);
        }
        $scope.submitRefresh();
    });
}])
   
.controller('profileCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),

        'fullname': 'Unknown',
        'email': 'Unknown',
        'phonenumber': 'Unknown',
        'identityprovider': 'Unknown',
    };

    $scope.enable_2fa = false;
    

    
    
    $scope.handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            $ionicPopup.alert({title: 'Error', template: error.data.message});
            
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

    $scope.enable2FA = function(flag) {
        $scope.enable_2fa = flag;
        $scope.enable_mfa($scope.enable_2fa);
    };
    
    $scope.enable_mfa = function(enable) {
        //
        // ENABLE MFA
        //
        // - Request:
        //   POST /user/mfa
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        $http({
            method: 'POST',
            url: server + '/user/mfa',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: {'enable': enable }
        })
        .then(function (result) {
            console.log(result.data);
            if (enable === true) {
                $ionicPopup.alert({ title: 'MFA', template: 'MFA was enabled successfully!', buttons: [{text: 'OK', type: 'button-positive'}] });
            }
            else {
                $ionicPopup.alert({ title: 'MFA', template: 'MFA was disabled successfully!', buttons: [{text: 'OK', type: 'button-positive'}] });
            }
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    };

    $scope.getProfile = function() {
        $scope.data.username = User.get_username();
        $scope.data.token = User.get_token();
        $scope.get_profile();
    };
    
    $scope.get_profile = function() {
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
            //console.log("ACCOUNT OK");
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
                    $scope.data.phonenumber +=  " (Click to VERIFY)";
                }
            }
            if (result.data.info.identity !== undefined) {
                $scope.data.identityprovider = result.data.info.identity.providerName + " (" + result.data.info.identity.userId + ")";
            }
            else {
                $scope.data.identityprovider = "None";
            }
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    };

    $scope.delete_account = function() {
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
            $scope.handle_error(error);
        });        
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
        //console.log("submitVerifynumber");

        // Handle invalid input        
        if ($scope.data.username === undefined) {
            $ionicPopup.alert({title: 'Verify Number Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Verify Number Error', template: 'Username is empty!'});
            return;
        }

        if ($scope.data.phonenumber === "Unknown") {
            return;
        }
        if ($scope.data.phonenumber.includes("Click to VERIFY") === false) {
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
            $scope.handle_error(error);
        });
    };
    
    $scope.submitSavechanges = function() {
        //console.log("submitSavechanges");
        
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
                            $scope.get_profile({
                                'username': $scope.data.username,
                                'token': $scope.data.token
                            });
                        }
                    }
                ]
            });
        })
        .catch(function (error) {
            $scope.data.phonenumber = "Unknown";
            $scope.handle_error(error);
        });        
    };

    $scope.submitChangepassword = function() {
        //console.log("submitChangepassword");
        
        // Cannot change password if login with social accounts
        if ($scope.data.identityprovider !== "Unknown" && $scope.data.identityprovider !== "None") {
            $ionicPopup.alert({title: 'Change Password', template: 'Cannot change password if you login via Facebook or Google!'});
            return;
        }
        
        $state.go('changePassword', {'username': $scope.data.username, 'token': $scope.data.token});
    };

    $scope.submitDeleteaccountAction = function() {
        //console.log("username=" + $scope.data.username);
        //console.log("token=" + $scope.data.token);
        
        $scope.delete_account(); 
    };

    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.enable_2fa = false;
        $scope.get_profile();
    });

    $scope.$on('$ionicView.beforeLeave', function(e) {
        $scope.data.fullname = 'Unknown';
        $scope.data.email = 'Unknown';
        $scope.data.phonenumber = 'Unknown';
        $scope.data.identityprovider = 'Unknown';
    });
}
])
   
.controller('creditsCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', 'Payments', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token, Payments) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),

        'subscription_type': 'Unknown',
        'subscription_credits': 'Unknown',
    };

    $scope.topups = [];
    $scope.usages = [];
    
    
    $scope.handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            $ionicPopup.alert({title: 'Error', template: error.data.message});
            
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

    $scope.get_subscription = function() {
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
            //console.log("get_subscription");
            console.log(result.data);

            $scope.data.subscription_type = result.data.subscription.type;
            $scope.data.subscription_credits = result.data.subscription.credits;
            $scope.getTopups();
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    };

    $scope.getTopups = function() {
        $scope.topups = [];
        $scope.usages = [];
        Payments.fetch_paypal_payments($scope.data).then(function(res) {
            $scope.topups = res;
            $scope.data.token = User.get_token();
        });        
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.topups = [];
        $scope.usages = [];
        $scope.get_subscription();
    });


    $scope.submitViewTransactionTopup = function(topup) {
        
        console.log(topup);
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'transaction': topup
        };
        $state.go('transactionDetails', param, {reload: true});
    };



    $scope.submitBuyCredits = function() {
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'credits': $scope.data.subscription_credits
        };
        $state.go('topUpCredits', param, {reload: true});   
    };

/*    
    $scope.submitViewCreditPurchases = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'credits': $scope.data.subscription_credits
        };
        $state.go('creditPurchases', param, {reload: true});
    };

    $scope.submitViewCreditUsage = function() {
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        //$state.go('creditUsage', param, {reload: true});   
    };
*/
}
])
   
.controller('topUpCreditsCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User, Token) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'credits': $stateParams.credits,
    };

    $scope.topup = {
        'credits': 100,
        'amount': 1,
    };

    $scope.timer = null;
    $scope.notice = "";
    
    
    $scope.computeAmount = function(credits) {
        $scope.topup.amount = credits/100;
    };
    
    $scope.submitCancel = function() {
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        $state.go('menu.credits', device_param, {reload: true});   
    };
    
    
    $scope.submitBuycredits = function() {

        // Check if atleast minimum value
        let minimum = 100;
        if ($scope.topup.credits < minimum) {
            $ionicPopup.alert({
                title: 'Error',
                template: 'Minimum allowed topup is ' + minimum + ' credits!',
            });
            return;
        }   
        
        $scope.notice = "";

        $ionicPopup.alert({
            title: 'Subscription',
            template: 'You have selected to buy ' + 
                $scope.topup.credits + ' credits at $' + $scope.topup.amount + ' USD. ' +
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
                        //console.log("YES!");
                        process_payment_paypal();
                    }
                }
            ]
        });
    };
    
    process_payment_paypal = function() {

        //console.log("process_payment_paypal");

        var host_url = "";
        if (window.__env.apiUrl === "localhost") {
            host_url = "http://localhost:8100";
        }
        else {
            host_url = server;
        }
        var paypal_param = {
            'returnurl': host_url + '/#/page_payment_confirmation',
            'cancelurl': host_url + '/#/page_payment_confirmation',
            'amount': $scope.topup.amount,
        };



        //       
        // PAYPAL SETUP
        //
        // - Request:
        //   POST /account/payment/paypalsetup
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'returnurl': string, 'cancelurl', string, 'amount': int }
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'payment': {'approvalurl': string, 'paymentid': string}}
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

            var win = window.open(result.data.payment.approvalurl,"_blank",
                'height=600,width=800,left=100,top=100,resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=no,directories=no,status=no',replace=false);
            if (win !== null) {
                $scope.notice = "Waiting for user to approve the Paypal transaction ...";
                $scope.timer = setInterval(function() {
                    if (win.closed) {
                        clearInterval($scope.timer);
                        //$scope.timer = null; // NOTE: delay the setting to null inside executePayment
                        
                        $scope.notice = "Please wait while we verify the Paypal transaction ...";
                        executePayment(result.data.payment.paymentid);
                        //verifyPayment(result.data.payment.paymentid);
                    }
                }, 1000);
            }
        })
        .catch(function (error) {
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: "Paypal Setup failed with " + error.status + " " + error.statusText + "! " + error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });

                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };

    executePayment = function(paymentid) {
        //
        // PAYPAL EXECUTE
        //
        // - Request:
        //   POST /account/payment/paypalexecute/PAYMENTID
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //
        // - Response:
        //   {'status': 'OK', 'message': string, 'subscription': {'type': string, 'credits': int, 'prevcredits': int}}
        //   {'status': 'NG', 'message': string}
        //  
        //console.log("paypalexecute " + paymentid);
        //console.log(paypal_param);
        $http({
            method: 'POST',
            url: server + '/account/payment/paypalexecute/' + paymentid,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
        })
        .then(function (result) {
            console.log(result.data);
            $scope.notice = "";
            $scope.timer = null;
            
            if (result.data.status === "OK") {
                $scope.data.credits = result.data.subscription.credits;
                var added_credits = result.data.subscription.credits - result.data.subscription.prevcredits;
                $ionicPopup.alert({
                    title: 'Payment Confirmation',
                    template: 'The payment transaction has been verified. ' + 
                        added_credits + ' credits has been successfully added to your account! ' + 
                        'Your new credit balance is ' + result.data.subscription.credits + '.',
                    buttons: [
                        {
                            text: 'OK',
                            type: 'button-positive',
                            onTap: function(e) {
                                param = {
                                    'username': $scope.data.username,
                                    'token': $scope.data.token
                                };
                                $state.go('menu.credits', param, {reload: true});   
                            }
                        }
                    ]
                });
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
            $scope.timer = null;
            $scope.notice = "";
            
            // Handle failed
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: "Paypal Verify failed with " + error.status + " " + error.statusText + "! " + error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });

                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.topup = {
            'credits': 100,
            'amount': 1,
        };
        $scope.timer = null;
        $scope.notice = "";
    });    
    
    $scope.$on('$ionicView.beforeLeave', function(e) {
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            $scope.timer = null;
        }
        $scope.notice = "";
    });    
}])
   
.controller('creditPurchasesCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Payments', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Payments) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'credits': $stateParams.credits
    };
    
    $scope.items = []; // items to be shown

    
    $scope.getTransactionDetails = function(item) {
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'credits': $scope.data.credits,
            'id': item.id
        };
        $state.go('transactionDetails', device_param, {reload: true});   
    };  
    
    $scope.submitRefresh = function() {
        $scope.items = [];
        Payments.fetch_paypal_payments($scope.data).then(function(res) {
            $scope.items = res;
            $scope.data.token = User.get_token();
        });
        
    };
    
    $scope.submitCancel = function() {
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'activeSection': 2
        };
        $state.go('menu.account', device_param, {reload: true});   
    };    
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.submitRefresh();
    });
}])
   
.controller('purchaseDetailsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Payments', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Payments) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        
        
        'credits': $stateParams.credits,
        'id': $stateParams.id,
    };
    
    $scope.paypal = {};

    $scope.submitRefresh = function() {
        //console.log("retrievePaypalTransaction " + $scope.data.id);
        retrievePaypalTransaction($scope.data.id);
    };
   
    retrievePaypalTransaction = function(id) {
        //
        // RETRIEVE PAYPAL TRANSACTION
        //
        // - Request:
        //   GET /account/payment/paypal/TRANSACTIONID
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'GET',
            url: server + '/account/payment/paypal/' + id,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: "Retrieve Paypal Transaction failed with " + error.status + " " + error.statusText + "! " + error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });

                if (error.data.message === "Token expired") {
                    Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                    $scope.data.token = User.get_token();
                }
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            window.close();
        });
    };
       
    
    $scope.submitCancel = function() {
        device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'credits': $scope.data.credits,
        };
        $state.go('creditPurchases', device_param, {reload: true});   
    };    
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.submitRefresh();
    });
}])
   
.controller('transactionDetailsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Payments', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Payments) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        
        'transaction': $state.params.transaction,
    };

    $scope.submitCancel = function() {
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
        };
        $state.go('menu.credits', param, {reload: true});   
    };    
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter");
        $scope.data.transaction = $state.params.transaction;
        //console.log($stateParams.transaction);
        //console.log($state.params.transaction);
        //console.log($scope.data.transaction);
    });
}])
   
.controller('paymentConfirmationCtrl', ['$scope', '$stateParams', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $ionicPopup, $http, Server) {

    var server = Server.rest_api;
    var spinner = document.getElementsByClassName("spinner2");
    

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
        var paymentid = GetURLParameter('paymentId');
        var payerid = GetURLParameter('PayerID');
        var params = {};
        if (paymentid !== null) {
            params.paymentid = paymentid;
        }
        if (payerid !== null) {
            params.payerid = payerid;
        }
        return params;
    }


    function storePaymentPayerID(paypal_param) {
        //
        // PAYPAL STORE PAYERID
        //
        // - Request:
        //   POST /account/payment/paypalpayerid/PAYMENTID
        //   headers: {'Content-Type': 'application/json'}
        //   data: { 'payerid': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //  
        //console.log("paypalexecute " + paypal_param.paymentid);
        //console.log(paypal_param);
        $http({
            method: 'POST',
            url: server + '/account/payment/paypalpayerid/' + paypal_param.paymentid,
            headers: {'Content-Type': 'application/json'},
            data: {'payerid': paypal_param.payerid}
        })
        .then(function (result) {
            console.log(result.data);
            spinner[0].style.visibility = "hidden";
            window.close();
        })
        .catch(function (error) {
            // Handle failed
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: "Paypal Store Token failed with " + error.status + " " + error.statusText + "! " + error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            spinner[0].style.visibility = "hidden";
            window.close();
        });
    }


    spinner[0].style.visibility = "visible";
    paypal_param = GetURLParameters();
    if (paypal_param !== null) {
        //console.log("GetURLParameters: ");
        console.log(paypal_param);

        if (paypal_param.payerid !== undefined) {
            console.log("Customer approved the transaction!");
            //executePayment(paypal_param);
            storePaymentPayerID(paypal_param);
        }
        else {
            console.log("Customer cancelled the transaction!");
            spinner[0].style.visibility = "hidden";
            window.close();
        }
    }
}])
   
.controller('menuCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'name': User.get_name()
    };

    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter ionicView");
        if ($scope.data.username === "") {
            $scope.data.username = User.get_username();
        }
        if ($scope.data.token === "") {
            $scope.data.token = User.get_token();
        }
        if ($scope.data.name === "") {
            $scope.data.name = User.get_name();
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
        console.log("logout: " + $scope.data.username);
        $scope.logout();
    };
    
    $scope.logout = function() {
        // 
        // LOGOUT
        // 
        // - Request:
        //   POST /user/logout
        //   headers: {'Authorization': 'Bearer ' + token.access}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/logout',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log("logout successful!");
            console.log(result.data);
            $scope.data.username = "";        
            $scope.data.token = "";        
            $scope.data.name = "";        
            User.clear();
            $state.go('home', {}, {reload: true});
        })
        .catch(function (error) {
            console.log("logout failed!");
            $scope.data.username = "";        
            $scope.data.token = "";        
            $scope.data.name = "";        
            User.clear();
            $state.go('home', {}, {reload: true});
        });    
    }    
}

  
  
])
   
.controller('loginCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': '',
        'password': ''
    };
    
    $scope.oauthorization_code = null;
    $scope.waiting_login = false;
    $scope.win = null;
    $scope.timer = null;
    $scope.runtime_max = 120;
    $scope.savetokens = false;

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
        //console.log(iat);
        //console.log(exp);

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
        $scope.waiting_login = true;

        var start_time = Math.floor(Date.now() / 1000);
        //console.log("login: " + $scope.data.username);

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
            $scope.waiting_login = false;
            
            console.log("login: OK " + (Math.floor(Date.now() / 1000)-start_time) + " secs");
            // Handle successful
            console.log(result.data);

            var user_data = {
                'username': $scope.data.username,
                'token': result.data.token,
                'name': result.data.name
            };
            
            User.set(user_data);
        
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            // Handle failed
            if (error.data !== null) {
                if (error.status == 401) {
                    if (error.data.message === "PasswordResetRequiredException") {
                        let data = {
                            'username': error.data.username
                        };
                        $state.go('resetPassword', data); 
                    }
                    else if (error.data.message === "MFARequiredException") {
                        let data = {
                            'username': error.data.username
                        };
                        $state.go('confirmMFA', data); 
                    }
                    else {
                        console.log(error.status + " " + error.statusText);
                        $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
                    }
                }
                else {
                    console.log(error.status + " " + error.statusText);
                    $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
                }
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };
    
    
    // Support for Login via social accounts like Facebook, Google, Amazon
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
                            return (sParameterName[1].split('#'))[0];
                        }
                    }
                }
            }
        }
        catch(err) {
        }
        return null;
    }

    // Support for Login via social accounts like Facebook, Google, Amazon
    // This will be called during the completion of the OAuth authorization code
    // Once called, it retrieves the code from the url parameters, together with the stateid random number
    // and then retrieves the tokens using the code
    // Once the token is retrieved, it saves it to the backend database
    // and then closes the window
    function GetURLParameters() {
        var state_id = GetURLParameter('state');
        $scope.oauthorization_code = GetURLParameter('code');

        if ($scope.savetokens) {
            if ($scope.oauthorization_code !== null && state_id !== null) {
                // successful login via social idp
                if (window.__env.apiUrl === "localhost") {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, state_id, window.__env.clientId, 'http://localhost:8100');
                    //$scope.login_idp($scope.oauthorization_code, 'http://localhost:8100');
                }
                else {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, state_id, window.__env.clientId, server);
                    //$scope.login_idp($scope.oauthorization_code, server);
                }
            }
            else if ($scope.oauthorization_code !== null) {
                // successful login via social idp
                if (window.__env.apiUrl === "localhost") {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, 0, window.__env.clientId, 'http://localhost:8100');
                }
                else {
                    $scope.get_tokens_from_oauthcode($scope.oauthorization_code, 0, window.__env.clientId, server);
                }
            }
            else if (state_id !== null) {
                // error login via social idp
                let error = GetURLParameter('error');
                if (error !== null) {
                    $scope.login_idp_storetoken(state_id, {});
                }
            }
            else {
                // regular login, do nothing
            }
        }
        else {
            if ($scope.oauthorization_code !== null && state_id !== null) {
                // successful login via social idp
                $scope.login_idp_storecode(state_id, $scope.oauthorization_code);
            }
            else if (state_id !== null) {
                // failed login via social idp
                let error = GetURLParameter('error');
                if (error !== null) {
                    $scope.login_idp_storecode(state_id, "");
                }
            }
            else {
                // regular login, do nothing
            }    
        }
    }

    // Support for Login via social accounts like Facebook, Google, Amazon
    // "The /oauth2/token endpoint only supports HTTPS POST. 
    //  The user pool client makes requests to this endpoint directly and not through the system browser."    
    $scope.get_tokens_from_oauthcode = function(oauthorization_code, state_id, client_id, redirect_uri, spinner=null) {
        //
        // GET TOKENS
        // - Request:
        //   POST 'https://' + window.__env.oauthDomain + '/oauth2/token'
        //   headers: {'Content-Type': 'application/x-www-form-urlencoded' }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //
        
        url = 'https://' + window.__env.oauthDomain + '/oauth2/token';
        data = 'grant_type=authorization_code' + '&client_id=' + client_id + '&code=' + oauthorization_code + '&redirect_uri=' + redirect_uri;
        //console.log(url);
        //console.log(data);
        
        $http({
            method: 'POST',
            url: url,
            headers: {'Content-Type': 'application/x-www-form-urlencoded' },
            data: data
        })
        .then(function (result) {
            console.log(result.data);

            if ($scope.savetokens) {
                // Set username and tokens
                if (state_id !== 0) {
                    $scope.login_idp_storetoken(state_id, { 'id': result.data.id_token, 'refresh': result.data.refresh_token, 'access': result.data.access_token });
                }
                else {
                    let user_data = {
                        'username': 'SocialIDPLogin',
                        'token': { 'id': result.data.id_token, 'refresh': result.data.refresh_token, 'access': result.data.access_token },
                        'name': 'SocialIDPLogin'
                    };
                    User.set(user_data);
                    $state.go('menu.devices', user_data);
                }
            }
            else {
                $scope.get_profile({ 'id': result.data.id_token, 'refresh': result.data.refresh_token, 'access': result.data.access_token }, spinner);
            }
        })
        .catch(function (error) {
            if ($scope.savetokens) {
                // Handle failed
                if (error.data !== null) {
                    console.log(error.status + " " + error.statusText);
                    $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
                }
                else {
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
            }
            else {
                spinner[0].style.visibility = "hidden";
                $scope.waiting_login = false;
                
                if (error.data !== null) {
                    console.log(error.status + " " + error.statusText);
                    $ionicPopup.alert({ title: 'Login Error', template: error.data.message });
                }
                else {
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
            }
        }); 
    };

    // Support for Login via social accounts like Facebook, Google, Amazon
    // When user clicks on the login via social accounts, 
    // a new window is opened which handles getting of the authorization code (OAuth process)
    // The specified callback url will be called containing the authorization.
    // Given the authorization code, the app requests for the tokens.
    $scope.getOAuthCode = function(socialidp=null) {
        
        // "The /login endpoint only supports HTTPS GET. 
        //  The user pool client makes this request through a system browser. 
        //  System browsers for JavaScript include Chrome or Firefox. 
        //  Android browsers include Custom Chrome Tab. iOS browsers include Safari View Control."        
        if (true) {
            var state = Math.floor(Math.random() * 8999999999 + 1000000000);
            
            var url = "https://" + window.__env.oauthDomain + "/login";
            url += "?client_id=" + window.__env.clientId;
            url += "&response_type=code";
            url += "&scope=email+openid+phone+aws.cognito.signin.user.admin";
            url += "&state=" + state;
            if (socialidp !== null) {
                url += "&identity_provider=" + socialidp;
            }
            
            if (window.__env.apiUrl === "localhost") {
                url += '&redirect_uri=http://localhost:8100';
            }
            else {
                url += '&redirect_uri=' + server;
            }
            
            $scope.win = window.open(url,"_blank",
                'width=1000,height=475,left=100,top=100,resizable=no,scrollbars=no,toolbar=no,menubar=no,location=no,directories=no,status=no,titlebar=no',replace=false);
            if ($scope.win !== null) {
                // Display spinner
                var spinner = document.getElementsByClassName("spinner");
                spinner[0].style.visibility = "visible";
                $scope.waiting_login = true;
                var runtime = 0;
                
                $scope.timer = setInterval(function() {
                    if ($scope.win.closed) {
                        //console.log("exited");
                        runtime = 0;
                        clearInterval($scope.timer);
                        $scope.timer = null;
                        
                        if ($scope.savetokens) {
                            $scope.login_idp_querytoken(spinner, state.toString());
                        }
                        else {
                            $scope.login_idp_querycode(spinner, state.toString());
                        }
                    }
                    else {
                        runtime += 1;
                        console.log(runtime);
                        if (runtime >= $scope.runtime_max) {
                            $scope.win.close();
                            $scope.win = null;
                            
                            spinner[0].style.visibility = "hidden";
                            $scope.waiting_login = false;
                            
                            runtime = 0;
                            clearInterval($scope.timer);
                            $scope.timer = null;
                            
                            $ionicPopup.alert({ title: 'Error', template: 'Login with social account timed out!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }
                    }
                }, 1000);
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Cannot open a new window! Check if popup window is blocked!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
    };



    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_storetoken = function(id, token) {
        // 
        // LOGIN IDP STORE TOKEN
        // 
        // - Request:
        //   POST /user/login/idp/token/<id>
        //   headers: {'Content-Type': 'application/json'}
        //   data: {'token': json_obj}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/login/idp/token/' + id,
            headers: {'Content-Type': 'application/json'},
            data: {'token': token}
        })
        .then(function (result) {
            console.log(result.data);
            window.close();
        })
        .catch(function (error) {
            window.close();
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


    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_querytoken = function(spinner, id) {
        // 
        // LOGIN IDP QUERY TOKEN
        // 
        // - Request:
        //   GET /user/login/idp/token/<id>
        //   headers: {'Content-Type': 'application/json'}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'GET',
            url: server + '/user/login/idp/token/' + id,
            headers: {'Content-Type': 'application/json'},
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            console.log(result.data);

            if (result.data.token !== undefined) {
                if (result.data.token.access === undefined) {
                    $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    return;
                }
                
                var user_data = {
                    'username': result.data.username,
                    'token': result.data.token,
                    'name': result.data.name,
                };
                
                User.set(user_data);
                $state.go('menu.devices', user_data);
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed due to cancellation or timeout!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
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


    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_storecode = function(id, code) {
        // 
        // LOGIN IDP STORE CODE
        // 
        // - Request:
        //   POST /user/login/idp/code/<id>
        //   headers: {'Content-Type': 'application/json'}
        //   data: {'code': string}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/login/idp/code/' + id,
            headers: {'Content-Type': 'application/json'},
            data: {'code': code}
        })
        .then(function (result) {
            console.log(result.data);

            $scope.oauthorization_code = null;
            window.close();
        })
        .catch(function (error) {
            $scope.oauthorization_code = null;
            window.close();

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

    // Support for Login via social accounts like Facebook, Google, Amazon
    $scope.login_idp_querycode = function(spinner, id) {
        // 
        // LOGIN IDP QUERY CODE
        // 
        // - Request:
        //   GET /user/login/idp/code/<id>
        //   headers: {'Content-Type': 'application/json'}
        // 
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'GET',
            url: server + '/user/login/idp/code/' + id,
            headers: {'Content-Type': 'application/json'},
        })
        .then(function (result) {
            console.log(result.data);

            // Handle failed login
            if (result.data.code === "") {
                spinner[0].style.visibility = "hidden";
                $scope.waiting_login = false;
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                return;
            }
            
            //$scope.oauthorization_code = result.data.code;
            if (window.__env.apiUrl === "localhost") {
                $scope.get_tokens_from_oauthcode(result.data.code, id, window.__env.clientId, 'http://localhost:8100', spinner);
            }
            else {
                $scope.get_tokens_from_oauthcode(result.data.code, id, window.__env.clientId, server, spinner);
            }
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            // Handle failed
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed due to cancellation!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        });
    };

    $scope.get_profile = function(token, spinner) {
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
            headers: {'Authorization': 'Bearer ' + token.access}
        })
        .then(function (result) {
            console.log("ACCOUNT OK");
            console.log(result.data);
            
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;

            let user_data = {
                'username': result.data.info.username,
                'token': token,
                'name': result.data.info.name
            };
            User.set(user_data);
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            $scope.waiting_login = false;
            
            if (error.data !== null) {
                $ionicPopup.alert({ title: 'Error', template: 'Login with social account failed!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else {
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }); 
    };
    
    // Support for Login via social accounts like Facebook
    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter");
        GetURLParameters();
    });
    
    $scope.$on('$ionicView.beforeLeave', function(e) {
        console.log("beforeLeave");
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            $scope.timer = null;
        }
    });
    
}])
   
.controller('signupCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;

    $scope.data = {
        'username': '',
        'password': '',
        'password2': '',
        'name'        : '',
        'phonenumber' : '',
        'email'       : '',
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
        'email': ''
    };
    
    $scope.submit = function() {
        console.log("email=" + $scope.data.email);

        // Handle invalid input
        if ($scope.data.email === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Field is empty!'});
            return;
        }          
        else if ($scope.data.email.length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Field is empty!'});
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
        'confirmationcode': '',
        'password': '',
        'password2': ''
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
        else if ($scope.data.username.length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Username is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode.length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.password === undefined) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.password.length === 0) {
            $ionicPopup.alert({title: 'Recovery Error', template: 'Password is empty!'});
            return;
        }
        else if ($scope.data.password.length < 6) {
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
        $state.go('menu.profile', {'username': $scope.data.username, 'token': $scope.data.token} );
    };
}])
   
.controller('confirmRegistrationCtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'confirmationcode': ''
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
   
.controller('confirmMFACtrl', ['$scope', '$stateParams', '$state', '$ionicPopup', '$http', 'Server', 'User', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $ionicPopup, $http, Server, User) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': $stateParams.username,
        'confirmationcode': ''
    };
    
    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("confirmationcode=" + $scope.data.confirmationcode);
        
        // Handle invalid input        
        if ($scope.data.confirmationcode === undefined) {
            $ionicPopup.alert({title: 'MFA Error', template: 'Code is empty!'});
            return;
        }
        else if ($scope.data.confirmationcode.length === 0) {
            $ionicPopup.alert({title: 'MFA Error', template: 'Code is empty!'});
            return;
        }


        // Display spinner
        var spinner = document.getElementsByClassName("spinner4");
        spinner[0].style.visibility = "visible";


        //
        // LOGIN MFA
        //
        // - Request:
        //   POST /user/login/mfa
        //   { 'username': string, 'confirmationcode': string }
        //
        // - Response:
        //   {'status': 'OK', 'message': string}
        //   {'status': 'NG', 'message': string}
        //
        $http({
            method: 'POST',
            url: server + '/user/login/mfa',
            headers: {'Content-Type': 'application/json'},
            data: $scope.data
        })
        .then(function (result) {
            spinner[0].style.visibility = "hidden";
            
            // Handle successful
            console.log(result.data);

            var user_data = {
                'username': $scope.data.username,
                'token': result.data.token,
                'name': result.data.name
            };
            
            User.set(user_data);
        
            $state.go('menu.devices', user_data);
        })
        .catch(function (error) {
            spinner[0].style.visibility = "hidden";
            
            // Handle failed
            console.log(error);
            if (error.data !== null) {
                console.log(error.status + " " + error.statusText);
                $ionicPopup.alert({title: 'MFA Error', template: error.data.message});
            }
            else {
                $ionicPopup.alert({title: 'MFA Error', template: 'Server is down!'});
            }
            return;
        });       
    };

    $scope.submitCancel = function() {
        $state.go('login');
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
            $state.go('menu.profile', {'username': $scope.data.username, 'token': $scope.data.token} );
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
        $state.go('menu.profile', {'username': $scope.data.username, 'token': $scope.data.token} );
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
            url: server + '/others/about',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({ title: 'Success', template: result.data.url[item],
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
            
            $ionicPopup.alert({ title: 'Success', template: result.data.url[item],
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
   
.controller('addDeviceGroupCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', 'DeviceGroups', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices, DeviceGroups) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),

        'devicegroupname': "",
    };


    $scope.submit = function() {
        console.log("username=" + $scope.data.username);
        console.log("token=" + $scope.data.token);
        console.log("devicegroupname=" + $scope.data.devicegroupname);

        if ($scope.data.devicegroupname === undefined) {
            console.log("ERROR: Register DeviceGroup devicegroupname is undefined!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register DeviceGroup devicegroupname is undefined!");
            return;
        }
        else if ($scope.data.devicegroupname.trim().length === 0) {
            console.log("ERROR: Register DeviceGroup devicegroupname is empty!");
            // TODO: replace alert with ionic alert
            alert("ERROR: Register DeviceGroup devicegroupname is empty!");
            return;
        }
        
        DeviceGroups.add($scope.data, $scope.data.devicegroupname).then(function(res) {
            console.log(res);
            
            if (res.data !== null) {
                if (res.data.status === "OK") {
                    $ionicPopup.alert({
                        title: 'Success',
                        template: 'Device group added successfully!',
                        buttons: [
                            {
                                text: 'OK',
                                type: 'button-positive',
                                onTap: function(e) {
                                    $state.go('menu.devices', 
                                        {
                                            'username': $scope.data.username, 
                                            'token': $scope.data.token,
                                            'activeSection': "2"
                                        });
                                }
                            }
                        ]
                    });
                }
                else {
                    if (res.status == 409) {
                        $ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    else {
                        $ionicPopup.alert({ title: 'Error', template: 'Failed to process device group!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
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
            'token': $scope.data.token,
            'activeSection': "2"
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
    
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
        'version'     : $stateParams.version
    };

    $scope.newfirmwareavailable = false;
    $scope.newfirmwareversion = 0;
    $scope.newfirmwareupdates = null;
    
    $scope.new_devicename = $stateParams.devicename;
    var device_statuses = ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"];


    $scope.onChangeDevicename = function(keyEvent, new_devicename) {
        if (keyEvent.which === 13) {
            $scope.changeDevicename($scope.data.devicename, new_devicename);
        }
    };
    
    // CHANGE DEVICENAME
    $scope.changeDevicename = function(devicename, new_devicename) {
        if ($scope.data.devicename === new_devicename) {
            $ionicPopup.alert({ title: 'Error', template: 'Device name is the same!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
        else {
            
            $ionicPopup.alert({
                title: 'Change Device Name',
                template: 'Are you sure you want to change the device name from ' + devicename + ' to ' + new_devicename + '?',
                buttons: [
                    { 
                        text: 'No',
                        type: 'button-negative',
                        onTap: function(e) {
                            $scope.new_devicename = devicename;
                        }
                    },
                    {
                        text: 'Yes',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.new_devicename = new_devicename;
                            $scope.update_devicename(devicename, new_devicename);
                        }
                    }
                ]            
            });            
        }
    };



    $scope.handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status >= 400 && error.status < 500) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!");
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    }; 


    // GET DEVICE FIRMWARE UPDATES
    $scope.get_latest_firmware = function() {
        //
        // GET STATUS
        // - Request:
        //   GET /others/firmwareupdates
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'document': json_object }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/others/firmwareupdates',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            console.log(result.data.document.ft900.latest);
            
            if ($scope.data.version !== "UNKNOWN") {
                if (result.data.document.ft900.latest > $scope.data.version) {
                    $scope.newfirmwareavailable = true;
                }
                else {
                    $scope.newfirmwareavailable = false;
                }
            }
            else {
                $scope.newfirmwareavailable = true;
            }
            
            $scope.newfirmwareupdates = result.data.document;
            $scope.newfirmwareversion = result.data.document.ft900.latest;
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 


    // UPDATE DEVICE NAME
    $scope.update_devicename = function(devicename, new_devicename) {
        //
        // UPDATE DEVICE NAME
        // - Request:
        //   POST /devices/device/<devicename>/name
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + devicename + '/name',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access, 'Content-Type': 'application/json' },
            data: {'new_devicename': new_devicename}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({
                title: 'Change Device Name',
                template: 'Change Device Name was successful!',
            });
            
            $scope.data.devicename = new_devicename;
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 


    // GET STATUS
    $scope.getDevice = function(devicename) {
        $scope.get_status(devicename);
    };

    $scope.get_status = function(devicename) {
        //
        // GET STATUS
        // - Request:
        //   GET /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { "status": int, "version": string } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + devicename + '/status',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({
                title: 'Device Status',
                template: 'Device is online - ' + device_statuses[result.data.value.status]  + '!',
            });              
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 
    
    

    $scope.setDeviceGeneralSettings = function() {
        console.log("setDeviceGeneralSettings=");
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'timestamp'    : $scope.data.timestamp,
            'heartbeat'    : $scope.data.heartbeat,
            'version'      : $scope.data.version,
        };
       
        $state.go('deviceGeneralSettings', device_param);    
    };


    
    // RESTART DEVICE/START DEVICE/STOP DEVICE
    $scope.setDevice = function(devicename, status) {
        console.log("devicename=" + $scope.data.devicename);
        status_index = device_statuses.indexOf(status);
        $scope.set_status(devicename, { 'status': status_index }); 
    };
    
    $scope.set_status = function(devicename, param) {
        //
        // SET STATUS for RESTART DEVICE/START DEVICE/STOP DEVICE
        // - Request:
        //   POST /devices/device/<devicename>/status
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'status': int }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': {'status': int} }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + devicename + '/status',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device Status',
                template: 'Device is now ' + device_statuses[result.data.value.status]  + '!',
            });            
        })
        .catch(function (error) {
            $scope.handle_error(error);
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
            'serialnumber' : $scope.data.serialnumber,
            'deviceversion': $scope.data.version,
            'devicestatus' : "Last active: " + $scope.data.heartbeat,
            'location'     : "UNKNOWN",
        };

        $state.go('device', device_param);    
    };


    // DELETE DEVICE
    $scope.deleteDevice = function(devicename) {
        $ionicPopup.alert({
            title: 'Delete Device',
            template: 'Are you sure you want to delete this device - ' + devicename + '?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.deleteDeviceAction(devicename);
                    }
                }
            ]            
        });            
    };
    
    $scope.deleteDeviceAction = function(devicename) {
        console.log("deleteDeviceAction= " + devicename);
        
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
            url: server + '/devices/device/' + devicename,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $state.go('menu.devices', {'username': $scope.data.username, 'token': $scope.data.token});
        })
        .catch(function (error) {
            $scope.handle_error(error);
        });    
    };
    

    // UPGRADE DEVICE FIRMWARE
    $scope.upgradeDeviceFirmware = function() {
        console.log("upgradeDeviceFirmware= " + $scope.data.devicename);
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'timestamp'    : $scope.data.timestamp,
            'heartbeat'    : $scope.data.heartbeat,
            'version'      : $scope.data.version,
            'firmware'     : $scope.newfirmwareupdates
        };
       
        $state.go('oTAFirmwareUpdate', device_param);    
    };
    
    // VIEW DEVICE LOCATION
    $scope.viewDeviceLocation = function() {
        console.log("viewDeviceLocation= " + $scope.data.devicename);
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'timestamp'    : $scope.data.timestamp,
            'heartbeat'    : $scope.data.heartbeat,
            'version'      : $scope.data.version,
        };
       
        $state.go('viewDeviceLocation', device_param);    
    };

    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.get_latest_firmware();
    });   
    
    // EXIT PAGE
    $scope.exitPage = function() {
        var device_param = {
            'username': $scope.data.username,
            'token'   : $scope.data.token
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
}])
   
.controller('deviceGroupCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', 'DeviceGroups', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName


function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices, DeviceGroups) {

    var server = Server.rest_api;

    $scope.data = {
        'username'        : User.get_username(),
        'token'           : User.get_token(),
        'devicegroupname' : $state.params.devicegroupname,
    };

    $scope.devices = [ {"id":0, "devicename": ""} ];
    $scope.deviceSelected = -1;
    $scope.devicegroup = [];
    $scope.new_devicegroupname = $state.params.devicegroupname;


    // CHANGE DEVICENAME
    $scope.changeName = function(devicegroupname, new_devicegroupname) {
        if ($scope.data.devicegroupname === new_devicegroupname) {
            $ionicPopup.alert({ title: 'Error', template: 'Device group name is the same!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
        else {
            
            $ionicPopup.alert({
                title: 'Change Device Group Name',
                template: 'Are you sure you want to change the device group name from ' + devicegroupname + ' to ' + new_devicegroupname + '?',
                buttons: [
                    { 
                        text: 'No',
                        type: 'button-negative',
                        onTap: function(e) {
                            $scope.new_devicegroupname = devicegroupname;
                        }
                    },
                    {
                        text: 'Yes',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.new_devicegroupname = new_devicegroupname;
                            $scope.update_devicegroupname(devicegroupname, new_devicegroupname);
                        }
                    }
                ]            
            });            
        }
    };



    $scope.handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status >= 400 && error.status < 500) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!");
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    }; 


    // UPDATE DEVICE GROUP NAME
    $scope.update_devicegroupname = function(devicegroupname, new_devicegroupname) {
        //
        // UPDATE DEVICE GROUP NAME
        // - Request:
        //   POST /devicegroups/<devicegroupname>/name
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: {'new_groupname': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devicegroups/' + devicegroupname + '/name',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access, 'Content-Type': 'application/json' },
            data: {'new_groupname': new_devicegroupname}
        })
        .then(function (result) {
            console.log(result.data);
            
            $ionicPopup.alert({
                title: 'Change Device Group Name',
                template: 'Change Device Name Group was successful!',
            });
            
            $scope.data.devicegroupname = new_devicegroupname;
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 


    // DELETE DEVICE
    $scope.deleteDeviceGroup = function(devicegroupname) {
        $ionicPopup.alert({
            title: 'Delete Device Group',
            template: 'Are you sure you want to delete this device group - ' + devicegroupname + '?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.deleteDeviceGroupAction(devicegroupname);
                    }
                }
            ]            
        });            
    };
    
    $scope.deleteDeviceGroupAction = function(devicegroupname) {
        
        DeviceGroups.delete($scope.data, $scope.data.devicegroupname).then(function(res) {
            console.log(res);
            
            if (res.data !== null) {
                if (res.data.status === "OK") {
                    $ionicPopup.alert({
                        title: 'Success',
                        template: 'Device group deleted successfully!',
                        buttons: [
                            {
                                text: 'OK',
                                type: 'button-positive',
                                onTap: function(e) {
                                    $state.go('menu.devices', 
                                        {
                                            'username': $scope.data.username, 
                                            'token': $scope.data.token,
                                            'activeSection': "2"
                                        });
                                }
                            }
                        ]
                    });
                }
                else {
                    if (res.status == 409) {
                        $ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    else {
                        $ionicPopup.alert({ title: 'Error', template: 'Failed to process device group!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
            }
            else {
                console.log("ERROR: Server is down!"); 
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{ text: 'OK', type: 'button-assertive' }] });
            }
        });    
    };
    

    $scope.getDeviceGroup = function(devicegroupname) {
        
        DeviceGroups.get($scope.data, $scope.data.devicegroupname).then(function(res) {
            console.log("getDeviceGroups");
            console.log(res);
            
            if (res.data !== null) {
                if (res.data.status === "OK") {
                    $scope.devicegroup = [];
                    for (var device in res.data.devicegroup.devices) {
                        $scope.devicegroup.push({'devicename': res.data.devicegroup.devices[device], 'enabled': true});
                    }
                }
                else {
                    if (res.status == 409) {
                        $ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    else {
                        $ionicPopup.alert({ title: 'Error', template: 'Failed to process device group!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
            }
            else {
                console.log("ERROR: Server is down!"); 
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{ text: 'OK', type: 'button-assertive' }] });
            }
        });    
    };
 
    $scope.changeDevice = function(id) {
        $scope.deviceSelected = id;
        console.log("changeDevice");
        console.log($scope.deviceSelected);
    };
    
    $scope.addDeviceToDeviceGroup = function(devicegroupname) {
        console.log("addDeviceToDeviceGroup");
        console.log($scope.deviceSelected);
        if ($scope.deviceSelected === -1) {
            return;
        }
        devicename = $scope.devices[$scope.deviceSelected].devicename;
        console.log(devicename);
        
        DeviceGroups.add_device($scope.data, $scope.data.devicegroupname, devicename).then(function(res) {
            console.log(res);
            
            if (res.data !== null) {
                if (res.data.status === "OK") {
                    $ionicPopup.alert({ title: 'Device Group', template: 'Device was added to device group successfully!', buttons: [{text: 'OK', type: 'button-positive'}] });
                    $scope.getDeviceGroup($scope.data.devicegroupname);
                }
                else {
                    if (res.status === 409 || res.status === 400) {
                        $ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
            }
            else {
                console.log("ERROR: Server is down!"); 
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{ text: 'OK', type: 'button-assertive' }] });
            }
        });    
    };

    $scope.setDevicesToDeviceGroup = function(devicegroupname) {
        console.log("setDevicesToDeviceGroup");
        var devices = [];
        for (var device in $scope.devicegroup) {
            if ($scope.devicegroup[device].enabled === true) {
                devices.push($scope.devicegroup[device].devicename);
            }
        }

        DeviceGroups.set_devices($scope.data, $scope.data.devicegroupname, devices).then(function(res) {
            console.log(res);
            
            if (res.data !== null) {
                if (res.data.status === "OK") {
                    $ionicPopup.alert({ title: 'Device Group', template: 'Devices was set to device group successfully!', buttons: [{text: 'OK', type: 'button-positive'}] });
                    $scope.getDeviceGroup($scope.data.devicegroupname);
                }
                else {
                    if (res.status === 409 || res.status === 400) {
                        $ionicPopup.alert({ title: 'Error', template: res.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
            }
            else {
                console.log("ERROR: Server is down!"); 
                $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{ text: 'OK', type: 'button-assertive' }] });
            }
        });    
    };
    
    $scope.getDevices = function() {
        Devices.fetch($scope.data, "").then(function(res) {
            $scope.data.token = User.get_token();
            
            // populate the list of devices
            $scope.devices = res;
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            if ($scope.devices.length > 0) {
                $scope.deviceSelected = 0;
            }
            
            $scope.getDeviceGroup($scope.data.devicegroupname);
        });
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.devicegroup = [];
        $scope.deviceSelected = -1;
        $scope.devices = [ {"id":0, "devicename": ""} ];
        $scope.getDevices();
    });   
    
    // EXIT PAGE
    $scope.exitPage = function() {
        var device_param = {
            'username': $scope.data.username,
            'token'   : $scope.data.token,
            'activeSection': '2',
        };
        $state.go('menu.devices', device_param, {reload: true});
    };
}])
   
.controller('deviceLocationCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', 'uiGmapGoogleMapApi', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName


function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices, uiGmapGoogleMapApi) {

    var server = Server.rest_api;

    $scope.data = {
        'username'      : User.get_username(),
        'token'         : User.get_token(),
        'devicename'    : $stateParams.devicename,
        'deviceid'      : $stateParams.deviceid,
        'serialnumber'  : $stateParams.serialnumber,
        'devicestatus'  : $stateParams.devicestatus,
        'deviceversion' : $stateParams.deviceversion,
        'location'      : $stateParams.location,
        'devicelocation': $stateParams.location,
        'zoom': 18,
        
        'locations': []
    };

    $scope.devices = [{"devicename": "All devices"}];

    $scope.timer = null;
    $scope.run_time = 0;
    $scope.refresh_time = 5;
    
    
    $scope.handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status >= 400 && error.status < 500) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!");
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    }; 


    $scope.changeDevice = function(devicename) {
        for (indexy=0; indexy<$scope.devices.length; indexy++) {
            if (devicename === $scope.devices[indexy].devicename) {
                $scope.data.devicename = $scope.devices[indexy].devicename;
                if ($scope.data.devicename !== "All devices") {
                    $scope.data.deviceid = $scope.devices[indexy].deviceid;
                    $scope.data.serialnumber = $scope.devices[indexy].serialnumber;
                    $scope.data.devicestatus = $scope.devices[indexy].devicestatus;
                    $scope.data.version = $scope.devices[indexy].version;
                }
                //$scope.map = null;
                $scope.markers = [];
                
                $scope.getDeviceLocation($scope.data.devicename);
                break;
            }
        }
    };
    
    $scope.get_devices = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            console.log($scope.devices);
            $scope.devices = $scope.devices.concat(res);

            console.log($scope.devices);
            $scope.data.token = User.get_token();

            if ($scope.data.devicename !== $stateParams.devicename) {
                $scope.data.devicename = $stateParams.devicename;
                $scope.changeDevice($scope.data.devicename);
            }
            else {
                $scope.getDeviceLocation($scope.data.devicename);
            }
        });
    };



    

    // GET DEVICE LOCATION
    $scope.getDeviceLocation = function(devicename) {
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            console.log("clearTimeout");
            $scope.timer = null;
        }
        
        if (devicename === "All devices") {
            $scope.get_devices_location();
        }
        else {
            $scope.get_device_location(devicename);
        }
    };

    // GET DEVICES LOCATION
    $scope.get_devices_location = function() {
        //console.log("get_devices_location ");
        //
        // GET DEVICES LOCATION
        // - Request:
        //   GET /devices/location
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'locations': ['devicename': string, 'location:{'latitude': float, 'longitude': float}, ...] }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access },
        })
        .then(function (result) {
            console.log("xxx");
            console.log(result.data);
            
            if ( result.data.locations === undefined ) {
                $ionicPopup.alert({ 
                    title: 'No location set yet', 
                    template: 'Using Bridgetek office as default location!', 
                    buttons: [{text: 'OK', type: 'button-assertive'}] });

                // set SG office as default location
                result.data.locations = [];
                
                for (let indexy=0; indexy<$scope.devices.length; indexy++)
                {
                    if ($scope.devices[indexy].devicename !== "All devices") {
                        result.data.locations.push({
                            'devicename': $scope.devices[indexy].devicename,
                            'location': {
                                'latitude': 1.33000,
                                'longitude': 103.89000
                            }
                        });
                    }
                }
                
                //console.log(result.data.locations);
            }           

            if (result.data.locations !== undefined) {
                ///$scope.data.locations = result.data.locations;
                //console.log("xxx");
                //console.log($scope.data.locations);
                for (var location in result.data.locations) {
                    $scope.data.locations.push({
                        'devicename': result.data.locations[location].devicename,
                        'location': {
                            "latitude": result.data.locations[location].location.latitude, 
                            "longitude": result.data.locations[location].location.longitude
                        }
                    });
                }
                //console.log($scope.data.locations);
             
                // find the center
                var center = {'latitude': 0, 'longitude':0};
                for (let indexy=0; indexy<$scope.data.locations.length; indexy++)
                {
                    center.latitude += $scope.data.locations[indexy].location.latitude;
                    center.longitude += $scope.data.locations[indexy].location.longitude;
                }
                center.latitude /= $scope.data.locations.length;
                center.longitude /= $scope.data.locations.length;
                //console.log(center);
             
                //$scope.infowindow = new google.maps.InfoWindow();
                
                // uiGmapGoogleMapApi is a promise.
                // The "then" callback function provides the google.maps object.
                uiGmapGoogleMapApi.then(function(maps) {
                    
                    // Configuration needed to display the road-map with traffic
                    // Displaying Ile-de-france (Paris neighbourhood)
                    $scope.map = {
                        center: center,
                        zoom: $scope.data.zoom,
                        options: {
                            mapTypeId: google.maps.MapTypeId.ROADMAP, // This is an example of a variable that cannot be placed outside of uiGmapGooogleMapApi without forcing of calling the google.map helper outside of the function
                            streetViewControl: true, // streetview
                            mapTypeControl: true, // satellite
                            scaleControl: true,
                            rotateControl: true,
                            zoomControl: true,
                            panControl: true
                        }, 
                        showTraficLayer:false
                    };

                    $scope.windowOptions = {
                        show: false
                    };

                    // add markers
                    $scope.markers = [];
                    for (var indexy=0; indexy<$scope.data.locations.length; indexy++)
                    {
                        $scope.markers.push({
                            id: $scope.data.locations[indexy].devicename,
                            coords: $scope.data.locations[indexy].location,
                            data: $scope.data.locations[indexy].devicename,
                            options: { draggable: false, animation: google.maps.Animation.DROP },
                            icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
                            //draggable: true
                        });
                    }

                    $scope.getFit = function() {
                      return true;  
                    };
                    
                    $scope.onClickMarker = function(marker, eventName, markerobj) {
                        console.log("onClickMarker");
                        //alert(markerobj.data);
                        $scope.windowOptions.show = !$scope.windowOptions.show;
                        $scope.selectedCoords = markerobj.coords;
                        $scope.info = markerobj.data;                        
                    };

                    $scope.onCloseClick = function () {
                        $scope.windowOptions.show = false;
                    };                    
                });
            }
            
            $scope.get_statuses();
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 

    // GET DEVICE LOCATION
    $scope.get_device_location = function(devicename) {
        console.log("get_device_location " + devicename);
        //
        // GET DEVICE LOCATION
        // - Request:
        //   GET /devices/device/DEVICENAME/location
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'location': {'latitude': float, 'longitude': float} }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + devicename + '/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            
            // if no coordinates yet, use SG office as defaut address
            if ( result.data.location === undefined ||
                (result.data.location !== undefined && (result.data.location.latitude === 0 && result.data.location.longitude === 0)) ) {

                // set SG office as default location
                result.data.location = {
                    'latitude': 1.33000,
                    'longitude': 103.89000
                };
                
                $ionicPopup.alert({ title: 'No location set yet', template: 'Using Bridgetek office as default location!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else {
                $scope.data.devicelocation.latitude = result.data.location.latitude;
                $scope.data.devicelocation.longitude = result.data.location.longitude;
            }
            
            if (result.data.location !== undefined) {
                $scope.data.location = {};
                $scope.data.location.latitude = result.data.location.latitude;
                $scope.data.location.longitude = result.data.location.longitude;
             
                
                uiGmapGoogleMapApi.then(function(maps){
                    $scope.map = {
                        center: $scope.data.location,
                        zoom: $scope.data.zoom,
                        options: {
                            mapTypeId: google.maps.MapTypeId.ROADMAP, // This is an example of a variable that cannot be placed outside of uiGmapGooogleMapApi without forcing of calling the google.map helper outside of the function
                            streetViewControl: true, // streetview
                            mapTypeControl: true, // satellite
                            scaleControl: true,
                            rotateControl: true,
                            zoomControl: true,
                            panControl: true
                        }, 
                        showTraficLayer:false
                    };
                    
                    $scope.windowOptions = {
                        show: false
                    };

                    // add markers
                    $scope.markers = [{
                        id: $scope.data.devicename,
                        coords: $scope.data.location,
                        data: [],
                        options: { draggable: true, animation: google.maps.Animation.DROP },
                        icon: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
                    }];
                    
                    $scope.getFit = function() {
                        return false;  
                    };

                    $scope.onClickMarker = function(marker, eventName, markerobj) {
                        $scope.windowOptions.show = !$scope.windowOptions.show;
                        $scope.selectedCoords = markerobj.coords;
                        $scope.info = markerobj.id;
                    };

                    $scope.onCloseClick = function () {
                        $scope.windowOptions.show = false;
                    };
                    
                });
            }
            
            $scope.get_status($scope.data.devicename);
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 


    $scope.get_status = function(devicename) {
        //$scope.data.devicestatus = 'Status: Detecting...';
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
            //console.log(result.data.status === "OK");
            for (var marker in $scope.markers) {
                if ($scope.markers[marker].id === devicename) {
                    $scope.markers[marker].icon = "https://maps.google.com/mapfiles/ms/icons/green-dot.png";
                    break;
                }
            }
        })
        .catch(function (error) {
        }); 
    };
    
    $scope.get_statuses = function() {
        //$scope.data.devicestatus = 'Status: Detecting...';
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
            url: server + '/devices/status',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            //console.log(result.data.devices);
            
            for (var marker in $scope.markers) {
                //console.log($scope.markers[marker].id);
                
                for (var device in result.data.devices) {
                    if ($scope.markers[marker].id === result.data.devices[device].devicename) {
                        //console.log(result.data.devices[device].devicename);
                        if (result.data.devices[device].status !== undefined) {
                            $scope.markers[marker].icon = "https://maps.google.com/mapfiles/ms/icons/green-dot.png";
                            //console.log(true);
                        }
                        else {
                            $scope.markers[marker].icon = "https://maps.google.com/mapfiles/ms/icons/red-dot.png";
                            //console.log(false);
                        }
                        break;
                    }
                }
            }
        })
        .catch(function (error) {
        }); 
    };
    
    // SET DEVICE LOCATION
    $scope.setDeviceLocation = function(devicename) {
        if (devicename === "All devices") {
            $scope.set_devices_location();
        }
        else {
            $scope.set_device_location(devicename);
        }
    };

    // SET DEVICES LOCATION
    $scope.set_devices_location = function() {
        console.log("set_devices_location ");
        //
        // SET DEVICES LOCATION
        // - Request:
        //   POST /devices/location
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: { 'locations': [{devicename: string, location: {'latitude': float, 'longitude': float}}, ...] }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'locations': $scope.data.locations }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({ title: 'Device location', template: 'Devices locations have been saved!', buttons: [{text: 'OK', type: 'button-positive'}] });
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 

    // SET DEVICE LOCATION
    $scope.set_device_location = function(devicename) {
        console.log("set_device_location " + devicename);
        //
        // SET DEVICE LOCATION
        // - Request:
        //   POST /devices/device/DEVICENAME/location
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: { 'latitude': float, 'longitude': float }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + devicename + '/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.location
        })
        .then(function (result) {
            console.log(result.data);
            console.log($scope.data.location);
            console.log($scope.data.devicelocation);
            $scope.data.devicelocation.latitude = $scope.data.location.latitude;
            $scope.data.devicelocation.longitude = $scope.data.location.longitude;
            $ionicPopup.alert({ title: 'Device location', template: 'Device location has been saved!', buttons: [{text: 'OK', type: 'button-positive'}] });
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 



    // DELETE DEVICE LOCATION
    $scope.deleteDeviceLocation = function(devicename) {
        if (devicename === "All devices") {
            $scope.delete_devices_location();
        }
        else {        
            $scope.delete_device_location(devicename);
        }
    };

    // DELETE DEVICES LOCATION
    $scope.delete_devices_location = function() {
        console.log("delete_devices_location ");
        //
        // DELETE DEVICES LOCATION
        // - Request:
        //   DELETE /devices/location
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'DELETE',
            url: server + '/devices/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({ 
                title: 'Device location', 
                template: 'Devices locations have been deleted!', 
                buttons: [{
                    text: 'OK', 
                    type: 'button-positive', 
                    onTap: function(e) {
                        $scope.get_devices_location();
                    }
                }] 
            });
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 

    // DELETE DEVICE LOCATION
    $scope.delete_device_location = function(devicename) {
        console.log("delete_device_location " + devicename);
        //
        // DELETE DEVICE LOCATION
        // - Request:
        //   DELETE /devices/device/DEVICENAME/location
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + devicename + '/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({ 
                title: 'Device location', 
                template: 'Device location has been deleted!', 
                buttons: [{
                    text: 'OK', 
                    type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.location.latitude = 0;
                        $scope.data.location.longitude = 0;                        
                        $scope.get_device_location(devicename);
                    }
                }] 
            });
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    }; 


    get_all_device_sensors_enabled_input = function() {
        if ($scope.data.devicename === "All devices") {
            return;
        }
        
        //
        // GET ALL ENABLED DEVICE SENSORS (enabled input)
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/sensors/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/sensors/readings',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            
            console.log($scope.markers);
            for (var marker in $scope.markers) {
                console.log($scope.markers[marker].id);
                if ($scope.data.devicename === $scope.markers[marker].id) {
                    $scope.markers[marker].data = result.data.sensors;
                    //$scope.sensornames = [];
                    //for (var sensor in result.data.sensors) {
                    //    $scope.sensornames.push(result.data.sensors[sensor].sensorname);
                    //}

                    $scope.windowParams = {
                        sensors: $scope.markers[marker].data,
                        //doIt: function() {
                        //  return $scope.doIt()
                        //}
                    }
                    /*
                    var data = $scope.markers[marker].id;
                    for (var sensor in result.data.sensors) {
                        data += "\n" + result.data.sensors[sensor].sensorname;
                    }
                    $scope.markers[marker].data = data;
                    */
                    console.log($scope.markers[marker].data);
                    break;
                }
            }
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    };
    
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.timer = null;
        $scope.run_time = 0;
        $scope.devices = [{"devicename": "All devices"}];
        $scope.get_devices();
    });
    
    $scope.$on('$ionicView.beforeLeave', function(e) {
        console.log("beforeLeave");
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            console.log("clearTimeout");
            $scope.timer = null;
        }
        $scope.run_time = 0;
    });
    
    
    // VIEW DEVICE
    $scope.viewDevice = function() {
        console.log("viewDevice= " + $scope.data.devicename);
        
        if ($scope.data.devicename === "All devices") {
            let device_param = {
                'username': $scope.data.username,
                'token'   : $scope.data.token
            };
            $state.go('menu.devices', device_param, {reload: true});
            return;    
        }

        /*
        var device_param = {
            'username'      : $scope.data.username,
            'token'         : $scope.data.token,
            'devicename'    : $scope.data.devicename,
            'deviceid'      : $scope.data.deviceid,
            'serialnumber'  : $scope.data.serialnumber,
            'devicestatus'  : $scope.data.devicestatus,
            'deviceversion' : $scope.data.deviceversion,
            'location'      : $scope.data.devicelocation,
        };
        console.log("viewDevice");
        console.log($scope.data.devicelocation.latitude);
        console.log($scope.data.devicelocation.longitude);
        $state.go('device', device_param, {reload: true});    
        */

        let device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'timestamp'    : $scope.data.timestamp,
            'heartbeat'    : $scope.data.heartbeat,
            'version'      : $scope.data.version,
        };
        $state.go('viewDevice', device_param);    
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
   
.controller('oTAFirmwareUpdateCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName


function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'timestamp'   : $stateParams.timestamp,
        'heartbeat'   : $stateParams.heartbeat,
        'version'     : $stateParams.version,
        'firmwares'   : $stateParams.firmware
    };

    $scope.ota_status = {
        'version': '',
        'status': '',
        'time': '',
        'timestamp': '',
    };
    
    $scope.disable = false;
    $scope.timer = null;
    $scope.runtime = 0;
    $scope.runtime_max = 300; // 5 minutes

    $scope.versiontouse = $stateParams.firmware.ft900.latest;
    $scope.descriptiontouse = [];
    $scope.datetouse = "";

    $scope.devices = [{"devicename": "All devices"}];
    $scope.devices_ota = [];
    

    $scope.changeDescription = function(version) {
        console.log("changeDescription " + version);
        for (var indexy=0; indexy<$scope.data.firmwares.ft900.firmware.length; indexy++) {
            console.log($scope.data.firmwares.ft900.firmware[indexy]);
            if ($scope.data.firmwares.ft900.firmware[indexy].version === version) {
                $scope.descriptiontouse = $scope.data.firmwares.ft900.firmware[indexy].description;
                $scope.datetouse = $scope.data.firmwares.ft900.firmware[indexy].date;
                console.log("changeDescription " + $scope.descriptiontouse);
                break;
            }
        }
    };

    $scope.handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                //$ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status >= 400 && error.status < 500) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!");
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    }; 

    $scope.onChecked = function(device) {
        console.log("onChecked " + device.devicename + " " + device.checked);
    };

    $scope.changeDevice = function(devicename) {
        for (indexy=0; indexy<$scope.devices.length; indexy++) {
            if (devicename === $scope.devices[indexy].devicename) {
                $scope.data.devicename = $scope.devices[indexy].devicename;
                if ($scope.data.devicename !== "All devices") {
                    $scope.data.deviceid = $scope.devices[indexy].deviceid;
                    $scope.data.serialnumber = $scope.devices[indexy].serialnumber;
                    $scope.data.devicestatus = $scope.devices[indexy].devicestatus;
                    if ($scope.devices[indexy].version === undefined) {
                        $scope.data.version = "UNKNOWN";
                    }
                    else {
                        $scope.data.version = $scope.devices[indexy].version;
                    }
                    //$scope.query_device(devicename);
                    $scope.get_ota_status($scope.versiontouse, $scope.data.devicename);
                }
                else {
                    $scope.get_ota_statuses($scope.versiontouse);
                }
                break;
            }
        }
    };
    
    $scope.get_devices = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = $scope.devices.concat(res);

            console.log($scope.devices);
            $scope.data.token = User.get_token();

            
            $scope.changeDescription($scope.versiontouse);

            console.log($scope.data.devicename);
            if ($scope.data.devicename !== "All devices") {
                $scope.get_ota_status($scope.versiontouse, $scope.data.devicename);
            }
            else {
                $scope.get_ota_statuses($scope.versiontouse);                
            }
        });
    };



    $scope.get_ota_statuses = function(version) {
        //
        // GET OTA STATUSES
        // - Request:
        //   GET /devices/ota
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { "status": string, "version": string } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/ota',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.devices_ota = result.data.ota;
            
            if ($scope.timer !== null) {
            
                for (let device in $scope.devices_ota) {
                    $scope.devices_ota[device].checked = false;
                }
            
                var has_ongoing = false;
                var has_pending = false;
                var has_completed = false;
                for (let device in $scope.devices_ota) {
                    console.log($scope.devices_ota[device]);
                    if ($scope.devices_ota[device].status === "pending") {
                        has_pending = true;
                    }
                    else if ($scope.devices_ota[device].status === "ongoing") {
                        has_ongoing = true;
                        break;
                    }
                    else if ($scope.devices_ota[device].status === "completed") {
                        has_completed = true;
                    }
                }
                
                if (has_ongoing === false) {
                    if ($scope.timer !== null) {
                        clearTimeout($scope.timer);
                        $scope.timer = null;
                    }
                    $scope.runtime = 0;
                    $scope.disable = false;
                    
                    var template = '';
                    if (has_completed === true && has_pending === true) {
                        template = 'Updating the firmware of selected online devices to version ' + version + ' was completed! All selected devices that are offline have been scheduled for update upon device bootup.';
                    }
                    else if (has_completed === false && has_pending === true) {
                        template = 'Updating the firmware of all devices to version ' + version + ' was pended! All devices are offline and have been scheduled for update upon device bootup.';
                    }
                    else {
                        template = 'Updating the firmware of all devices to version ' + version + ' was completed!';
                    }
                    $ionicPopup.alert({
                        title: 'OTA Firmware Update',
                        template: template
                    });            
                }
                else {
                    $scope.runtime += 1;
                    if ($scope.runtime >= $scope.runtime_max) {
                        if ($scope.timer !== null) {
                            clearTimeout($scope.timer);
                            $scope.timer = null;
                        }
                        $scope.runtime = 0;
                        $scope.disable = false;
                    }
                }
            }
            else {
                for (let device in $scope.devices_ota) {
                    $scope.devices_ota[device].checked = true;
                }
            }
        })
        .catch(function (error) {
            $scope.disable = false;
            $scope.handle_error(error);
        }); 
    };

    $scope.get_ota_status = function(version) {
        console.log("get_ota_status");
        //
        // GET OTA STATUS
        // - Request:
        //   GET /devices/device/<devicename>/ota
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/ota',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.ota_status = result.data.ota;
            if ($scope.ota_status.timestamp !== "n/a") {
                let timestamp = new Date($scope.ota_status.timestamp * 1000); 
                $scope.ota_status.timestamp = "" + timestamp;
            }
            
            if ($scope.disable) {
                if (result.data.ota.status !== "ongoing") {
                    if ($scope.timer !== null) {
                        clearTimeout($scope.timer);
                        $scope.timer = null;
                    }
                    $scope.runtime = 0;
                    $scope.disable = false;
                    
                    $ionicPopup.alert({
                        title: 'OTA Firmware Update',
                        template: 'Updating the firmware of this device - ' + $scope.data.devicename + ' - to version ' + version + ' was ' + result.data.ota.status + '!',
                        buttons: [
                            {
                                text: 'OK',
                                type: 'button-positive',
                                onTap: function(e) {
                                    $scope.data.version = version;
                                    //$scope.get_devices();
                                }
                            }
                        ]            
                    });            
                }
                else {
                    $scope.runtime += 1;
                    if ($scope.runtime >= $scope.runtime_max) {
                        if ($scope.timer !== null) {
                            clearTimeout($scope.timer);
                            $scope.timer = null;
                        }
                        $scope.runtime = 0;
                        $scope.disable = false;
                    }
                }
            }
        })
        .catch(function (error) {
            $scope.handle_error(error);
            
            if ($scope.timer !== null) {
                clearTimeout($scope.timer);
                $scope.timer = null;
            }
            $scope.runtime = 0;
            $scope.disable = false;
            
            $ionicPopup.alert({
                title: 'OTA Firmware Update',
                template: 'Updating the firmware of this device - ' + $scope.data.devicename + ' failed!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive'
                    }
                ]            
            });            
            
        }); 
    };


    $scope.queryDevice = function(devicename) {
        if ($scope.data.devicename !== "All devices") {
            $scope.query_device(devicename);
        }
        else {
            $scope.get_ota_statuses();
        }        
    };

    $scope.query_device = function(devicename) {
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
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    };    


    $scope.cancelFirmware = function() {
        
        var prompt = 'Are you sure you want to cancel the firmware update?';
        
        $ionicPopup.alert({
            title: 'OTA Firmware Update',
            template: prompt,
            buttons: [
                { 
                    text: 'No',
                    type: 'button-negative',
                },
                {
                    text: 'Yes',
                    type: 'button-positive',
                    onTap: function(e) {
                        
                        if ($scope.timer !== null) {
                            clearTimeout($scope.timer);
                            $scope.timer = null;
                        }
                        $scope.runtime = 0;
                        $scope.disable = false;
                    }
                }
            ]            
        });            
        
    };


    $scope.upgradeFirmware = function(version, devicename) {

        // Note: Device can be offline    
        var prompt = '';
        
        if (devicename === "All devices") {
            
            var devices = [];
            for (let device in $scope.devices_ota) {
                if ($scope.devices_ota[device].checked) {
                    devices.push($scope.devices_ota[device].devicename);
                }
            }
    
            if (devices.length === 0) {
                prompt = 'No device is selected. Please select 1 or more devices.';
                $ionicPopup.alert({
                    title: 'Error',
                    template: prompt
                });
                return;
            }

            prompt = 'Are you sure you want to update the firmware of selected devices to version ' + version + '?';
            $ionicPopup.alert({
                title: 'OTA Firmware Update',
                template: prompt,
                buttons: [
                    { 
                        text: 'No',
                        type: 'button-negative',
                    },
                    {
                        text: 'Yes',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.disable = true;
                            $scope.upgrade_firmwares(version, devices);
                        }
                    }
                ]            
            });            
        }
        else {
            if ($scope.data.version > version) {
                prompt = 'Are you sure you want to downgrade the firmware of this device - ' + devicename + ' - to version ' + version + '?';
            }
            else if ($scope.data.version < version) {
                prompt = 'Are you sure you want to upgrade the firmware of this device - ' + devicename + ' - to version ' + version + '?';
                if (version != $scope.data.firmwares.ft900.latest) {
                    prompt += ' The latest version is ' + $scope.data.firmwares.ft900.latest + '.';
                }
            }
            else {
                prompt = 'Are you sure you want to update the firmware of this device - ' + devicename + ' - to version ' + version + '? The current version of the device is the same.';
            }
            
            $ionicPopup.alert({
                title: 'OTA Firmware Update',
                template: prompt,
                buttons: [
                    { 
                        text: 'No',
                        type: 'button-negative',
                    },
                    {
                        text: 'Yes',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.disable = true;
                            $scope.upgrade_firmware(version, devicename);
                        }
                    }
                ]            
            });            
        }    
    };

    $scope.upgrade_firmware = function(version, devicename) {
        //
        // UPGRADE DEVICE FIRMWARE
        // - Request:
        //   POST /devices/device/<devicename>/firmware
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + devicename + '/firmware',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access, 'Content-Type': 'application/json'},
            data: { 'version': version }
        })
        .then(function (result) {
            console.log(result.data);

            if (result.data.status === "OK") {
                if ($scope.timer !== null) {
                    clearTimeout($scope.timer);
                    $scope.timer = null;
                }
    
                $scope.runtime = 0;
                //$scope.timer = setInterval($scope.get_upgrade_firmware, 1000, version);
                $scope.timer = setInterval($scope.get_ota_status, 1000, version);
            }
            else {
                $scope.disable = false;
                $ionicPopup.alert({ title: 'Error', template: result.data.message, buttons: [{text: 'OK', type: 'button-positive'}] });
            }
        })
        .catch(function (error) {
            $scope.disable = false;
            $scope.handle_error(error);
        }); 
    };    

    $scope.upgrade_firmwares = function(version, devices_list) {
        
        var param = { 'version': version };
        if (devices_list.length > 0) {
            param.devices = devices_list;
        }
        
        //
        // UPGRADE FIRMWARES
        // - Request:
        //   POST /devices/firmwares
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/firmware',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access, 'Content-Type': 'application/json'},
            data: param
        })
        .then(function (result) {
            console.log(result.data);

            if (result.data.status === "OK") {
                if ($scope.timer !== null) {
                    clearTimeout($scope.timer);
                    $scope.timer = null;
                }
    
                $scope.runtime = 0;
                //$scope.timer = setInterval($scope.get_upgrade_firmware, 1000, version);
                $scope.timer = setInterval($scope.get_ota_statuses, 1000, version);
            }
            else {
                $scope.disable = false;
                $ionicPopup.alert({ title: 'Error', template: result.data.message, buttons: [{text: 'OK', type: 'button-positive'}] });
            }
        })
        .catch(function (error) {
            $scope.disable = false;
            $scope.handle_error(error);
        }); 
    };    

    $scope.get_upgrade_firmware = function(version) {
        console.log("get_upgrade_firmware");
        //
        // GET UPGRADE DEVICE FIRMWARE
        // - Request:
        //   GET /devices/device/<devicename>/firmware
        //
        // - Response:
        //   { 'status': 'OK', 'message': string}
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/firmware',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            console.log(result.data.result);
            if (result.data.result !== "ongoing") {
                if ($scope.timer !== null) {
                    clearTimeout($scope.timer);
                    $scope.timer = null;
                }
                $scope.runtime = 0;
                
                $ionicPopup.alert({
                    title: 'OTA Firmware Update',
                    template: 'Updating the firmware of this device - ' + $scope.data.devicename + ' - to version ' + version + ' was ' + result.data.result + '!',
                    buttons: [
                        {
                            text: 'OK',
                            type: 'button-positive',
                            onTap: function(e) {
                                $scope.data.version = version;
                                //$scope.get_devices();
                            }
                        }
                    ]            
                });            
            }
            else {
                $scope.runtime += 1;
                if ($scope.runtime >= $scope.runtime_max) {
                    if ($scope.timer !== null) {
                        clearTimeout($scope.timer);
                        $scope.timer = null;
                    }
                    $scope.runtime = 0;
                }
            }
        })
        .catch(function (error) {
            $scope.handle_error(error);
            
            if ($scope.timer !== null) {
                clearTimeout($scope.timer);
                $scope.timer = null;
            }
            $scope.runtime = 0;
            
            $ionicPopup.alert({
                title: 'OTA Firmware Update',
                template: 'Updating the firmware of this device - ' + $scope.data.devicename + ' failed!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive'
                    }
                ]            
            });            
            
        }); 
    };    


    $scope.$on('$ionicView.enter', function(e) {
        $scope.devices = [{"devicename": "All devices"}];
        $scope.devices_ota = [];
        $scope.disable = false;
        $scope.timer = null;
        console.log("xxxxxxxxxx " + $scope.data.version);
        $scope.get_devices();
    });

    $scope.$on('$ionicView.beforeLeave', function(e) {
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            $scope.timer = null;
        }
        $scope.runtime = 0;
    });   


    // VIEW DEVICE
    $scope.viewDevice = function() {
        console.log("viewDevice= " + $scope.data.devicename);
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'timestamp'    : $scope.data.timestamp,
            'heartbeat'    : $scope.data.heartbeat,
            'version'      : $scope.data.version,
        };
       
        $state.go('viewDevice', device_param);    
    };    
    
    // EXIT PAGE
    $scope.exitPage = function() {
        
        if ($scope.data.devicename !== "All devices") {

            var device_param = {
                'username'     : $scope.data.username,
                'token'        : $scope.data.token,
                'devicename'   : $scope.data.devicename,
                'deviceid'     : $scope.data.deviceid,
                'serialnumber' : $scope.data.serialnumber,
                'timestamp'    : $scope.data.timestamp,
                'heartbeat'    : $scope.data.heartbeat,
                'version'      : $scope.data.version,
            };
           
            $state.go('viewDevice', device_param); 
        
            /*
            let device_param = {
                'username': User.get_username(),
                'token': User.get_token(),
                'devicename': $scope.data.devicename,
                'deviceid': $scope.data.deviceid,
                'serialnumber': $scope.data.serialnumber,
                'devicestatus': "Last active: " + $scope.data.heartbeat,
                'deviceversion': $scope.data.version,
            };
    
            $state.go('device', device_param, {reload:true} );
            */
        }
        else {
            
            let device_param = {
                'username': User.get_username(),
                'token': User.get_token()
            };
    
            $state.go('menu.devices', device_param, {reload:true} );        
        }
    };
}])
   
.controller('deviceGeneralSettingsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
        'version'     : $stateParams.version
    };

    $scope.settings =  {
        'sensorrate'  : 5,
    };


    // GET SETTINGS
    $scope.getSettings = function(devicename) {
        get_settings(devicename);
    };

    get_settings = function(devicename) {
        //
        // GET SETTINGS
        // - Request:
        //   GET /devices/device/<devicename>/settings
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { "sensorrate": int } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + devicename + '/settings',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.settings = result.data.value;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    }; 


    // SET SETTINGS
    $scope.setSettings = function(devicename) {
        set_settings(devicename); 
    };
    
    set_settings = function(devicename) {
        //
        // SET SETTINGS
        // - Request:
        //   POST /devices/device/<devicename>/settings
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'status': int }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + devicename + '/settings',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json'},
            data: $scope.settings
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device Settings',
                template: 'Device settings has been applied successully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    
    // DELETE PROPERTIES
    $scope.deleteProperties = function(devicename) {
        delete_properties(devicename); 
    };
    
    delete_properties = function(devicename) {
        //
        // DELETE PROPERTIES
        // - Request:
        //   DELETE /devices/device/<devicename>/sensors/properties
        //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
        //   data: { 'status': int }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //        
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + devicename + '/sensors/properties',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device Sensor Properties',
                template: 'Device sensor properties has been reseted/cleared successully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    
    $scope.exitPage = function() {
        console.log("setDeviceGeneralSettings=");
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'timestamp'    : $scope.data.timestamp,
            'heartbeat'    : $scope.data.heartbeat,
            'version'      : $scope.data.version,
        };
       
        $state.go('viewDevice', device_param);    
    };
    
    $scope.getSettings($scope.data.devicename);
}])
   
.controller('deviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
        'devicestatus': $stateParams.devicestatus,
        'deviceversion': $stateParams.deviceversion,
        'location': $state.params.location,
        'devicelocation': $state.params.location !== "UNKNOWN" && $state.params.location !== undefined ? $state.params.location.latitude.toFixed(4) + "... , " + $state.params.location.longitude.toFixed(4) + "..." : "UNKNOWN",
        'status': $stateParams.devicestatus,
    };
    $scope.treeData = null;

    console.log("xxx " + $scope.data.devicename);

    $scope.submitDashboard = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('menu.sensorDashboard', $scope.data, {animate: false} );
    };   

    $scope.submitGPIO = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceGPIO', $scope.data, {animate: false} );
    };   

    $scope.submitUART = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceUART', $scope.data, {animate: false} );
    };    

    $scope.submitI2C = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceI2C', $scope.data, {animate: false} );
    };

    $scope.submitADC = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceADC', $scope.data, {animate: false} );
    };

    $scope.submit1WIRE = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('device1WIRE', $scope.data, {animate: false} );
    };

    $scope.submitTPROBE = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceTPROBE', $scope.data, {animate: false} );
    };

    $scope.submitNotifications = function() {
        console.log("devicename=" + $scope.data.devicename);
        $state.go('deviceNotifications', $scope.data, {animate: false} );
    };

    $scope.submitTODO = function() {
        console.log("devicename=" + $scope.data.devicename);
        //if ($scope.data.devicestatus === 'Status: UNKNOWN') {
        //    return;
        //}
        $ionicPopup.alert({ title: 'Error', template: 'Not yet supported!', buttons: [{text: 'OK', type: 'button-assertive'}] });
    };


    $scope.handle_error = function(error) {
        // Handle failed login
        if (error.data !== null) {
            console.log("ERROR: Control Device failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    // GET STATUS
    $scope.getStatus = function(devicename) {
        $scope.get_status(devicename);
    };

    $scope.get_status = function(devicename) {
        console.log("get_status " + devicename);
        //$scope.data.devicestatus = 'Status: Detecting...';
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
            //console.log("OK XXXXXXXXXXXXXXXXXXX");
            console.log(result.data);
        
            if (result.data.status === "OK") {
                $scope.data.status = 'Online';
            }
            else {
                $scope.data.status = 'Offline';
            }
            if (result.data.value !== undefined) {
                $scope.data.deviceversion = result.data.value.version;
            }
            
            $scope.get_hierarchy($scope.data.devicename, 1, 1);
        })
        .catch(function (error) {
            //console.log("ERRORXXXXXXXXXXXXXXXXXXXXXXXXXXX get_status");
            console.log($scope.data);
            $scope.data.status = 'Offline';
            
            if (error.data.value !== undefined) {
                $scope.data.deviceversion = error.data.value.version;
            }
            
            $scope.get_hierarchy($scope.data.devicename, 1, 0);
        }); 
    };   

    $scope.get_hierarchy = function(devicename, checkdevice=0, status=null) {
        console.log("get_hierarchy " + devicename);
        var data = undefined;
        if (checkdevice === 1) {
            data = {};
            data.checkdevice = checkdevice;
            if (status !== null) {
                data.status = status;
            }
        }
        //
        // GET DEVICE HIERARCHY
        // - Request:
        //   POST /devices/device/<devicename>/hierarchy
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'hierarchy': { "name": string, "children": ["name": string, "children": [...]] } }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'POST',
            url: server + '/devices/device/' + devicename + '/hierarchy',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access},
            data: data
        })
        .then(function (result) {
            console.log(result.data);

            if ($scope.treeData !== null) {
                $scope.eraseTreeChart2();
                $scope.treeData = null;
            }
            $scope.treeData = result.data.hierarchy;
            $scope.drawTreeChart($scope.treeData);
        })
        .catch(function (error) {
            $scope.handle_error(error);
        }); 
    };

    // GET DEVICE
    $scope.getDevice = function(devicename) {
        $scope.get_device(devicename);
    };  
    
    $scope.get_device = function(devicename) {
        console.log("get_device " + devicename);
        console.log("get_device " + $scope.data.devicename);
        console.log("get_device " + $stateParams.devicename);
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
            url: server + '/devices/device/' + devicename,
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
                'timestamp': "" + timestamp,
                'heartbeat': "" + heartbeat,
                'version': $scope.data.deviceversion
            };
            
//            $state.go('menu.mapsExample', device_param, {reload:true});
            $state.go('viewDevice', device_param, {reload:true});
        })
        .catch(function (error) {
            $scope.handle_error(error);
        });         
    };


    // GET DEVICE LOCATION
    $scope.get_device_location = function(devicename) {
        console.log("get_device_location " + devicename);
        //
        // GET DEVICE LOCATION
        // - Request:
        //   GET /devices/device/DEVICENAME/location
        //   headers: {'Authorization': 'Bearer ' + token.access}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'location': {'latitude': float, 'longitude': float} }
        //   { 'status': 'NG', 'message': string}
        //        
        $http({
            method: 'GET',
            url: server + '/devices/device/' + devicename + '/location',
            headers: {'Authorization': 'Bearer ' +  $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.location !== undefined) {
                $scope.data.location = result.data.location;
                $scope.data.devicelocation = result.data.location !== "UNKNOWN" ? result.data.location.latitude.toFixed(4) + "..., " + result.data.location.longitude.toFixed(4) + "..." : "UNKNOWN";
                $scope.getStatus($scope.data.devicename);
            }
        })
        .catch(function (error) {
            $scope.handle_error(error);
        });         
    };


    // VIEW DEVICE LOCATION
    $scope.viewDeviceLocation = function(device) {
        console.log("viewDeviceLocation= " + device.devicename);
        
        var device_param = {
            'username'     : $scope.data.username,
            'token'        : $scope.data.token,
            'devicename'   : $scope.data.devicename,
            'deviceid'     : $scope.data.deviceid,
            'serialnumber' : $scope.data.serialnumber,
            'devicestatus' : $scope.data.devicestatus,
            'deviceversion': $scope.data.deviceversion,
            'location'     : $scope.data.location,
        };
       
        if ($stateParams.devicelocation !== undefined) {
            device_param.location = $stateParams.devicelocation;
        }
        else if ($stateParams.devicelocation === "UKNOWN") {
            device_param.location = null;
        }
        $state.go('deviceLocation', device_param, {reload: true});    
    };
    
    // EXIT PAGE
    $scope.exitPage = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token
        };
        
        if ($scope.data.status === "Online") {
            if ($scope.treeData !== null) {
                $scope.eraseTreeChart();
                $scope.treeData = null;
            }
        }
        else { //if ($scope.data.status !== "Online") {
            if ($scope.treeData !== null) {
                $scope.eraseTreeChart2();
                $scope.treeData = null;
            }
        }
        
        $state.go('menu.devices', device_param, {reload: true});
    };
   
    $scope.$on('$ionicView.enter', function(e) {
        console.log("DEVICE enter");
        if ($scope.treeData !== null) { 
            $scope.eraseTreeChart2();
            $scope.treeData = null;
        }
        $scope.get_hierarchy($scope.data.devicename);
        
        //console.log($stateParams.location);
        //console.log($stateParams.location.latitude);
        //console.log($stateParams.location.longitude);
        //console.log($state.params.location.latitude);
        //console.log($state.params.location.longitude);
        
        if ($state.params.location === "" || $state.params.location === "UNKNOWN" || $state.params.location === undefined) {
            $scope.data.devicelocation = "UNKNOWN";
            $scope.get_device_location($scope.data.devicename);
            if ($scope.data.deviceversion === "") {
                $scope.getStatus($scope.data.devicename);
            }
        }
        else if ($stateParams.location === "" || $stateParams.location === "UNKNOWN" || $stateParams.location === undefined) {
            $scope.data.devicelocation = "UNKNOWN";
            $scope.get_device_location($scope.data.devicename);
            if ($scope.data.deviceversion === "") {
                $scope.getStatus($scope.data.devicename);
            }
        }
        else {
            $stateParams.location = $state.params.location;
            $scope.data.location = $state.params.location;
            $scope.data.devicelocation = $stateParams.location !== "UNKNOWN" ? $stateParams.location.latitude.toFixed(4) + "..., " + $stateParams.location.longitude.toFixed(4) + "..." : "UNKNOWN";
            $scope.getStatus($scope.data.devicename);
        }
    });   
   
    $scope.$on('$ionicView.beforeLeave', function(e) {
        console.log("DEVICE beforeLeave");
        if ($scope.data.status === "Online") {
            if ($scope.treeData !== null) {
                $scope.eraseTreeChart();
                $scope.treeData = null;
            }
        }
        else { //if ($scope.data.status !== "Online") {
            if ($scope.treeData !== null) {
                $scope.eraseTreeChart2();
                $scope.treeData = null;
            }
        }
        //if ($scope.treeData !== null) {
        //    $scope.eraseTreeChart();
        //    $scope.treeData = null;
        //}
    });
    
/*
    $scope.treeData = {
      "name": "Demo1Device1",
      "active": 1,  // online/offline
      "children": [
        {
          "name": "UART",
          "children": [
            {
              "name": "UART 1",
            },
          ]
        },
        {
          "name": "GPIO",
          "children": [
            {
              "name": "GPIO 1",
            },
            {
              "name": "GPIO 2",
            },
            {
              "name": "GPIO 3",
            },
            {
              "name": "GPIO 4",
            },
          ]
        },
        {
          "name": "I2C",
          "children": [
            {
              "name": "I2C 1",
              "children": [
                {
                  "name": "POT 1",
                  "active": 0,  // online/offline
                  "children": [
                    {
                      "name": "Temperature",
                      "active": 0,  // online/offline
                    }
                  ]
                }
              ]
            },
            {
              "name": "I2C 2",
            },
            {
              "name": "I2C 3",
            },
            {
              "name": "I2C 4",
            },
          ]
        },
        {
          "name": "ADC",
          "children": [
            {
              "name": "ADC 1",
            },
            {
              "name": "ADC 2",
            },
          ]
        },
        {
          "name": "Onewire",
          "children": [
            {
              "name": "Onewire 1",
            },
          ]
        },
        {
          "name": "TProbe",
          "children": [
            {
              "name": "TProbe 1",
            },
          ]
        },
      ]
    };
*/
    
    $scope.eraseTreeChart = function(){
        const svg_id = "#" + $scope.data.devicename;
        var svg = d3.select(svg_id);
        svg.data([]).exit().remove();
    };

    $scope.eraseTreeChart2 = function(){
        const svg_id = "#" + $scope.data.devicename;
        var svg = d3.select(svg_id);
        svg.select("svg").remove();
    };
   
    $scope.drawTreeChart = function(treeData) { // Function for creating bar chart
        //console.log(document.getElementsByClassName("hierarchychart"));
        
        // set the dimensions and margins of the diagram
        const margin = {top: 50, right: 100, bottom: 50, left: 250},
              width  = 800 - margin.left - margin.right,
              height = 450 - margin.top - margin.bottom;
        
        // declares a tree layout and assigns the size
        const treemap = d3.tree().size([height, width]);
        
        //  assigns the data to a hierarchy using parent-child relationships
        let nodes = d3.hierarchy(treeData, d => d.children);
        
        // maps the node data to the tree layout
        nodes = treemap(nodes);
        
        // append the svg object to the body of the page
        // appends a 'group' element to 'svg'
        // moves the 'group' element to the top left margin
        const svg_id = "#" + $scope.data.devicename;
        //console.log(d3.select(svg_id));
        
        const svg = d3.select(svg_id).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        // adds the links between the nodes
        const link = g.selectAll(".d3link")
            .data( nodes.descendants().slice(1))
          .enter().append("path")
            .attr("class", "d3link")
            //.style("stroke", d => d.data.level)
            .attr("d", d => {
               return "M" + d.y + "," + d.x
                 + "C" + (d.y + d.parent.y) / 2 + "," + d.x
                 + " " + (d.y + d.parent.y) / 2 + "," + d.parent.x
                 + " " + d.parent.y + "," + d.parent.x;
               });
        
        // adds each node as a group
        const node = g.selectAll(".d3node")
            .data(nodes.descendants())
            .enter().append("g")
            .attr("class", d => "d3node" + (d.children ? " node--internal" : " node--leaf"))
            .attr("transform", d => "translate(" + d.y + "," + d.x + ")");
        
        // adds the circle to the node
        node.append("circle")
          .attr("r", d => 4)//d.data.value) // hardcode value to 4
          .style("stroke", d => d.data.type)
          .style("fill", d => /*d.data.level*/ {
                return d.data.active===1 ? "green" : (d.data.active===0 ? "red" : "#DDDDDD"); 
              }
          );
          
        // adds the text to the node
        node.append("text")
          .attr("dy", ".35em")
          .attr("x", d => d.children ? (/*d.data.value*/4 + 5) * -1 : /*d.data.value*/4 + 5)
          .attr("y", d => d.children && d.depth !== 0 ? -(/*d.data.value*/4 + 5) : 0)
          .style("text-anchor", d => d.children ? "end" : "start")
          .text(d => d.data.name);
    };
}])
   
.controller('sensorDashboardCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,
    };

    $scope.timer = null;
        
    $scope.devices = [{"devicename": "All devices"}];

    // Filter by peripherals
    $scope.peripherals = [ 
        "All peripherals",
        "I2C1",
        "I2C2",
        "I2C3",
        "I2C4",
        "ADC1",
        "ADC2",
        "1WIRE1",
        "TPROBE1"
    ];
    $scope.peripheral = $scope.peripherals[0];
    
    // Filter by sensor class
    $scope.sensorclasses = [ 
        "All classes",
        //"speaker", 
        //"display",
        //"light",
        "potentiometer",
        "temperature",
        "humidity",
        "anemometer",
        "battery",
        "fluid",
    ];
    $scope.sensorclass = $scope.sensorclasses[0];
    
    // Filter by sensor status
    $scope.sensorstatuses = [ 
        "All online/offline",
        "online",
        "offline",
    ];
    $scope.sensorstatus = $scope.sensorstatuses[0];

    $scope.timeranges = [ 
        "Last 5 minutes",
        "Last 15 minutes",
        "Last 30 minutes",
        "Last 60 minutes",
        "Last 3 hours",
        "Last 6 hours",
        "Last 12 hours",
        "Last 24 hours",
        "Last 3 days",
        "Last 7 days",
        "Last 2 weeks",
        "Last 4 weeks",
        "Last 3 months",
        "Last 6 months",
        "Last 12 months",
    ];
    $scope.timerange = $scope.timeranges[0];
    $scope.timerangeindex = 0;
    $scope.checkdevice = 1;
    
    
    $scope.hide_settings = false;
    $scope.sensors = [];
    $scope.sensorsummary = [];
    $scope.sensorsummaryshow = false;
    $scope.devicesummary = [];
    $scope.devicesummaryshow = false;
    $scope.usages = [];
    $scope.usagesshow = false;
    $scope.comparisons = [];
    $scope.sensors_counthdr = "No sensor returned" ;
    $scope.refresh_automatically = false;
    $scope.refresh_time = 5;
    $scope.run_time = 0;
    $scope.big_charts = false;
    $scope.online_charts = false;

    $scope.stats = {};
    
    // colorful palette    
    $scope.sensors_datachart_colors_options     = ['#11C1F3', '#33CD5F', '#FFC900', '#F38124', '#EF473A', '#F58CF6', '#B6A2FC', '#3C5A99'];
    $scope.sensors_datachart_colors_options_ex  = ['#EF473A', '#F38124', '#FFC900', '#33CD5F', '#11C1F3', '#3C5A99', '#B6A2FC', '#F58CF6'];
    $scope.sensors_datachart_colors_options_ex2 = ['#F58CF6', '#B6A2FC', '#3C5A99', '#EF473A', '#F38124', '#FFC900', '#33CD5F', '#11C1F3'];
    // sunburst palette
    //$scope.sensors_datachart_colors_options     = ['#A78FC9', '#D98DCC', '#FF94B4', '#FFAD94', '#EFD38F', '#CFF5A7', '#93F8AD', '#66EBCA', '#66CDE6'];
    //$scope.sensors_datachart_colors_options_ex  = ['#FFAD94', '#EFD38F', '#CFF5A7', '#93F8AD', '#66EBCA', '#66CDE6', '#A78FC9', '#D98DCC', '#FF94B4'];
    //$scope.sensors_datachart_colors_options_ex2 = ['#93F8AD', '#66EBCA', '#66CDE6', '#A78FC9', '#D98DCC', '#FF94B4', '#FFAD94', '#EFD38F', '#CFF5A7'];    
    
    $scope.sensors_datachart = [{"labels": [], "data": [], "series": [], "colors": []}];
    $scope.sensors_datachart_empty = {"labels": [], "data": [], "series": [], "colors": []};
    
    $scope.sensors_datachart_options = {
        "animation": false, 
        "legend": {
            "display": true,
            "position": 'bottom'
        },
        "scales": {
            "xAxes": [{
                "ticks": {
                    //"autoSkip": false,
                    "maxRotation": 90,
                    "minRotation": 90
                }
            }],
            "yAxes": [{
                "ticks": {
                    "beginAtZero": true,
                    "max": 100,
                    "min": 0,
                }
            }],
        },
        "tooltips": {
            "enabled": true,
            "callbacks": {
                "beforeTitle": function(tooltipItem, data) {
                    //console.log("beforeTitle");
                    //console.log(data);
                    //console.log(data.datasets[0]._meta);
                    var key = Object.keys(data.datasets[0]._meta)[0];
                    var canvasid = data.datasets[0]._meta[key].controller.chart.ctx.canvas.id;
                    return canvasid + "\r\n";
                },
                "title": function(tooltipItem, data) {
                    //console.log("title");
                    //console.log(tooltipItem);
                    //console.log(data);
                    var key = Object.keys(data.datasets[0]._meta)[0];
                    var canvasid = data.datasets[0]._meta[key].controller.chart.ctx.canvas.id;
                    var devicename = canvasid.split(".")[0];
                    var sensorname = canvasid.split(".")[1];
                    //console.log(devicename);
                    //console.log(sensorname);
                    var date = "";
                    for (var sensor in $scope.sensors_datachart) {
                        if ($scope.sensors_datachart[sensor].devicename === devicename && 
                            $scope.sensors_datachart[sensor].sensorname === sensorname) {
                                key = tooltipItem[0].index;
                                //console.log(key);
                                date = $scope.sensors_datachart[sensor].labels_date[key];
                                break;
                            }
                    }
                    
                    return "Date: " + date + "\r\nTime: " + tooltipItem[0].label;
                },
                "label": function(tooltipItem, data) {
                    //console.log("label");
                    var label = data.datasets[tooltipItem.datasetIndex].label || '';
                    
                    var key = Object.keys(data.datasets[0]._meta)[0];
                    var canvasid = data.datasets[0]._meta[key].controller.chart.ctx.canvas.id;
                    var devicename = canvasid.split(".")[0];
                    var sensorname = canvasid.split(".")[1];
                    
                    var unit = null;
                    for (var sensor in $scope.sensors_datachart) {
                        if ($scope.sensors_datachart[sensor].devicename === devicename && 
                            $scope.sensors_datachart[sensor].sensorname === sensorname) {
                                let index = tooltipItem.datasetIndex;
                                if ($scope.sensors_datachart[sensor].data !== undefined) {
                                    unit = $scope.sensors_datachart[sensor].units[index];
                                    //console.log(unit);
                                }
                                break;
                            }
                    }
                    
                    if (unit !== undefined && unit !== null && unit !== "") {
                        label += " (" + unit + ")";
                    }
                    
                    return label;
                }, 
                "afterLabel": function(tooltipItem, data) {
                    //console.log("afterLabel");
                    //console.log(tooltipItem);
                    //console.log(data);
                    var key = Object.keys(data.datasets[0]._meta)[0];
                    //console.log(key);
                    var canvasid = data.datasets[0]._meta[key].controller.chart.ctx.canvas.id;
                    var devicename = canvasid.split(".")[0];
                    var sensorname = canvasid.split(".")[1];
                    //console.log(devicename);
                    //console.log(sensorname);
                    var val = null;
                    var low = null;
                    var high = null;

                    for (var sensor in $scope.sensors_datachart) {
                        if ($scope.sensors_datachart[sensor].devicename === devicename && 
                            $scope.sensors_datachart[sensor].sensorname === sensorname) {
                                key = tooltipItem.index;
                                //console.log(key);
                                let index = tooltipItem.datasetIndex;
                                if ($scope.sensors_datachart[sensor].data !== undefined) {
                                    val = $scope.sensors_datachart[sensor].data[index][key];
                                    //console.log(val);
                                }
                                if ($scope.sensors_datachart[sensor].low !== undefined) {
                                    low = $scope.sensors_datachart[sensor].low[index][key];
                                    //console.log(low);
                                }
                                if ($scope.sensors_datachart[sensor].high !== undefined) {
                                    high = $scope.sensors_datachart[sensor].high[index][key];
                                    //console.log(high);
                                }
                                break;
                            }
                    }
                    
                    var append = "";
                    if (val !== undefined && val !== null) {
                        append += "value: " + val.toString();
                    }
                    if (low !== undefined && low !== null) {
                        append += "\r\n" + "low: " + low.toString();
                    }
                    if (high !== undefined && high !== null) {
                        append += "\r\n" + "high: " + high.toString();
                    }
                    return append;
                },
/*                
                "afterBody": function(tooltipItem, data) {
                    var key = Object.keys(data.datasets[0]._meta)[0];
                    var canvasid = data.datasets[0]._meta[key].controller.chart.ctx.canvas.id;
                    var devicename = canvasid.split(".")[0];
                    var sensorname = canvasid.split(".")[1];
                    //console.log(devicename);
                    //console.log(sensorname);
                    var low = null;
                    var high = null;
                    
                    for (var sensor in $scope.sensors_datachart) {
                        if ($scope.sensors_datachart[sensor].devicename === devicename && 
                            $scope.sensors_datachart[sensor].sensorname === sensorname) {
                                key = tooltipItem[0].index;
                                //console.log(key);
                                if ($scope.sensors_datachart[sensor].low !== undefined) {
                                    low = $scope.sensors_datachart[sensor].low[0][key];
                                }
                                if ($scope.sensors_datachart[sensor].high !== undefined) {
                                    high = $scope.sensors_datachart[sensor].high[0][key];
                                }
                                break;
                            }
                    }
                    
                    if (low === undefined || high === undefined || low === null || high === null) {
                        return "";
                    }
                    
                    var append = "\r\n";
                    append += "low: " + low.toString() + "\r\n";
                    append += "high: " + high.toString() + "\r\n";
                    return append;
                },
*/                
            }            
        },
    
/*        "title": {
            "display": true,
            "position": 'bottom'
        },*/

/*        "elements": {
            "line": {
                "fill": false
            }
        },*/

/*        "onClick": function(e) {
            //console.log(e);
            console.log(e.srcElement.id);
            var element = this.getElementAtEvent(e);
            if (element.length) {
                //console.log(element[0]);
                console.log(element[0]._index);
            }
        },*/           
    };
    
    $scope.sensors_datachart_piechart_devices_statuses_options = {
        "title": {
            "display": true,
            "text": 'Status'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    $scope.sensors_datachart_piechart_devices_groups_options = {
        "title": {
            "display": true,
            "text": 'Groups'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    $scope.sensors_datachart_piechart_devices_versions_options = {
        "title": {
            "display": true,
            "text": 'Versions'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    $scope.sensors_datachart_piechart_devices_locations_options = {
        "title": {
            "display": true,
            "text": 'Locations'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    
    
    $scope.sensors_datachart_piechart_sensors_statuses_options = {
        "title": {
            "display": true,
            "text": 'Status'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    $scope.sensors_datachart_piechart_sensors_types_options = {
        "title": {
            "display": true,
            "text": 'Types'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    $scope.sensors_datachart_piechart_sensors_peripherals_options = {
        "title": {
            "display": true,
            "text": 'Peripherals'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    $scope.sensors_datachart_piechart_sensors_classes_options = {
        "title": {
            "display": true,
            "text": 'Classes'
        },
        "legend": {
            "display": true,
            "position": 'left'
        },
    };
    
    $scope.sensors_datachart_barchart_usages_alerts_series = ["sms", "email", "notification"];
    $scope.sensors_datachart_barchart_usages_alerts_options = {
        "title": {
            "display": true,
            "text": 'Alerts'
        },
        "animation": false, 
        "scales": {
            "xAxes": [{
                "ticks": {
                    "beginAtZero": true,
                    "max": 100,
                    "min": 0,                    
                }
            }]
        },
        "tooltips": {
            "enabled": true,
            "callbacks": {
                "title": function(tooltipItem, data) {
                    return "Alerts usage for " + tooltipItem[0].label;
                },
                "label": function(tooltipItem, data) {
                    return tooltipItem.xLabel + "%";
                }
            }
        },
        "legend": {
            "display": true,
            "position": 'left'
        }
    };
    $scope.sensors_datachart_barchart_usages_storage_series = ["sensor data", "alert data"];
    $scope.sensors_datachart_barchart_usages_storage_options = {
        "title": {
            "display": true,
            "text": 'Storage'
        },
        "animation": false, 
        "scales": {
            "xAxes": [{
                "ticks": {
                    "beginAtZero": true,
                    "max": 100,
                    "min": 0,                    
                }
            }]
        },
        "tooltips": {
            "enabled": true,
            "callbacks": {
                "title": function(tooltipItem, data) {
                    return "Storage usage";
                },                
                "label": function(tooltipItem, data) {
                    return tooltipItem.xLabel + "%";
                }
            }
        },
        "legend": {
            "display": true,
            "position": 'left'
        }
    };
    $scope.sensors_datachart_barchart_usages_login_series = ["via email", "via sms"];
    $scope.sensors_datachart_barchart_usages_login_options = {
        "title": {
            "display": true,
            "text": 'Logins'
        },
        "animation": false, 
        "scales": {
            "xAxes": [{
                "ticks": {
                    "beginAtZero": true,
                    "max": 100,
                    "min": 0,                    
                }
            }]
        },
        "tooltips": {
            "enabled": true,
            "callbacks": {
                "title": function(tooltipItem, data) {
                    return "Login success rate for " + tooltipItem[0].label;
                },
                "label": function(tooltipItem, data) {
                    return tooltipItem.xLabel + "%";
                }
            }
        },
        "legend": {
            "display": true,
            "position": 'left'
        }
    };
    $scope.sensors_datachart_barchart_options = {
        "animation": false, 
        "scales": {
            //"xAxes": [{
            //    "ticks": {
            //        //"autoSkip": false,
            //        "maxRotation": 90,
            //        "minRotation": 90
            //    }
            //}],
            "yAxes": [{
                "ticks": {
                    "beginAtZero": true,
                }
            }],
        }
    };

    
    $scope.changeTimeRangeIndexBackward = function() {
        $scope.timerangeindex += 1;
        //console.log($scope.timerangeindex);
        if ($scope.refresh_automatically === false) {
            $scope.submitQuery();            
        }
    };

    $scope.changeTimeRangeIndexForward = function() {
        if ($scope.timerangeindex > 0) {
            $scope.timerangeindex -= 1;
            //console.log($scope.timerangeindex);
            if ($scope.refresh_automatically === false) {
                $scope.submitQuery();            
            }
        }    
    };

    $scope.changeBigChart = function(s) {
        $scope.big_charts = s;
        //console.log($scope.big_charts);
    };

    $scope.changeOnlineChart = function(s) {
        $scope.online_charts = s;
        //console.log($scope.online_charts);
    };

    $scope.changeHideSettings = function(s) {
        $scope.hide_settings = s;
    };
    
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Sensor Dashboard failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
        }
    };
    
    get_all_device_sensors_enabled_input = function() {
        //
        // GET ALL ENABLED DEVICE SENSORS (enabled input)
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/sensors/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/sensors/readings',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No sensor returned";
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 sensor returned";
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " sensors returned";
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    $scope.changeSensorHide = function(sensor) {
        sensor.show = !sensor.show;
    };

    $scope.changeSensorTableHide = function() {
        $scope.sensorsummaryshow = !$scope.sensorsummaryshow;
    };
    
    $scope.changeDeviceTableHide = function() {
        $scope.devicesummaryshow = !$scope.devicesummaryshow;
    };

    $scope.changeUsageTableHide = function() {
        $scope.usagesshow = !$scope.usagesshow;
    };

    $scope.changeSensorComparisonsHide = function(comparison) {
        comparison.show = !comparison.show;
    };

    get_all_device_sensors_enabled_input_dataset = function() {
        //console.log($scope.peripheral);
        //console.log($scope.sensorclass);
        var points = 60;
        if ($scope.big_charts === false) {
            points = 30;   
        }
        
        //
        // GET ALL ENABLED DEVICE SENSORS (enabled input) DATASETS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/sensors/readings/dataset
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Request:
        //   POST /devices/sensors/readings/dataset
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'devicename': string, 'peripheral': string, 'class': string, 'status': string, 'timerange': string, 'points': int, 'index': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        //$http({
        //    method: 'GET',
        //    url: server + '/devices/device/' + $scope.data.devicename + '/sensors/readings/dataset',
        //    headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        //})
        $http({
            method: 'POST',
            url: server + '/devices/sensors/readings/dataset',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: {
                'devicename': $scope.data.devicename, 
                'peripheral': $scope.peripheral, 
                'class': $scope.sensorclass, 
                'status': $scope.sensorstatus, 
                'timerange': $scope.timerange, 
                'points': points,
                'index': $scope.timerangeindex,
                'checkdevice': $scope.checkdevice,
            }
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.sensors.length === 0) {
                $scope.sensors_counthdr = "No sensor returned";
                $scope.sensors = [];
                return;
            }
            else {
                // delete 
                if ($scope.online_charts === true) {
                    let count = result.data.sensors.length;
                    
                    for (let indexy=count-1; indexy>=0; indexy--) {
                        if (result.data.sensors[indexy].enabled === 0) {
                            //delete result.data.sensors[indexy];
                            result.data.sensors.splice(indexy, 1);
                        }
                    }
                    /*
                    for (let indexy=0; indexy<count; indexy++) {
                        if (result.data.sensors[indexy].enabled === 0) {
                            result.data.sensors.splice(indexy, 1);
                        }
                    }
                    */
                    console.log(result.data.sensors.length);
                }
                if (result.data.sensors.length === 0) {
                    $scope.sensors_counthdr = "No sensor returned";
                    $scope.sensors = [];
                    return;
                }
                else if (result.data.sensors.length === 1) {
                    $scope.sensors_counthdr = "1 sensor returned";
                }
                else {
                    $scope.sensors_counthdr = result.data.sensors.length.toString() + " sensors returned";
                }
            }
            
            // handle show parameter for sensor
            for (let indexy=0; indexy<result.data.sensors.length; indexy++) {
                let found = false;
                for (let indexz=0; indexz<$scope.sensors.length; indexz++) {
                    if ($scope.sensors[indexz].devicename === result.data.sensors[indexy].devicename &&
                        $scope.sensors[indexz].sensorname === result.data.sensors[indexy].sensorname) {
                            if ($scope.sensors[indexz].show === undefined) {
                                result.data.sensors[indexy].show = true;
                            }
                            else {
                                result.data.sensors[indexy].show = $scope.sensors[indexz].show;
                            }
                            found = true;
                            break;
                        }
                }
                if (found === false) {
                    result.data.sensors[indexy].show = true;
                }
            }
            $scope.sensors = result.data.sensors;
            // handle show parameter for comparison
            if (result.data.comparisons !== undefined) {
                for (let indexy=0; indexy<result.data.comparisons.length; indexy++) {
                    result.data.comparisons[indexy].show = true;
                    /*
                    let found = false;
                    if ($scope.comparisons !== undefined) {
                        for (let indexz=0; indexz<$scope.comparisons.length; indexz++) {
                            if ($scope.comparisons[indexz].class === result.data.comparisons[indexy].class) {
                                if ($scope.comparisons[indexz].show === undefined) {
                                    result.data.comparisons[indexy].show = true;
                                }
                                else {
                                    result.data.comparisons[indexy].show = $scope.comparisons[indexz].show;
                                }
                                found = true;
                                break;
                            }
                        }
                    }
                    if (found === false) {
                        result.data.comparisons[indexy].show = true;
                    }
                    */
                }
                $scope.comparisons = result.data.comparisons;
            }
            
            if (result.data.stats !== undefined) {
                $scope.stats = result.data.stats;
            }
            if (result.data.summary !== undefined) {
                $scope.sensorsummary = result.data.summary.sensors;
                $scope.devicesummary = result.data.summary.devices;
            }
            if (result.data.usages !== undefined) {
                $scope.usages = result.data.usages;
            }

            if ($scope.sensors.length > 0) {
                
                // set default labels and data
                $scope.sensors_datachart = [];
                let color_index = 0;
                
                let show_seconds = false;
                if ($scope.timerange.includes("minutes") && $scope.timerange !== "Last 60 minutes") {
                    show_seconds = true;
                }
                
                for (let indexy=0; indexy<$scope.sensors.length; indexy++) {
                    // colors, series
                    $scope.sensors[indexy].dataset.colors = [];
                    if (color_index >= $scope.sensors_datachart_colors_options.length) {
                        color_index = 0;
                    }
                    $scope.sensors[indexy].dataset.colors.push($scope.sensors_datachart_colors_options[color_index++]);
                    $scope.sensors[indexy].dataset.series = [];
                    $scope.sensors[indexy].dataset.series.push($scope.sensors[indexy].class);
                    if ($scope.sensors[indexy].subclass) {
                        $scope.sensors[indexy].dataset.series.push($scope.sensors[indexy].subclass);
                        $scope.sensors[indexy].dataset.colors.push($scope.sensors_datachart_colors_options[color_index++]);
                    }
                    //console.log("xxxxxxx" + indexy + " " + color_index + " " + $scope.sensors[indexy].dataset.colors);

                    // devicename, sensorname, units, formats    
                    $scope.sensors[indexy].dataset.devicename = $scope.sensors[indexy].devicename;
                    $scope.sensors[indexy].dataset.sensorname = $scope.sensors[indexy].sensorname;
                    $scope.sensors[indexy].dataset.units      = $scope.sensors[indexy].units;
                    $scope.sensors[indexy].dataset.formats    = $scope.sensors[indexy].formats;
                    
                    // labels
                    $scope.sensors[indexy].dataset.labels_time = [];
                    $scope.sensors[indexy].dataset.labels_date = [];
                
                    
                    for (let indexz=0; indexz<$scope.sensors[indexy].dataset.labels.length; indexz++) {
                        var timestamp = new Date($scope.sensors[indexy].dataset.labels[indexz] * 1000);
                        //console.log(timestamp);
                        var timestamp_time = 
                            ('0'+timestamp.getHours()).slice(-2) + ":" + 
                            ('0'+timestamp.getMinutes()).slice(-2);
                        if (show_seconds) {    
                            timestamp_time += ":" + ('0'+timestamp.getSeconds()).slice(-2);
                        }
                        //console.log(timestamp_time);
                        var timestamp_date = 
                            timestamp.getFullYear() + "/" + 
                            ('0'+(timestamp.getMonth()+1)).slice(-2) + "/" + 
                            ('0'+timestamp.getDate()).slice(-2);
                        //console.log(timestamp_date);
                        $scope.sensors[indexy].dataset.labels_time.push(timestamp_time);
                        $scope.sensors[indexy].dataset.labels_date.push(timestamp_date);
                    }

                    $scope.sensors_datachart.push( $scope.sensors[indexy].dataset );
                }
                //console.log($scope.sensors_datachart);
            }
            

            if ($scope.timer !== null /* && $scope.data.devicename === "All devices" */) {
                if ($scope.checkdevice === 1) {
                    $scope.checkdevice = 0;
                    //get_all_sensor_thresholdsforwards();
                }
            }
            else {
                if ($scope.checkdevice === 1) {
                    //get_all_sensor_thresholdsforwards();
                }
            }
        })
        .catch(function (error) {
            $scope.sensors_counthdr = "No sensor returned";
            $scope.sensors = [];
            handle_error(error);
        }); 
    };

/*
    $scope.chartOnClick = function(evt, sensor) {
        console.log("chartOnClick");
        console.log(evt);
        console.log(sensor);
        
        var element = evt.getPointsAtEvent();
        if (element.length) {
            console.log(element[0]);
        }        
    };
*/
    delete_all_device_sensors_enabled_input = function(flag=false) {
        //
        // DELETE ALL ENABLED DEVICE SENSORS (enabled input)
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/sensors/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/sensors/readings',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
        })
        .then(function (result) {
            console.log(result.data);
            
            if (flag === true) {
                $scope.submitQuery();
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    delete_all_device_sensors = function(flag=false) {
        //
        // DELETE ALL ENABLED DEVICE SENSORS (enabled input)
        //
        // - Request:
        //   DELETE /devices/sensors/readings/dataset
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'devicename': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/sensors/readings/dataset',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: {'devicename': $scope.data.devicename}
        })
        .then(function (result) {
            console.log(result.data);
            
            if (flag === true) {
                $scope.submitQuery();
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    get_all_sensor_configurationsummary = function() {
        //
        // GET PERIPHERAL SENSOR CONFIGURATION SUMMARY
        //
        // - Request:
        //   GET /devices/sensors/configurationsummary
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'summary': {'sensorname': string, 'devicename': string, 'classes': string, 'configuration': string, 'enabled': int} }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/sensors/configurationsummary',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
        })
        .then(function (result) {
            console.log(result.data);
            $scope.sensorsummary = result.data.summary.sensors;
            $scope.devicesummary = result.data.summary.devices;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    $scope.changePeripheral = function(peripheral) {
        $scope.peripheral = peripheral;
        $scope.submitQuery();
    };

    $scope.changeSensorClass = function(sensorclass) {
        $scope.sensorclass = sensorclass;
        $scope.submitQuery();
    };

    $scope.changeSensorStatus = function(sensorstatus) {
        $scope.sensorstatus = sensorstatus;
        $scope.submitQuery();
    };

    $scope.changeTimeRange = function(timerange) {
        $scope.timerange = timerange;
        $scope.submitQuery();
    };

    $scope.changeDevice = function(devicename, refresh=false) {
        var found = false;
        for (indexy=0; indexy<$scope.devices.length; indexy++) {
            if (devicename === $scope.devices[indexy].devicename) {
                $scope.data.devicename = $scope.devices[indexy].devicename;
                if ($scope.data.devicename !== "All devices") {
                    $scope.data.deviceid = $scope.devices[indexy].deviceid;
                    $scope.data.serialnumber = $scope.devices[indexy].serialnumber;
                    $scope.data.devicestatus = $scope.devices[indexy].devicestatus;
                }
                
                found = true;
                $scope.submitQuery(refresh=refresh);
                break;
            }
        }
        if (found === false) {
            $scope.submitQuery(refresh=refresh);
        }
    };

    get_devices = function(flag) {
        
        param = {
            'username': User.get_username(),
            'token': User.get_token()     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = $scope.devices.concat(res);
            $scope.data.token = User.get_token();
            $scope.changeDevice($scope.data.devicename, refresh=true);
        });
    };

    $scope.chartLabels = function(sensor) {
        //console.log("chartLabels " + sensor.sensorname);  
        
        if ($scope.sensors.length === 0) {
            return $scope.sensors_datachart_empty.labels;
        }
        
        let indexy = 0;
        for (indexy=0; indexy<$scope.sensors.length; indexy++) {
            if ($scope.sensors[indexy].sensorname === sensor.sensorname &&
                $scope.sensors[indexy].devicename === sensor.devicename) {
                break;
            }
        }

        if (indexy >= $scope.sensors_datachart.length) {
            return $scope.sensors_datachart_empty.labels;
        }
        
        return $scope.sensors_datachart[indexy].labels_time;
    };

    $scope.chartData = function(sensor) {
        //console.log("chartData " + sensor.sensorname);

        if ($scope.sensors.length === 0) {
            return $scope.sensors_datachart_empty.data;
        }
        
        let indexy = 0;
        for (indexy=0; indexy<$scope.sensors.length; indexy++) {
            if ($scope.sensors[indexy].sensorname === sensor.sensorname &&
                $scope.sensors[indexy].devicename === sensor.devicename) {
                break;
            }
        }
        
        if (indexy >= $scope.sensors_datachart.length) {
            return $scope.sensors_datachart_empty.data;
        }
        
        return $scope.sensors_datachart[indexy].data;
    };


    $scope.chartSeries = function(sensor) {
        //console.log("chartData " + sensor.sensorname);

        if ($scope.sensors.length === 0) {
            return $scope.sensors_datachart_empty.series;
        }
        
        let indexy = 0;
        for (indexy=0; indexy<$scope.sensors.length; indexy++) {
            if ($scope.sensors[indexy].sensorname === sensor.sensorname &&
                $scope.sensors[indexy].devicename === sensor.devicename) {
                break;
            }
        }

        if (indexy >= $scope.sensors_datachart.length) {
            return $scope.sensors_datachart_empty.series;
        }
        
        return $scope.sensors_datachart[indexy].series;
    };
    
    $scope.chartColors = function(sensor) {
        //console.log("chartData " + sensor.sensorname);

        if ($scope.sensors.length === 0) {
            return $scope.sensors_datachart_empty.colors;
        }
        
        let indexy = 0;
        for (indexy=0; indexy<$scope.sensors.length; indexy++) {
            if ($scope.sensors[indexy].sensorname === sensor.sensorname &&
                $scope.sensors[indexy].devicename === sensor.devicename) {
                break;
            }
        }

        if (indexy >= $scope.sensors_datachart.length) {
            return $scope.sensors_datachart_empty.colors;
        }
        
        return $scope.sensors_datachart[indexy].colors;
    };    


    $scope.getMax = function(sensorclass) {
        let max = 0;
        if (sensorclass !== undefined) {
            if (sensorclass === "potentiometer") {
                max = 255;
            }
            else if (sensorclass === "temperature") {
                max = 40;
            }
            else {
                max = 100;
            }
        }
        return max;
    };

    $scope.chartOptions = function(sensor) {
        //console.log("chartOptions " + sensor.sensorname);
        //console.log(sensor);

        if ($scope.sensors.length === 0) {
            return $scope.sensors_datachart_options;
        }
        
        let found = false;
        for (indexy=0; indexy<$scope.sensors.length; indexy++) {
            if ($scope.sensors[indexy].sensorname === sensor.sensorname &&
                $scope.sensors[indexy].devicename === sensor.devicename) {

                let class_max = $scope.getMax(sensor.class);
                let subclass_max = $scope.getMax(sensor.subclass);
                $scope.sensors_datachart_options.scales.yAxes[0].ticks.max = Math.max(class_max, subclass_max);
                found = true;
                break;
            }
        }

        if (found === false) {
            $scope.sensors_datachart_options.scales.yAxes[0].ticks.max = 100;
        }
        
        return $scope.sensors_datachart_options;
    };    



    $scope.changeRefresh = function(refresh, timeout) {
        $scope.refresh_automatically = refresh;
        $scope.refresh_time = timeout;
        
        if (refresh === true) {
            //console.log(refresh);
            //console.log(timeout);
            if ($scope.refresh_time < 1) {
                $scope.refresh_time = 1;
            }
            $ionicPopup.alert({
                title: 'Refresh values automatically',
                template: 'The values will be refreshed automatically every ' + $scope.refresh_time + ' seconds.',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.timerangeindex = 0;
                            $scope.checkdevice = 1;
                            $scope.timer = setInterval($scope.pollSensorData, $scope.refresh_time * 1000);
                            $scope.submitQuery(clear=false);
                        }
                    }
                ]            
            });            
        }
        else {
            clearTimeout($scope.timer);
            $scope.timer = null;
            $scope.run_time = 0;
        }
    };

    $scope.pollSensorData = function() {
        $scope.run_time += 1;
        let seconds = 259200; // 3600 (1 hour) * 24 = 86400 seconds * 3 = 3 days
        
        // auto-stop after X seconds
        let run_time_max = Math.round(seconds/$scope.refresh_time);
        if ($scope.run_time > run_time_max) {
            
            clearTimeout($scope.timer);
            //console.log("clearTimeout");
            $scope.timer = null;
            $scope.run_time = 0;
            $scope.checkdevice = 1;
            $scope.refresh_automatically = !$scope.refresh_automatically;
            
            $ionicPopup.alert({
                title: 'Refresh values automatically',
                template: 'The polling has been stopped after 1 hour!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.refresh_automatically = false;
                        }
                    }
                ]            
            });            
            return;
        }
        $scope.submitQuery(clear=false);
    };

    $scope.submitDelete = function() {

        var template;
                
        if ($scope.data.devicename === "All devices") {
            template = 'Are you sure you want to clear database values for sensor readings of all sensors for all devices?';
        }
        else {
            template = 'Are you sure you want to clear database values for sensor readings of all sensors for ' + $scope.data.devicename + ' ?';
        }
        
        $ionicPopup.alert({
            title: 'Reset Sensor Readings',
            template: template,
            buttons: [
                { 
                    text: 'No',
                    type: 'button-assertive',
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
        //delete_all_device_sensors_enabled_input();
        delete_all_device_sensors(flag=true);
    };

    $scope.submitRefresh = function() {
        if ($scope.refresh_automatically) {
            console.log("Its already running!");
            return;
        }
        $scope.submitQuery();
    };

    $scope.submitQuery = function(clear=true, refresh=false) {
        
        if (clear) {
            if ($scope.timer !== null) {
                clearTimeout($scope.timer);
                //console.log("clearTimeout");
                $scope.timer = null;
            }
            $scope.run_time = 0;
            $scope.refresh_automatically = false;
            
            if (refresh) {
                $scope.sensors = [];
                $scope.sensors_counthdr = "No sensor returned";
            }
        }
        
        get_all_device_sensors_enabled_input_dataset();
    };

    $scope.submitViewSensorChart = function(sensor) {
        
        // TODO: temporariy disable
        return;

        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            //console.log("clearTimeout");
            $scope.timer = null;
        }
        $scope.run_time = 0;
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'location': $scope.data.location,
            'sensor': sensor,
        };
        $state.go('sensorChart', device_param);
    };

    $scope.submitExit = function() {
        console.log("hello");
        
        if ($scope.data.devicename !== "All devices") {
            let device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': $scope.data.devicename,
                'devicestatus': $scope.data.devicestatus,
                'deviceid': $scope.data.deviceid,
                'serialnumber': $scope.data.serialnumber,
                'location': $scope.data.location,
            };
            $state.go('device', device_param);
        }
        else {
            let device_param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
            };
            $state.go('menu.devices', device_param);
        }
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter sensor dashboard");
        $scope.devices = [{"devicename": "All devices"}];
        $scope.sensors = [];
        $scope.sensorsummary = [];
        $scope.sensorsummaryshow = false;
        $scope.devicesummary = [];
        $scope.devicesummaryshow = false;
        $scope.usages = [];
        $scope.usagesshow = false;
    
        $scope.comparisons = [];
        $scope.sensors_counthdr = "No sensor returned";
        
        $scope.timer = null;
        $scope.run_time = 0;
        
        //$scope.peripheral = $scope.peripherals[0];
        //$scope.sensorclass = $scope.sensorclasses[0];
        //$scope.sensorstatus = $scope.sensorstatuses[0];
        //$scope.timerange = $scope.timeranges[0];
        //$scope.timerangeindex = 0;
        $scope.checkdevice = 1;
        
        
        $scope.hide_settings = false;
        $scope.refresh_automatically = false;
        $scope.refresh_time = 5;
        $scope.run_time = 0;
        $scope.big_charts = false;
        $scope.online_charts = false;
    
        $scope.stats = {};        
        
        $scope.sensors_datachart = [{"labels": [], "data": [], "series": [], "colors": []}];
        //console.log($scope.data);
        //console.log($state.params);
        //console.log($stateParams);
        get_devices();
    });
    
    $scope.$on('$ionicView.beforeLeave', function(e) {
        //console.log("beforeLeave");
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            //console.log("clearTimeout");
            $scope.timer = null;
        }
        $scope.run_time = 0;
        $scope.timerangeindex = 0;
        $scope.checkdevice = 1;
    });
}])
   
.controller('sensorChartCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    //$scope.sensors = [];
    //$scope.sensors_counthdr = "No sensor enabled" ;
    //$scope.refresh_automatically = false;
    //$scope.refresh_time = 3;
    //$scope.run_time = 0;
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,
        'sensor': $stateParams.sensor,
    };


    $scope.datachart = {
        'labels' : [],
        'data': [], 
        'colors' : ['#387EF5'],
    };
   // $scope.timer = null;
    
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Sensor Dashboard failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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

    get_xxx_device_readings_dataset = function() {
        //
        // GET XXX DEVICE READINGS DATASET
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/xxx/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + $scope.data.sensor.source + '/' + $scope.data.sensor.number + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/readings/dataset',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            
            var readings = result.data.sensor_readings.readings;
            //console.log(readings);
            $scope.datachart.data = [];
            $scope.datachart.labels = [];
            for (var reading in readings) {
                //console.log(readings[reading]);
                var timestamp = new Date(readings[reading].timestamp * 1000);
                var timestamp_str = timestamp.getHours() + ":" + timestamp.getMinutes() + ":" + timestamp.getSeconds();
                $scope.datachart.data.push(readings[reading].sensor_readings.value);
                $scope.datachart.labels.push(timestamp_str);
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    delete_xxx_device_readings = function() {
        //
        // DELETE XXX DEVICE READINGS
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/xxx/NUMBER/sensors/sensor/SENSORNAME/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + $scope.data.sensor.source + '/' + $scope.data.sensor.number + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/readings',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
/*    
    get_all_device_sensors_enabled_input = function() {
        //
        // GET ALL ENABLED DEVICE SENSORS (enabled input)
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/sensors/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/sensors/readings',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No sensor enabled";
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 sensor enabled";
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " sensors enabled";
            }            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    delete_all_device_sensors_enabled_input = function() {
        //
        // DELETE ALL ENABLED DEVICE SENSORS (enabled input)
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/sensors/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/sensors/readings',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
*/

/*
    $scope.changeRefresh = function(refresh, timeout) {
        $scope.refresh_automatically = refresh;
        $scope.refresh_time = timeout;
        console.log(refresh);
        console.log(timeout);
        
        if (refresh === true) {
            if ($scope.refresh_time < 1) {
                $scope.refresh_time = 1;
            }
            $ionicPopup.alert({
                title: 'Refresh values automatically',
                template: 'The values will be refreshed automatically every ' + $scope.refresh_time + ' seconds.',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.timer = setInterval($scope.pollSensorData, $scope.refresh_time * 1000);
                        }
                    }
                ]            
            });            
        }
        else {
            clearTimeout($scope.timer);
            $scope.timer = null;
            $scope.run_time = 0;
        }
    };

    $scope.pollSensorData = function() {
        $scope.run_time += 1;
        
        // auto-stop in 1hour 3600/$scope.refresh_time
        let run_time_max = Math.round(3600/$scope.refresh_time);
        if ($scope.run_time > run_time_max) {
            
            $scope.run_time = 0;
            clearTimeout($scope.timer);
            console.log("clearTimeout");
            $scope.timer = null;
            $scope.refresh_automatically = !$scope.refresh_automatically;
            
            $ionicPopup.alert({
                title: 'Refresh values automatically',
                template: 'The polling has been stopped after 1 hour!',
                buttons: [
                    {
                        text: 'OK',
                        type: 'button-positive',
                        onTap: function(e) {
                            $scope.refresh_automatically = false;
                        }
                    }
                ]            
            });            
            return;
        }
        $scope.submitQuery();
    };
*/

    $scope.submitDelete = function() {
        $ionicPopup.alert({
            title: 'Reset Sensor Readings',
            template: 'Are you sure you want to clear database values for sensor readings of all sensors?',
            buttons: [
                { 
                    text: 'No',
                    type: 'button-assertive',
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
        delete_xxx_device_readings();
        //delete_all_device_sensors_enabled_input();
    };

    $scope.submitQuery = function() {
        get_xxx_device_readings_dataset();
        //get_all_device_sensors_enabled_input();
    };

    $scope.submitExit = function() {
        console.log("hello");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'location': $scope.data.location,
        };
        $state.go('menu.sensorDashboard', device_param);
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.submitQuery();
    });
    
    $scope.$on('$ionicView.beforeLeave', function(e) {
        console.log("beforeLeave");
        if ($scope.timer !== null) {
            clearTimeout($scope.timer);
            console.log("clearTimeout");
            $scope.timer = null;
        }
    });
}])
   
.controller('deviceGPIOCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

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
        { "id":0,  "label": "Negative"     },
        { "id":1,  "label": "Positive"     },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,

        'activeSection': 1,
        'showNotification': 0,
        'enableGPIO': true,
        'statusGPIO': true,
        'voltageidx': $scope.voltages[0].id,
        'hardware_devicename': $scope.devices[0].id,
        
        'gpio': {
            'direction'   : $scope.directions[0].id,
            'mode'        : $scope.modes[0].id,
            'alert'       : $scope.alerts[0].id,
            'alertperiod' : 10000,
            'polarity'    : $scope.polarities[0].id,
            'width'       : 1,
            'mark'        : 1,
            'space'       : 1,
            'count'       : 1,
        
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

    $scope.changeGPIO = function(i) {
        console.log(i);
        let title = "Enable GPIO";
        let action = "enable GPIO";
        if (i === false) {
            title = "Disable GPIO";
            action = "disable GPIO";
        }
        $ionicPopup.alert({ 
            title: title + $scope.data.activeSection.toString(), 
            template: 'Are you sure you want to ' + action + $scope.data.activeSection.toString() +'?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enableGPIO = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enableGPIO = i;
                        enable_gpio(i);
                    }
                }
            ]            
        });            
    };
    
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Device GPIO failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    

    get_devices = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
        });
    };
    
    get_gpios = function() {
        //
        // GET GPIOS
        //
        // - Request:
        //   GET /devices/device/<devicename>/gpios
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      'voltage': int,
        //      'gpios': [
        //         {'direction': int, 'status': int, 'enabled': int},
        //         {'direction': int, 'status': int, 'enabled': int}, 
        //         {'direction': int, 'status': int, 'enabled': int}, 
        //         {'direction': int, 'status': int, 'enabled': int}
        //      ]
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpios',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.value !== undefined) {
                if (result.data.value.voltage !== undefined) {
                    $scope.data.voltageidx = result.data.value.voltage;
                }
                if (result.data.value.gpios !== undefined) {
                    if (result.data.value.gpios[$scope.data.activeSection - 1].enabled !== undefined) {
                        // update enabled UI
                        if (result.data.value.gpios[$scope.data.activeSection - 1].enabled === 0) {
                            $scope.data.enableGPIO = false;
                        }
                        else {
                            $scope.data.enableGPIO = true;
                        }
                        // update status UI
                        if (result.data.value.gpios[$scope.data.activeSection - 1].status === 0) {
                            $scope.data.statusGPIO = false;
                        }
                        else {
                            $scope.data.statusGPIO = true;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
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
                
                // update $scope.data.hardware_devicename based on retrieved recipient
                if ($scope.data.gpio.notification.endpoints.modem.recipients !== "") {
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    for (indexy=0; indexy<$scope.devices.length; indexy++) {
                        if ($scope.devices[indexy].devicename === 
                            $scope.data.gpio.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                        }
                    }
                }                
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
            
            get_gpios();
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


    $scope.set_gpio_voltage = function() {
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
            $ionicPopup.alert({
                title: 'Device GPIO',
                template: 'GPIO voltage was configured successfully!',
            });
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    enable_gpio = function(enable) {
        var enable_int = 1;
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE GPIO
        //
        // - Request:
        //   POST /devices/device/<devicename>/gpio/<number>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/gpio/' + $scope.data.activeSection.toString()  + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device GPIO',
                template: 'GPIO ' + $scope.data.activeSection.toString() + ' was ' + action + ' successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    $scope.submit = function() {
        $scope.data.gpio.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        console.log($scope.data.gpio);
        if ($scope.data.gpio.direction === 0) {
            if ($scope.data.gpio.alertperiod < 5000) {
                $ionicPopup.alert({ title: 'Error', template: 'Alert period must be >= 5000!', 
                    buttons: [{text: 'OK', type: 'button-assertive'}] });
                $scope.data.gpio.alertperiod = 5000;
                return;
            }
        }
        else {
            if ($scope.data.gpio.mode === 1) {
                if ($scope.data.gpio.width < 1) {
                    $ionicPopup.alert({ title: 'Error', template: 'Width must be > 0!', 
                        buttons: [{text: 'OK', type: 'button-assertive'}] });
                    $scope.data.gpio.width = 100;
                    return;
                }
            }
            else if ($scope.data.gpio.mode === 2) {
                if ($scope.data.gpio.mark < 1) {
                    $ionicPopup.alert({ title: 'Error', template: 'Mark must be > 0!', 
                        buttons: [{text: 'OK', type: 'button-assertive'}] });
                    $scope.data.gpio.mark = 100;
                    return;
                }
                if ($scope.data.gpio.space < 1) {
                    $ionicPopup.alert({ title: 'Error', template: 'Space must be > 0!', 
                        buttons: [{text: 'OK', type: 'button-assertive'}] });
                    $scope.data.gpio.space = 100;
                    return;
                }
                if ($scope.data.gpio.count < 1) {
                    $ionicPopup.alert({ title: 'Error', template: 'Count must be > 0!', 
                        buttons: [{text: 'OK', type: 'button-assertive'}] });
                    $scope.data.gpio.count = 1;
                    return;
                }
            }
        }
        set_gpio_properties();
        $scope.data.enableGPIO = false;
    };

    $scope.submitQuery = function() {

        get_gpio_properties();
        //get_gpios(); // call inside get_uart_properties instead
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
            'location': $scope.data.location === "" ? "UNKNOWN" : $scope.data.location,
        };
        $state.go('device', device_param);
    };
    
    
    $scope.$on('$ionicView.enter', function(e) {
        $scope.submitQuery();
    });
    
    //$scope.submitQuery();
    //get_gpios();
    
    get_devices();    
}])
   
.controller('deviceUARTCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

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

    $scope.flowcontrols = [
        { "id":0, "label": "None" },
        { "id":1, "label": "Rts/Cts" },
        { "id":2, "label": "Xon/Xoff" },
    ];     
    
    $scope.stopbits = [
        { "id":0, "label": "1"   },
        { "id":1, "label": "2"   }
    ];     
    
    $scope.databits = [
        { "id":0, "label": "7" },
        { "id":1, "label": "8" },
    ];     

    $scope.devices = [ {"id":0, "devicename": ""} ];
    

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,
        
        'activeSection': 1,
        'showNotification': 0,
        'enableUART': true,
        'hardware_devicename': $scope.devices[0].id,
        
        'uart': {
            'baudrate': $scope.baudrates[7].id,
            'parity': $scope.parities[0].id,
            'flowcontrol': $scope.flowcontrols[0].id,
            'stopbits': $scope.stopbits[0].id,
            'databits': $scope.databits[1].id,
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

    //$scope.changeSection = function(s) {
    //    $scope.data.activeSection = s;
    //    $scope.submitQuery();
    //};
    
    $scope.setDefaultProperties = function() {
        $scope.data.uart.baudrate    = $scope.baudrates[7].id;
        $scope.data.uart.parity      = $scope.parities[0].id;
        $scope.data.uart.flowcontrol = $scope.flowcontrols[0].id;
        $scope.data.uart.stopbits    = $scope.stopbits[0].id;
        $scope.data.uart.databits    = $scope.databits[1].id;
    };
    
    
    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
    };

    $scope.changeUART = function(i) {
        console.log(i);
        let title = "Enable UART";
        let action = "enable UART";
        if (i === false) {
            title = "Disable UART";
            action = "disable UART";
        }
        $ionicPopup.alert({ 
            title: title,
            template: 'Are you sure you want to ' + action + '?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enableUART = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enableUART = i;
                        enable_uart(i);
                    }
                }
            ]            
        });            
    };

    
    handle_error = function(error, showerror=true) {
        if (error.data !== null) {
            console.log("ERROR: Device UART failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
 
 
    get_devices = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
        });
    };
    
    get_uart_properties = function() {
        //
        // GET UART PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/uart/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': 
        //     { 
        //      'baudrate': int,
        //      'parity': int,
        //      'databits': int,
        //      'stopbits': int,
        //      'flowcontrol': int,
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
            url: server + '/devices/device/' + $scope.data.devicename + '/uart/properties',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value.notification !== undefined) {
                $scope.data.uart = result.data.value;
                
                // update $scope.data.hardware_devicename based on retrieved recipient
                if ($scope.data.uart.notification.endpoints.modem.recipients !== "") {
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    for (indexy=0; indexy<$scope.devices.length; indexy++) {
                        if ($scope.devices[indexy].devicename === 
                            $scope.data.uart.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                        }
                    }
                }
            }
            else {
                $scope.data.uart.baudrate = result.data.value.baudrate;
                $scope.data.uart.parity = result.data.value.parity;
                $scope.data.uart.flowcontrol = result.data.value.flowcontrol;
                $scope.data.uart.stopbits = result.data.value.stopbits;
                $scope.data.uart.databits = result.data.value.databits;
            }
            
            get_uarts();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    set_uart_properties = function(param) {
        //
        // SET UART PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/uart/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'baudrate': int,
        //      'parity': int,
        //      'databits': int,
        //      'stopbits': int,
        //      'flowcontrol': int,
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
            url: server + '/devices/device/' + $scope.data.devicename + '/uart/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: param
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


    enable_uart = function(enable) {
        var enable_int = 1;        
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE UART
        //
        // - Request:
        //   POST /devices/device/<devicename>/uart/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/uart/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device UART',
                template: 'UART ' + $scope.data.activeSection.toString() + ' was ' + action + ' successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    

    get_uarts = function() {
        //
        // GET UARTS
        //
        // - Request:
        //   GET /devices/device/<devicename>/uarts
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      'uarts': [
        //         {'enabled': int},
        //      ]
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/uarts',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.value !== undefined) {
                if (result.data.value.uarts !== undefined) {
                    if (result.data.value.uarts[0].enabled !== undefined) {
                        if (result.data.value.uarts[0].enabled === 0) {
                            $scope.data.enableUART = false;
                        }
                        else {
                            $scope.data.enableUART = true;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };    


    $scope.submit = function() {
        $scope.data.uart.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        console.log($scope.data.uart.notification.endpoints.modem.recipients);
        console.log($scope.data.uart);
        set_uart_properties($scope.data.uart);
    };
    
    $scope.submitQuery = function() {

        get_uart_properties();
        //get_uarts(); // call inside get_uart_properties instead
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
            'location': $scope.data.location === "" ? "UNKNOWN" : $scope.data.location,
        };
        $state.go('device', device_param);
    };

    $scope.submitQuery();
    //get_profile();
    
    get_devices();
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
        'location': $stateParams.location,
        
        'activeSection': 1,
        'enableI2C': true,
    };

    $scope.sensors = [];
    $scope.sensors_counthdr = "No I2C device registered for I2C " + $scope.data.activeSection.toString();

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
        $scope.getI2CSensors();
        $scope.data.enableI2C = true;
    };
   

   
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Device I2C failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


/*
    // GET I2C SENSORS READINGS
    $scope.getI2CSensorsReadings = function() {
        console.log("getI2CSensorsReadings");
        get_i2c_sensors_readings();
    };

    get_i2c_sensors_readings = function() {
        //
        // GET I2C SENSORS READINGS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensor_readings': ['sensorname': string, ..., 'sensor_readings': {'value': int, 'lowest': int, 'highest': int}], ... }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.activeSection.toString() + '/sensors/readings',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log("sensor_readings ok");
            console.log(result.data);
            console.log("sensor_readings ok");
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };
*/

/*    
    get_i2cs = function() {
        //
        // GET I2CS
        //
        // - Request:
        //   GET /devices/device/<devicename>/i2cs
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      'i2cs': [
        //         {'enabled': int},
        //         {'enabled': int}, 
        //         {'enabled': int}, 
        //         {'enabled': int}
        //      ]
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2cs',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.value !== undefined) {
                if (result.data.value.i2cs !== undefined) {
                    if (result.data.value.i2cs[$scope.data.activeSection - 1].enabled !== undefined) {
                        if (result.data.value.i2cs[$scope.data.activeSection - 1].enabled === 0) {
                            $scope.data.enableI2C = false;
                        }
                        else {
                            $scope.data.enableI2C = true;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };
*/    
    
    
    // GET I2C DEVICES
    $scope.getI2CSensors = function() {
        console.log("getI2CSensors");
        get_i2c_sensors();
        //get_i2cs();
    };

    get_i2c_sensors = function() {
        //
        // GET I2C SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        time_start = Date.now();
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.activeSection.toString() + '/sensors',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(Date.now() - time_start);
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No I2C device registered for I2C " + $scope.data.activeSection.toString();
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 I2C device registered for I2C " + $scope.data.activeSection.toString();
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " I2C devices registered for I2C " + $scope.data.activeSection.toString();
            }
            
            // add for toggle button
            for (var i=0; i<$scope.sensors.length; i++) {
                if ($scope.sensors[i].enabled === 1) {
                    $scope.sensors[i].enabled_bool = true;
                }
                else {
                    $scope.sensors[i].enabled_bool = false;
                }
            }
            
            if (result.data.message.includes("offline")) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        })
        .catch(function (error) {
            console.log(Date.now() - time_start);
            handle_error(error);
        }); 
    };


    $scope.processSensor = function(sensor) {
        
        param = {
            'username': $scope.data.username,
            'token':$scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        param.sensor = sensor;
        param.source = "I2C";
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                // handle multiclass
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    
                    param.from = false;
                    param.attributes = {
                        'color': {
                            'usage': 0,
                            'single': {
                                'endpoint': 0,
                                'manual': 0,
                                'hardware': {
                                    //'deviceid': '',  
                                    'devicename': '',  
                                    'peripheral': '',  
                                    'sensorname': '',  
                                    'attribute': '',  
                                    //'number': 0,  
                                    //'address': 0,  
                                },
                            },
                            'individual': {
                                'red': {
                                    'endpoint': 0,
                                    'manual': 0,
                                    'hardware': {
                                        //'deviceid': '',  
                                        'devicename': '',  
                                        'peripheral': '',  
                                        'sensorname': '',  
                                        'attribute': '',  
                                        //'number': 0,  
                                        //'address': 0,  
                                    },
                                },
                                'green': {
                                    'endpoint': 0,
                                    'manual': 0,
                                    'hardware': {
                                        //'deviceid': '',  
                                        'devicename': '',  
                                        'peripheral': '',  
                                        'sensorname': '',  
                                        'attribute': '',  
                                        //'number': 0,  
                                        //'address': 0,  
                                    },
                                },
                                'blue': {
                                    'endpoint': 0,
                                    'manual': 0,
                                    'hardware': {
                                        //'deviceid': '',  
                                        'devicename': '',  
                                        'peripheral': '',  
                                        'sensorname': '',  
                                        'attribute': '',   
                                        //'number': 0,  
                                        //'address': 0,  
                                    },
                                },
                            },
                        },
                        'fadeouttime': 1,
                    };
    
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else {
                    $state.go('unknown', param);
                }
            }
        }
        else {
            param.sensor.class = "unknown";
            param.sensor.attributes = [];
            $state.go('unknown', param);
        }
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
        //   DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.activeSection.toString() + '/sensors/sensor/' + sensor.sensorname,
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


    // ENABLE SENSOR
    $scope.changeDevice = function(sensor, i) {
        console.log(i);
        enable_xxx_sensor(sensor, i, "i2c");
    };    
    
    enable_xxx_sensor = function(sensor, enable, peripheral) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device ' + peripheral.toUpperCase(),
                template: peripheral.toUpperCase() + ' Device ' + sensor.sensorname + ' on ' + peripheral.toUpperCase() + ' ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });
            
            // update
            get_i2c_sensors();
        })
        .catch(function (error) {
            handle_error(error);
            
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };


    // ADD I2C DEVICES    
    $scope.addI2CDevice = function() {
        console.log("addI2CDevice");
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            
            'i2cnumber': $scope.data.activeSection,
        };
        $state.go('addI2CDevice', device_param);
    };


    $scope.$on('$ionicView.enter', function(e) {
        $scope.sensors = [];
        $scope.sensors_counthdr = "No I2C device registered for I2C " + $scope.data.activeSection.toString();        
        $scope.getI2CSensors();
    });

    $scope.$on('$ionicView.beforeLeave', function(e) {
        $scope.sensors = [];
        $scope.sensors_counthdr = "No I2C device registered for I2C " + $scope.data.activeSection.toString();
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
            'location': $scope.data.location === "" ? "UNKNOWN" : $scope.data.location,
        };
        $state.go('device', device_param);
    };
}])
   
.controller('deviceADCCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.voltages = [
        { "id":0,  "label": "-5/+5V Range"   },
        { "id":1,  "label": "-10/+10V Range" },
        { "id":2,  "label": "0/10V Range"    },
    ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,
        
        'activeSection': 1,
        'enableADC': true,
        'voltage': 0,
    };

    $scope.sensors = [];
    $scope.sensors_counthdr = "No ADC device registered for ADC " + $scope.data.activeSection.toString();

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
        $scope.getADCSensors();
        $scope.data.enableADC = true;
    };
   
    $scope.changeADC = function(i) {
        console.log(i);
        let title = "Enable ADC";
        let action = "enable ADC";
        if (i === false) {
            title = "Disable ADC";
            action = "disable ADC";
        }
        $ionicPopup.alert({ 
            title: title + $scope.data.activeSection.toString(), 
            template: 'Are you sure you want to ' + action + $scope.data.activeSection.toString() +'?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enableADC = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enableADC = i;
                        enable_adc(i);
                    }
                }
            ]            
        });            
    };
   
   
   
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Device ADC failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
/*    
    get_adcs = function() {
        //
        // GET ADCS
        //
        // - Request:
        //   GET /devices/device/<devicename>/adcs
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      'adcs': [
        //         {'enabled': int},
        //         {'enabled': int}, 
        //         {'enabled': int}, 
        //         {'enabled': int}
        //      ]
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/adcs',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.value !== undefined) {
                if (result.data.value.adcs !== undefined) {
                    if (result.data.value.adcs[$scope.data.activeSection - 1].enabled !== undefined) {
                        if (result.data.value.adcs[$scope.data.activeSection - 1].enabled === 0) {
                            $scope.data.enableADC = false;
                        }
                        else {
                            $scope.data.enableADC = true;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };
*/    
    
    
    // GET ADC DEVICES
    $scope.getADCSensors = function() {
        console.log("getADCSensors");
        get_adc_sensors();
        //get_adcs();
    };

    get_adc_sensors = function() {
        //
        // GET ADC SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/adc/NUMBER/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.activeSection.toString() + '/sensors',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No ADC device registered for ADC " + $scope.data.activeSection.toString();
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 ADC device registered for ADC " + $scope.data.activeSection.toString();
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " ADC devices registered for ADC " + $scope.data.activeSection.toString();
            }
            
            // add for toggle button
            for (var i=0; i<$scope.sensors.length; i++) {
                if ($scope.sensors[i].enabled === 1) {
                    $scope.sensors[i].enabled_bool = true;
                }
                else {
                    $scope.sensors[i].enabled_bool = false;
                }
            }
            
            
            if (result.data.message.includes("offline")) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            
            get_adc_voltage();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    $scope.processSensor = function(sensor) {
        
        param = {
            'username': $scope.data.username,
            'token':$scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        param.sensor = sensor;
        param.source = "ADC";
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                // handle multiclass
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else if (sensor.class === "battery") {
                    $state.go('battery', param);
                }
                else if (sensor.class === "fluid") {
                    $state.go('fluid', param);
                }
                else {
                    $state.go('unknown', param);
                }
            }
        }
        else {
            param.sensor.class = "unknown";
            param.sensor.attributes = [];
            $state.go('unknown', param);
        }
    };


    // DELETE ADC SENSOR
    $scope.deleteADCSensor = function(sensor) {
        console.log("deleteADCSensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_adc_sensor(sensor);
                    }
                }
            ]            
        });
    };
    
    delete_adc_sensor = function(sensor) {
        //
        // DELETE ADC SENSOR
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.activeSection.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.getADCSensors();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    // ENABLE SENSOR
    $scope.changeDevice = function(sensor, i) {
        console.log(i);
        enable_xxx_sensor(sensor, i, "adc");
    };    
    
    enable_xxx_sensor = function(sensor, enable, peripheral) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device ' + peripheral.toUpperCase(),
                template: peripheral.toUpperCase() + ' Device ' + sensor.sensorname + ' on ' + peripheral.toUpperCase() + ' ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });
            
            // update
            get_adc_sensors();
        })
        .catch(function (error) {
            handle_error(error);
            
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };



    get_adc_voltage = function() {
        //
        // GET ADC VOLTAGE
        //
        // - Request:
        //   GET /devices/device/<devicename>/adc/voltage
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/voltage',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            $scope.data.voltage = result.data.value.voltage;
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };


    $scope.set_adc_voltage = function() {
        //
        // SET ADC VOLTAGE
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/voltage
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: { 'voltage': int }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/voltage',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'voltage': $scope.data.voltage }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device ADC',
                template: 'ADC voltage was configured successfully!',
            });
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    // ADD ADC DEVICES    
    $scope.addADCDevice = function() {
        console.log("add1WIREDevice");
        
        if ($scope.sensors.length > 0) {
            $ionicPopup.alert({ title: 'Error', template: 'Cannot add more than 1 ADC sensor device!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }
        
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            
            'adcnumber': $scope.data.activeSection,
        };
        $state.go('addADCDevice', device_param);        
    };


    $scope.$on('$ionicView.enter', function(e) {
        $scope.getADCSensors();
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
            'location': $scope.data.location === "" ? "UNKNOWN" : $scope.data.location,
        };
        $state.go('device', device_param);
    };
}])
   
.controller('deviceTPROBECtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.voltages = [
        { "id":0,  "label": "-5/+5V Range"   },
        { "id":1,  "label": "-10/+10V Range" },
        { "id":2,  "label": "0/10V Range"    },
    ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,
        
        'activeSection': 1,
        'enableTPROBE': true,
        'voltage': 0,
    };

    $scope.sensors = [];
    $scope.sensors_counthdr = "No TPROBE device registered";

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
        $scope.getTPROBESensors();
        $scope.data.enableTPROBE = true;
    };
   
    $scope.changeTPROBE = function(i) {
        console.log(i);
        let title = "Enable TPROBE";
        let action = "enable TPROBE";
        if (i === false) {
            title = "Disable TPROBE";
            action = "disable TPROBE";
        }
        $ionicPopup.alert({ 
            title: title + $scope.data.activeSection.toString(), 
            template: 'Are you sure you want to ' + action + $scope.data.activeSection.toString() +'?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enableTPROBE = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enableTPROBE = i;
                        enable_tprobe(i);
                    }
                }
            ]            
        });            
    };
   
   
   
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Device TPROBE failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
/*    
    get_tprobes = function() {
        //
        // GET TPROBES
        //
        // - Request:
        //   GET /devices/device/<devicename>/tprobes
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      'tprobes': [
        //         {'enabled': int},
        //         {'enabled': int}, 
        //         {'enabled': int}, 
        //         {'enabled': int}
        //      ]
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobes',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.value !== undefined) {
                if (result.data.value.tprobes !== undefined) {
                    if (result.data.value.tprobes[$scope.data.activeSection - 1].enabled !== undefined) {
                        if (result.data.value.tprobes[$scope.data.activeSection - 1].enabled === 0) {
                            $scope.data.enableTPROBE = false;
                        }
                        else {
                            $scope.data.enableTPROBE = true;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };
*/    
    
    
    // GET TPROBE DEVICES
    $scope.getTPROBESensors = function() {
        console.log("getTPROBESensors");
        get_tprobe_sensors();
        //get_tprobes();
    };

    get_tprobe_sensors = function() {
        //
        // GET TPROBE SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.activeSection.toString() + '/sensors',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No TPROBE device registered";
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 TPROBE device registered";
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " TPROBE devices registered";
            }
            
            // add for toggle button
            for (var i=0; i<$scope.sensors.length; i++) {
                if ($scope.sensors[i].enabled === 1) {
                    $scope.sensors[i].enabled_bool = true;
                }
                else {
                    $scope.sensors[i].enabled_bool = false;
                }
            }
            
            if (result.data.message.includes("offline")) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    $scope.processSensor = function(sensor) {
        
        param = {
            'username': $scope.data.username,
            'token':$scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        param.sensor = sensor;
        param.source = "TPROBE";
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                // handle multiclass
                param.multiclass = {
                    'attributes': '',    
                    'subattributes': '',    
                }
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else {
                    $state.go('unknown', param);
                }
            }
        }
        else {
            param.sensor.class = "unknown";
            param.sensor.attributes = [];
            $state.go('unknown', param);
        }
    };


    // DELETE TPROBE SENSOR
    $scope.deleteTPROBESensor = function(sensor) {
        console.log("deleteTPROBESensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_tprobe_sensor(sensor);
                    }
                }
            ]            
        });
    };
    
    delete_tprobe_sensor = function(sensor) {
        //
        // DELETE TPROBE SENSOR
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.activeSection.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.getTPROBESensors();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    // ENABLE SENSOR
    $scope.changeDevice = function(sensor, i) {
        console.log(i);
        enable_xxx_sensor(sensor, i, "tprobe");
    };    
    
    enable_xxx_sensor = function(sensor, enable, peripheral) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device ' + peripheral.toUpperCase(),
                template: peripheral.toUpperCase() + ' Device ' + sensor.sensorname + ' on ' + peripheral.toUpperCase() + ' ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });
            
            // update
            get_tprobe_sensors();
        })
        .catch(function (error) {
            handle_error(error);
            
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };



    // ADD TPROBE DEVICES    
    $scope.addTPROBEDevice = function() {
        console.log("addTPROBEDevice");
        
        if ($scope.sensors.length > 0) {
            $ionicPopup.alert({ title: 'Error', template: 'Cannot add more than 1 TPROBE sensor device!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            
            'tprobenumber': $scope.data.activeSection,
        };
        $state.go('addTPROBEDevice', device_param);        
    };


    $scope.$on('$ionicView.enter', function(e) {
        $scope.getTPROBESensors();
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
            'location': $scope.data.location === "" ? "UNKNOWN" : $scope.data.location,
        };
        $state.go('device', device_param);
    };
}])
   
.controller('device1WIRECtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.voltages = [
        { "id":0,  "label": "-5/+5V Range"   },
        { "id":1,  "label": "-10/+10V Range" },
        { "id":2,  "label": "0/10V Range"    },
    ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        'location': $stateParams.location,
        
        'activeSection': 1,
        'enable1WIRE': true,
        'voltage': 0,
    };

    $scope.sensors = [];
    $scope.sensors_counthdr = "No 1WIRE device registered";

    $scope.changeSection = function(s) {
        $scope.data.activeSection = s;
        $scope.get1WIRESensors();
        $scope.data.enable1WIRE = true;
    };
   
    $scope.change1WIRE = function(i) {
        console.log(i);
        let title = "Enable 1WIRE";
        let action = "enable 1WIRE";
        if (i === false) {
            title = "Disable 1WIRE";
            action = "disable 1WIRE";
        }
        $ionicPopup.alert({ 
            title: title + $scope.data.activeSection.toString(), 
            template: 'Are you sure you want to ' + action + $scope.data.activeSection.toString() +'?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enable1WIRE = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enable1WIRE = i;
                        enable_1wire(i);
                    }
                }
            ]            
        });            
    };
   
   
   
    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Device 1WIRE failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
/*    
    get_1wires = function() {
        //
        // GET 1WIRES
        //
        // - Request:
        //   GET /devices/device/<devicename>/1wires
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'value':
        //     { 
        //      '1wires': [
        //         {'enabled': int},
        //         {'enabled': int}, 
        //         {'enabled': int}, 
        //         {'enabled': int}
        //      ]
        //     }        
        //   }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wires',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.value !== undefined) {
                if (result.data.value.1wires !== undefined) {
                    if (result.data.value.1wires[$scope.data.activeSection - 1].enabled !== undefined) {
                        if (result.data.value.1wires[$scope.data.activeSection - 1].enabled === 0) {
                            $scope.data.enable1WIRE = false;
                        }
                        else {
                            $scope.data.enable1WIRE = true;
                        }
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, false);
        }); 
    };
*/    
    
    
    // GET 1WIRE DEVICES
    $scope.get1WIRESensors = function() {
        console.log("get1WIRESensors");
        get_1wire_sensors();
        //get_1wires();
    };

    get_1wire_sensors = function() {
        //
        // GET 1WIRE SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + $scope.data.activeSection.toString() + '/sensors',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            $scope.sensors = result.data.sensors;
            
            if ($scope.sensors.length === 0) {
                $scope.sensors_counthdr = "No 1WIRE device registered";
            }
            else if ($scope.sensors.length === 1) {
                $scope.sensors_counthdr = "1 1WIRE device registered";
            }
            else {
                $scope.sensors_counthdr = $scope.sensors.length.toString() + " 1WIRE devices registered";
            }
            
            // add for toggle button
            for (var i=0; i<$scope.sensors.length; i++) {
                if ($scope.sensors[i].enabled === 1) {
                    $scope.sensors[i].enabled_bool = true;
                }
                else {
                    $scope.sensors[i].enabled_bool = false;
                }
            }
            
            if (result.data.message.includes("offline")) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    $scope.processSensor = function(sensor) {
        
        param = {
            'username': $scope.data.username,
            'token':$scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
        };
        param.sensor = sensor;
        param.source = "1WIRE";
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                // handle multiclass
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else {
                    $state.go('multiclass', param);
                }
            }
        }
        else {
            param.sensor.class = "multiclass";
            param.sensor.attributes = [];
            $state.go('multiclass', param);
        }
    };


    // DELETE 1WIRE SENSOR
    $scope.delete1WIRESensor = function(sensor) {
        console.log("delete1WIRESensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_1wire_sensor(sensor);
                    }
                }
            ]            
        });
    };
    
    delete_1wire_sensor = function(sensor) {
        //
        // DELETE 1WIRE SENSOR
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + $scope.data.activeSection.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.get1WIRESensors();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };


    // ENABLE SENSOR
    $scope.changeDevice = function(sensor, i) {
        console.log(i);
        enable_xxx_sensor(sensor, i, "1wire");
    };    
    
    enable_xxx_sensor = function(sensor, enable, peripheral) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device ' + peripheral.toUpperCase(),
                template: peripheral.toUpperCase() + ' Device ' + sensor.sensorname + ' on ' + peripheral.toUpperCase() + ' ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });
            
            // update
            get_1wire_sensors();
        })
        .catch(function (error) {
            handle_error(error);
            
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };



    // ADD 1WIRE DEVICES    
    $scope.add1WIREDevice = function() {
        console.log("add1WIREDevice");
        
        if ($scope.sensors.length > 0) {
            $ionicPopup.alert({ title: 'Error', template: 'Cannot add more than 1 ONEWIRE sensor device!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            
            'onewirenumber': $scope.data.activeSection,
        };
        $state.go('add1WIREDevice', device_param);        
    };


    $scope.$on('$ionicView.enter', function(e) {
        $scope.get1WIRESensors();
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
            'location': $scope.data.location === "" ? "UNKNOWN" : $scope.data.location,
        };
        $state.go('device', device_param);
    };
}])
   
.controller('viewI2CDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'attributes': $stateParams.attributes,
        'enabled': $stateParams.sensor.enabled ? true: false,
    };
    
    $scope.sensor_readings = {
        'value': 0,
        'lowest': 0,
        'highest': 0,
    };


    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    // GET I2C SENSOR READING
    $scope.getI2CSensorReading = function(sensor) {
        console.log("getI2CSensorReading");
        get_i2c_sensor_reading(sensor);
    };

    get_i2c_sensor_reading = function(sensor) {
        //
        // GET I2C SENSOR READING
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.sensor_readings = result.data.sensor_readings;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE I2C SENSOR READING
    $scope.deleteI2CSensorReading = function(sensor) {
        console.log("deleteI2CSensorReading");
        delete_i2c_sensor_reading(sensor);
    };

    delete_i2c_sensor_reading = function(sensor) {
        //
        // DELETE I2C SENSOR READING
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE I2C SENSOR
    $scope.deleteI2CSensor = function() {
        console.log("deleteI2CSensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_i2c_sensor($scope.data.sensor);
                        $scope.submitDeviceList();
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
        //   DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };    
    
    
    // ENABLE I2C SENSOR
    $scope.changeI2CDevice = function(i) {
        console.log(i);
        let title = "Enable I2C Device";
        let action = "enable I2C device";
        if (i === false) {
            title = "Disable I2C Device";
            action = "disable I2C device";
        }
        $ionicPopup.alert({ 
            title: title, 
            template: 'Are you sure you want to ' + action + ' ' + $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number + '?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enable = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enable = i;
                        enable_i2c_sensor($scope.data.sensor, i);
                    }
                }
            ]            
        });            
    };    
    
    enable_i2c_sensor = function(sensor, enable) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE I2C SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device I2C',
                template: 'I2C Device ' + sensor.sensorname + ' on I2C ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
            
            $scope.data.enabled = $scope.data.enabled? false: true;
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };


    // GO BACK TO SPECIFIC I2C DEVICE PAGE
    $scope.processI2CSensor = function() {
        console.log("processI2CSensor");
        sensor = $scope.data.sensor;
        param = $scope.data;
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    param.from = false;
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else {
                    $state.go('unknown', param);
                }
            }
        }
        else {
            param.sensor.class = "unknown";
            param.sensor.attributes = [];
            $state.go('unknown', param);
        }
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
   
.controller('viewADCDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'attributes': $stateParams.attributes,
        'enabled': $stateParams.sensor.enabled ? true: false,
    };
    
    $scope.sensor_readings = {
        'value': 0,
        'lowest': 0,
        'highest': 0,
    };


    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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

    // GET ADC SENSOR READING
    $scope.getADCSensorReading = function(sensor) {
        console.log("getADCSensorReading");
        get_adc_sensor_reading(sensor);
    };

    get_adc_sensor_reading = function(sensor) {
        //
        // GET ADC SENSOR READING
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.sensor_readings = result.data.sensor_readings;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE ADC SENSOR READING
    $scope.deleteADCSensorReading = function(sensor) {
        console.log("deleteADCSensorReading");
        delete_adc_sensor_reading(sensor);
    };

    delete_adc_sensor_reading = function(sensor) {
        //
        // DELETE ADC SENSOR READING
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE ADC SENSOR
    $scope.deleteADCSensor = function() {
        console.log("deleteADCSensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_adc_sensor($scope.data.sensor);
                        $scope.submitDeviceList();
                    }
                }
            ]            
        });
    };
    
    delete_adc_sensor = function(sensor) {
        //
        // DELETE ADC SENSOR
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };    
    
    
    // ENABLE ADC SENSOR
    $scope.changeADCDevice = function(i) {
        console.log(i);
        let title = "Enable ADC Device";
        let action = "enable ADC device";
        if (i === false) {
            title = "Disable ADC Device";
            action = "disable ADC device";
        }
        $ionicPopup.alert({ 
            title: title, 
            template: 'Are you sure you want to ' + action + ' ' + $scope.data.sensor.sensorname + ' on ADC ' + $scope.data.sensor.number + '?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enable = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enable = i;
                        enable_adc_sensor($scope.data.sensor, i);
                    }
                }
            ]            
        });            
    };    
    
    enable_adc_sensor = function(sensor, enable) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE ADC SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device ADC',
                template: 'ADC Device ' + sensor.sensorname + ' on ADC ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
            
            $scope.data.enabled = $scope.data.enabled? false: true;
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };


    // GO BACK TO SPECIFIC ADC DEVICE PAGE
    $scope.processADCSensor = function() {
        console.log("processADCSensor");
        sensor = $scope.data.sensor;
        param = $scope.data;
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else if (sensor.class === "battery") {
                    $state.go('battery', param);
                }
                else if (sensor.class === "fluid") {
                    $state.go('fluid', param);
                }
                else {
                    $state.go('unknown', param);
                }
            }
        }
        else {
            param.sensor.class = "unknown";
            param.sensor.attributes = [];
            $state.go('unknown', param);
        }
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
        $state.go('deviceADC', device_param);
    };
}])
   
.controller('viewTPROBEDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        'multiclass': $stateParams.multiclass,
        
        'attributes': $stateParams.attributes,
        'enabled': $stateParams.sensor.enabled ? true: false,
    };
    
    $scope.sensor_readings = {
        'value': 0,
        'lowest': 0,
        'highest': 0,
    };

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    // GET TPROBE SENSOR READING
    $scope.getTPROBESensorReading = function(sensor) {
        console.log("getTPROBESensorReading");
        get_tprobe_sensor_reading(sensor);
    };

    get_tprobe_sensor_reading = function(sensor) {
        //
        // GET TPROBE SENSOR READING
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.sensor_readings = result.data.sensor_readings;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE TPROBE SENSOR READING
    $scope.deleteTPROBESensorReading = function(sensor) {
        console.log("deleteTPROBESensorReading");
        delete_tprobe_sensor_reading(sensor);
    };

    delete_tprobe_sensor_reading = function(sensor) {
        //
        // DELETE TPROBE SENSOR READING
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE TPROBE SENSOR
    $scope.deleteTPROBESensor = function() {
        console.log("deleteTPROBESensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_tprobe_sensor($scope.data.sensor);
                        $scope.submitDeviceList();
                    }
                }
            ]            
        });
    };
    
    delete_tprobe_sensor = function(sensor) {
        //
        // DELETE TPROBE SENSOR
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };    
    
    
    // ENABLE TPROBE SENSOR
    $scope.changeTPROBEDevice = function(i) {
        console.log(i);
        let title = "Enable TPROBE Device";
        let action = "enable TPROBE device";
        if (i === false) {
            title = "Disable TPROBE Device";
            action = "disable TPROBE device";
        }
        $ionicPopup.alert({ 
            title: title, 
            template: 'Are you sure you want to ' + action + ' ' + $scope.data.sensor.sensorname + ' on TPROBE ' + $scope.data.sensor.number + '?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enable = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enable = i;
                        enable_tprobe_sensor($scope.data.sensor, i);
                    }
                }
            ]            
        });            
    };    
    
    enable_tprobe_sensor = function(sensor, enable) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE TPROBE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/tprobe/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device TPROBE',
                template: 'TPROBE Device ' + sensor.sensorname + ' on TPROBE ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
            
            $scope.data.enabled = $scope.data.enabled? false: true;
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };


    // GO BACK TO SPECIFIC TPROBE DEVICE PAGE
    $scope.processTPROBESensor = function() {
        console.log("processTPROBESensor");
        sensor = $scope.data.sensor;
        param = $scope.data;
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else {
                    $state.go('unknown', param);
                }
            }
        }
        else {
            param.sensor.class = "unknown";
            param.sensor.attributes = [];
            $state.go('unknown', param);
        }
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
        $state.go('deviceTPROBE', device_param);
    };
}])
   
.controller('view1WIREDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'attributes': $stateParams.attributes,
        'enabled': $stateParams.sensor.enabled ? true: false,
    };
    
    $scope.sensor_readings = {
        'value': 0,
        'lowest': 0,
        'highest': 0,
    };

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    // GET 1WIRE SENSOR READING
    $scope.get1WIRESensorReading = function(sensor) {
        console.log("get1WIRESensorReading");
        get_1wire_sensor_reading(sensor);
    };

    get_1wire_sensor_reading = function(sensor) {
        //
        // GET 1WIRE SENSOR READING
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': int, 'lowest': int, 'highest': int} }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            $scope.sensor_readings = result.data.sensor_readings;
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE 1WIRE SENSOR READING
    $scope.delete1WIRESensorReading = function(sensor) {
        console.log("delete1WIRESensorReading");
        delete_1wire_sensor_reading(sensor);
    };

    delete_1wire_sensor_reading = function(sensor) {
        //
        // DELETE 1WIRE SENSOR READING
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/<sensorname>/readings
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname + "/readings",
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
        
    };

    
    // DELETE 1WIRE SENSOR
    $scope.delete1WIRESensor = function() {
        console.log("delete1WIRESensor");
        
        $ionicPopup.alert({ title: 'Delete Sensor', template: 'Are you sure you want to delete this sensor?',
            buttons: [
                { text: 'No', type: 'button-negative', },
                { text: 'Yes', type: 'button-assertive',
                    onTap: function(e) {
                        delete_1wire_sensor($scope.data.sensor);
                        $scope.submitDeviceList();
                    }
                }
            ]            
        });
    };
    
    delete_1wire_sensor = function(sensor) {
        //
        // DELETE 1WIRE SENSOR
        //
        // - Request:
        //   DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'DELETE',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + sensor.number.toString() + '/sensors/sensor/' + sensor.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };    
    
    
    // ENABLE 1WIRE SENSOR
    $scope.change1WIREDevice = function(i) {
        console.log(i);
        let title = "Enable 1WIRE Device";
        let action = "enable 1WIRE device";
        if (i === false) {
            title = "Disable 1WIRE Device";
            action = "disable 1WIRE device";
        }
        $ionicPopup.alert({ 
            title: title, 
            template: 'Are you sure you want to ' + action + ' ' + $scope.data.sensor.sensorname + ' on 1WIRE ' + $scope.data.sensor.number + '?',
            buttons: [{ 
                    text: 'No', type: 'button-negative',
                    onTap: function(e) {
                        $scope.data.enable = !i;
                    }
                }, {
                    text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        $scope.data.enable = i;
                        enable_1wire_sensor($scope.data.sensor, i);
                    }
                }
            ]            
        });            
    };    
    
    enable_1wire_sensor = function(sensor, enable) {
        var enable_int = 1;            
        action = "enabled";
        if (enable === false) {
            enable_int = 0;
            action = "disabled";
        }
        //
        // ENABLE/DISABLE 1WIRE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/1wire/<number>/sensors/sensor/<sensorname>/enable
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'enable': int}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + sensor.number.toString()  + '/sensors/sensor/' + sensor.sensorname + '/enable',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: { 'enable': enable_int }
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'Device 1WIRE',
                template: '1WIRE Device ' + sensor.sensorname + ' on 1WIRE ' + sensor.number.toString() + ' was ' + action + ' successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error);
            
            $scope.data.enabled = $scope.data.enabled? false: true;
            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
        }); 
    };


    // GO BACK TO SPECIFIC 1WIRE DEVICE PAGE
    $scope.process1WIRESensor = function() {
        console.log("process1WIRESensor");
        sensor = $scope.data.sensor;
        param = $scope.data;
        
        if (sensor.class !== undefined) {
            if (sensor.subclass !== undefined) {
                $state.go('multiclass', param);
            }
            else {
                if (sensor.class === "light") {
                    $state.go('light', param);
                }
                else if (sensor.class === "temperature") {
                    $state.go('temperature', param);
                }
                else if (sensor.class === "humidity") {
                    $state.go('humidity', param);
                }
                else if (sensor.class === "speaker") {
                    $state.go('speaker', param);
                }
                else if (sensor.class === "display") {
                    $state.go('display', param);
                }
                else if (sensor.class === "potentiometer") {
                    $state.go('potentiometer', param);
                }
                else if (sensor.class === "anemometer") {
                    $state.go('anemometer', param);
                }
                else {
                    $state.go('multiclass', param);
                }
            }
        }
        else {
            param.sensor.class = "multiclass";
            param.sensor.attributes = [];
            $state.go('multiclass', param);
        }
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
        $state.go('device1WIRE', device_param);
    };
}])
   
.controller('unknownCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
    };



    // VIEW I2C DEVICE
    $scope.viewI2CDevice = function() {
        console.log("viewI2CDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
        };
        $state.go('viewI2CDevice', device_param);
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
   
.controller('multiclassCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'multiclass': $stateParams.multiclass,
    };


    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Multiclass failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
    $scope.enterPage = function(sensor_class) {
        
        var param = $scope.data;
        console.log("enterPage " + sensor_class);
        console.log("1 " + $scope.data.multiclass.attributes);
        console.log("2 " + $scope.data.multiclass.subattributes);
        
        if (sensor_class === "light") {
            $state.go('light', param, {reload: true});
        }
        else if (sensor_class === "temperature") {
            $state.go('temperature', param, {reload: true});
        }
        else if (sensor_class === "humidity") {
            $state.go('humidity', param, {reload: true});
        }
        else if (sensor_class === "speaker") {
            $state.go('speaker', param, {reload: true});
        }
        else if (sensor_class === "display") {
            $state.go('display', param, {reload: true});
        }
        else if (sensor_class === "potentiometer") {
            $state.go('potentiometer', param, {reload: true});
        }
        else if (sensor_class === "anemometer") {
            $state.go('anemometer', param, {reload: true});
        }
        else {
            $state.go('unknown', param, {reload: true});
        }
        
    };



    $scope.submit = function() {
        console.log("submit");

        if ($scope.data.multiclass.attributes === "") {
            let template = $scope.data.sensor.class + " is not yet configured!";
            $ionicPopup.alert({ title: 'Error', template: template, buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }
        else if ($scope.data.multiclass.subattributes === "") {
            let template = $scope.data.sensor.subclass + " is not yet configured!";
            $ionicPopup.alert({ title: 'Error', template: template, buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }

        $scope.data.attributes = $scope.data.multiclass.attributes;
        $scope.data.attributes.subattributes = $scope.data.multiclass.subattributes;
        console.log($scope.data.attributes);
        
        
        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        
                        if ($scope.data.source === "I2C") {
                            set_i2c_properties();
                        }
                        else if ($scope.data.source === "TPROBE") {
                            set_tprobe_properties();
                        }
                        else if ($scope.data.source === "1WIRE") {
                            set_1wire_properties();
                        }
                        else if ($scope.data.source === "ADC") {
                            set_adc_properties();
                        }
                        
                    }
                }
            ]            
        });
    };

    set_i2c_properties = function() {
        //
        // SET I2C PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    
    set_tprobe_properties = function() {
        //
        // SET TPROBE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/tprobe/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'TPROBE device',
                template: $scope.data.sensor.sensorname + ' on TPROBE ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

    set_1wire_properties = function() {
        //
        // SET 1WIRE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/1wire/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: '1WIRE device',
                template: $scope.data.sensor.sensorname + ' on 1WIRE ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

    set_adc_properties = function() {
        //
        // SET ADC PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'ADC device',
                template: $scope.data.sensor.sensorname + ' on ADC ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    



    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        
        
        if ($scope.data.multiclass.attributes === '' && $scope.data.multiclass.subattributes === '') {
            if ($scope.data.source === "I2C") {
                //get_i2c_device_properties();
            }
            else if ($scope.data.source === "TPROBE") {
                get_tprobe_device_properties();
            }
            else if ($scope.data.source === "1WIRE") {
                //get_1wire_device_properties();
            }
        }
    };


    get_tprobe_device_properties = function() {
        //
        // GET TPROBE DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/tprobe/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.subattributes !== undefined) {
                    $scope.data.multiclass.attributes = result.data.value;
                    $scope.data.multiclass.subattributes = result.data.value.subattributes;
                    delete $scope.data.multiclass.attributes["subattributes"];
                    console.log($scope.data.multiclass.attributes);
                    console.log($scope.data.multiclass.subattributes);
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };



    // VIEW I2C DEVICE
    $scope.viewI2CDevice = function() {
        console.log("viewI2CDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $stateParams.source,
            'multiclass': $scope.data.multiclass,
        };
        
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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

        if ($scope.data.source === "I2C") {
           $state.go('deviceI2C', device_param);
        }
        else if ($scope.data.source === "ADC") {
           $state.go('deviceADC', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
           $state.go('deviceTPROBE', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
           $state.go('device1WIRE', device_param);
        }
    };
    
    $scope.submitRefresh();
}])
   
.controller('lightCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.colorusages = [
        { "id":0,  "label": "RGB as color"     },
        { "id":1,  "label": "RGB as component" },
    ];


    $scope.endpoints = [
        { "id":0,  "label": "Manual"   },
        { "id":1,  "label": "Hardware" },
    ];

    // handle hardware endpoint
    $scope.devices = [ {"id":0, "devicename": ""} ];
    $scope.i2cdevices = [ {"id":0, "sensorname": ""} ];
    $scope.i2cdevices_empty = [ {"id":0, "sensorname": ""} ];


    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'from': $stateParams.from,
        'attributes': $stateParams.attributes,
/*        
        'attributes': {
            'color': {
                'usage': $scope.colorusages[0].id,
                'single': {
                    'endpoint': $scope.endpoints[0].id,
                    'manual': 0,
                    'hardware': {
                        'devicename': "",
                        'sensorname': "",  
                    },
                },
                'individual': {
                    'red': {
                        'endpoint': $scope.endpoints[0].id,
                        'manual': 0,
                        'hardware': {
                            'devicename': "",
                            'sensorname': "",  
                        },
                    },
                    'blue': {
                        'endpoint': $scope.endpoints[0].id,
                        'manual': 0,
                        'hardware': {
                            'devicename': "",
                            'sensorname': "",  
                        },
                    },
                    'green': {
                        'endpoint': $scope.endpoints[0].id,
                        'manual': 0,
                        'hardware': {
                            'devicename': "",
                            'sensorname': "",  
                        },
                    },
                },
            },
            
            //'brightness': 100,
            'fadeouttime': 1,
        },
*/        
    };

    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Light failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
    $scope.configureColor = function(colortype) {
        param = {
            'username': $scope.data.username,
            'token':$scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
            'attributes': $scope.data.attributes,
            
            'colortype': colortype,
        };
        $state.go('lightRGB', param);
    };

    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        
        let send_all = false;
        if (send_all === true) {        
            if ($scope.data.attributes.color.usage === 0) {
                $scope.data.attributes.color.individual.red.hardware.devicename = "";
                $scope.data.attributes.color.individual.red.hardware.peripheral = "";
                $scope.data.attributes.color.individual.red.hardware.sensorname = "";
                $scope.data.attributes.color.individual.red.hardware.attribute = "";
    
                $scope.data.attributes.color.individual.green.hardware.devicename = "";
                $scope.data.attributes.color.individual.green.hardware.peripheral = "";
                $scope.data.attributes.color.individual.green.hardware.sensorname = "";
                $scope.data.attributes.color.individual.green.hardware.attribute = "";
    
                $scope.data.attributes.color.individual.blue.hardware.devicename = "";
                $scope.data.attributes.color.individual.blue.hardware.peripheral = "";
                $scope.data.attributes.color.individual.blue.hardware.sensorname = "";
                $scope.data.attributes.color.individual.blue.hardware.attribute = "";
            }
            else if ($scope.data.attributes.color.usage === 1) {
                $scope.data.attributes.color.single.hardware.devicename = "";
                $scope.data.attributes.color.single.hardware.peripheral = "";
                $scope.data.attributes.color.single.hardware.sensorname = "";
                $scope.data.attributes.color.single.hardware.attribute = "";
            }
            
            
            // Add prompt when setting properties
            $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
                buttons: [
                    { text: 'No', type: 'button-negative', },
                    { text: 'Yes', type: 'button-assertive',
                        onTap: function(e) {
                            
                            set_i2c_device_properties($scope.data.attributes);
                        }
                    }
                ]            
            });
        }
        else {
            param_attributes = {
                'color': {
                    'usage': $scope.data.attributes.color.usage,
                    'single': {},
                    'individual': {},
                },
                'fadeouttime': $scope.data.attributes.fadeouttime
            };
    
            if (param_attributes.color.usage === 0) {
                
                // RGB
                param_attributes.color.single.endpoint = $scope.data.attributes.color.single.endpoint;
                if (param_attributes.color.single.endpoint === 0) {
                    param_attributes.color.single.manual = $scope.data.attributes.color.single.manual;
                }
                else {
                    param_attributes.color.single.hardware = {};
                    param_attributes.color.single.hardware.devicename = $scope.data.attributes.color.single.hardware.devicename;
                    param_attributes.color.single.hardware.sensorname = $scope.data.attributes.color.single.hardware.sensorname;
                    param_attributes.color.single.hardware.peripheral = $scope.data.attributes.color.single.hardware.peripheral;
                    param_attributes.color.single.hardware.attribute  = $scope.data.attributes.color.single.hardware.attribute;
                }
                
            }
            else {

                // RED
                param_attributes.color.individual.red = {};
                param_attributes.color.individual.red.endpoint = $scope.data.attributes.color.individual.red.endpoint;
                if (param_attributes.color.individual.red.endpoint === 0) {
                    param_attributes.color.individual.red.manual = $scope.data.attributes.color.individual.red.manual;
                }
                else {
                    param_attributes.color.individual.red.hardware = {};
                    param_attributes.color.individual.red.hardware.devicename = $scope.data.attributes.color.individual.red.hardware.devicename;
                    param_attributes.color.individual.red.hardware.sensorname = $scope.data.attributes.color.individual.red.hardware.sensorname;
                    param_attributes.color.individual.red.hardware.peripheral = $scope.data.attributes.color.individual.red.hardware.peripheral;
                    param_attributes.color.individual.red.hardware.attribute  = $scope.data.attributes.color.individual.red.hardware.attribute;
                }
                
                // GREEN
                param_attributes.color.individual.green = {};
                param_attributes.color.individual.green.endpoint = $scope.data.attributes.color.individual.green.endpoint;
                if (param_attributes.color.individual.green.endpoint === 0) {
                    param_attributes.color.individual.green.manual = $scope.data.attributes.color.individual.green.manual;
                }
                else {
                    param_attributes.color.individual.green.hardware = {};
                    param_attributes.color.individual.green.hardware.devicename = $scope.data.attributes.color.individual.green.hardware.devicename;
                    param_attributes.color.individual.green.hardware.sensorname = $scope.data.attributes.color.individual.green.hardware.sensorname;
                    param_attributes.color.individual.green.hardware.peripheral = $scope.data.attributes.color.individual.green.hardware.peripheral;
                    param_attributes.color.individual.green.hardware.attribute  = $scope.data.attributes.color.individual.green.hardware.attribute;
                }

                // BLUE
                param_attributes.color.individual.blue = {};
                param_attributes.color.individual.blue.endpoint = $scope.data.attributes.color.individual.blue.endpoint;
                if (param_attributes.color.individual.blue.endpoint === 0) {
                    param_attributes.color.individual.blue.manual = $scope.data.attributes.color.individual.blue.manual;
                }
                else {
                    param_attributes.color.individual.blue.hardware = {};
                    param_attributes.color.individual.blue.hardware.devicename = $scope.data.attributes.color.individual.blue.hardware.devicename;
                    param_attributes.color.individual.blue.hardware.sensorname = $scope.data.attributes.color.individual.blue.hardware.sensorname;
                    param_attributes.color.individual.blue.hardware.peripheral = $scope.data.attributes.color.individual.blue.hardware.peripheral;
                    param_attributes.color.individual.blue.hardware.attribute  = $scope.data.attributes.color.individual.blue.hardware.attribute;
                }
                
            }


            // Add prompt when setting properties
            $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
                buttons: [
                    { text: 'No', type: 'button-assertive', },
                    { text: 'Yes', type: 'button-positive',
                        onTap: function(e) {
                            
                            set_i2c_device_properties(param_attributes);
                        }
                    }
                ]            
            });
        }        
    };

    set_i2c_device_properties = function(attributes) {
        //
        // SET I2C DEVICE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: attributes
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_i2c_device_properties();
    };

    get_i2c_device_properties = function() {
        //
        // GET I2C DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                
                let read_all = false;
                if (read_all === true) {
                    $scope.data.attributes = result.data.value;
                }
                else {
                    $scope.data.attributes.color.usage = result.data.value.color.usage;
                    
                    if ($scope.data.attributes.color.usage === 0) {
                        // RGB
                        $scope.data.attributes.color.single.endpoint = result.data.value.color.single.endpoint;
                        if ($scope.data.attributes.color.single.endpoint === 0) {
                            $scope.data.attributes.color.single.manual = result.data.value.color.single.manual;
                            $scope.data.attributes.color.single.hardware.devicename = ""; // default
                            $scope.data.attributes.color.single.hardware.peripheral = ""; // default
                            $scope.data.attributes.color.single.hardware.sensorname = ""; // default
                            $scope.data.attributes.color.single.hardware.attribute  = ""; // default
                        }
                        else {
                            $scope.data.attributes.color.single.manual = 0; // default
                            $scope.data.attributes.color.single.hardware.devicename = result.data.value.color.single.hardware.devicename;
                            $scope.data.attributes.color.single.hardware.peripheral = result.data.value.color.single.hardware.peripheral;
                            $scope.data.attributes.color.single.hardware.sensorname = result.data.value.color.single.hardware.sensorname;
                            $scope.data.attributes.color.single.hardware.attribute  = result.data.value.color.single.hardware.attribute;
                        }
                        
                        // RED
                        $scope.data.attributes.color.individual.red.endpoint = 0; // default
                        $scope.data.attributes.color.individual.red.manual = 0; // default
                        $scope.data.attributes.color.individual.red.hardware.devicename = ""; // default
                        $scope.data.attributes.color.individual.red.hardware.peripheral = ""; // default
                        $scope.data.attributes.color.individual.red.hardware.sensorname = ""; // default
                        $scope.data.attributes.color.individual.red.hardware.attribute  = ""; // default
                        
                        // GREEN
                        $scope.data.attributes.color.individual.green.endpoint = 0; // default
                        $scope.data.attributes.color.individual.green.manual = 0; // default
                        $scope.data.attributes.color.individual.green.hardware.devicename = ""; // default
                        $scope.data.attributes.color.individual.green.hardware.peripheral = ""; // default
                        $scope.data.attributes.color.individual.green.hardware.sensorname = ""; // default
                        $scope.data.attributes.color.individual.green.hardware.attribute  = ""; // default
                        
                        // BLUE
                        $scope.data.attributes.color.individual.blue.endpoint = 0; // default
                        $scope.data.attributes.color.individual.blue.manual = 0; // default
                        $scope.data.attributes.color.individual.blue.hardware.devicename = ""; // default
                        $scope.data.attributes.color.individual.blue.hardware.peripheral = ""; // default
                        $scope.data.attributes.color.individual.blue.hardware.sensorname = ""; // default
                        $scope.data.attributes.color.individual.blue.hardware.attribute  = ""; // default
                    }
                    else {
                        // RGB
                        $scope.data.attributes.color.single.endpoint = 0; // default
                        $scope.data.attributes.color.single.manual = 0; // default
                        $scope.data.attributes.color.single.hardware.devicename = ""; // default
                        $scope.data.attributes.color.single.hardware.peripheral = ""; // default
                        $scope.data.attributes.color.single.hardware.sensorname = ""; // default
                        $scope.data.attributes.color.single.hardware.attribute  = ""; // default

                        // RED
                        $scope.data.attributes.color.individual.red.endpoint = result.data.value.color.individual.red.endpoint;
                        if ($scope.data.attributes.color.individual.red.endpoint === 0) {
                            $scope.data.attributes.color.individual.red.manual = result.data.value.color.individual.red.manual;
                            $scope.data.attributes.color.individual.red.hardware.devicename = ""; // default
                            $scope.data.attributes.color.individual.red.hardware.peripheral = ""; // default
                            $scope.data.attributes.color.individual.red.hardware.sensorname = ""; // default
                            $scope.data.attributes.color.individual.red.hardware.attribute  = ""; // default
                        }
                        else {
                            $scope.data.attributes.color.individual.red.manual = 0; // default
                            $scope.data.attributes.color.individual.red.hardware.devicename = result.data.value.color.individual.red.hardware.devicename;
                            $scope.data.attributes.color.individual.red.hardware.peripheral = result.data.value.color.individual.red.hardware.peripheral;
                            $scope.data.attributes.color.individual.red.hardware.sensorname = result.data.value.color.individual.red.hardware.sensorname;
                            $scope.data.attributes.color.individual.red.hardware.attribute  = result.data.value.color.individual.red.hardware.attribute;
                        }
                        
                        // GREEN
                        $scope.data.attributes.color.individual.green.endpoint = result.data.value.color.individual.green.endpoint;
                        if ($scope.data.attributes.color.individual.green.endpoint === 0) {
                            $scope.data.attributes.color.individual.green.manual = result.data.value.color.individual.green.manual;
                            $scope.data.attributes.color.individual.green.hardware.devicename = ""; // default
                            $scope.data.attributes.color.individual.green.hardware.peripheral = ""; // default
                            $scope.data.attributes.color.individual.green.hardware.sensorname = ""; // default
                            $scope.data.attributes.color.individual.green.hardware.attribute  = ""; // default
                        }
                        else {
                            $scope.data.attributes.color.individual.green.manual = 0; // default
                            $scope.data.attributes.color.individual.green.hardware.devicename = result.data.value.color.individual.green.hardware.devicename;
                            $scope.data.attributes.color.individual.green.hardware.peripheral = result.data.value.color.individual.green.hardware.peripheral;
                            $scope.data.attributes.color.individual.green.hardware.sensorname = result.data.value.color.individual.green.hardware.sensorname;
                            $scope.data.attributes.color.individual.green.hardware.attribute  = result.data.value.color.individual.green.hardware.attribute;
                        }
                        
                        // BLUE
                        $scope.data.attributes.color.individual.blue.endpoint = result.data.value.color.individual.blue.endpoint;
                        if ($scope.data.attributes.color.individual.blue.endpoint === 0) {
                            $scope.data.attributes.color.individual.blue.manual = result.data.value.color.individual.blue.manual;
                            $scope.data.attributes.color.individual.blue.hardware.devicename = ""; // default
                            $scope.data.attributes.color.individual.blue.hardware.peripheral = ""; // default
                            $scope.data.attributes.color.individual.blue.hardware.sensorname = ""; // default
                            $scope.data.attributes.color.individual.blue.hardware.attribute  = ""; // default
                        }
                        else {
                            $scope.data.attributes.color.individual.blue.manual = 0; // default
                            $scope.data.attributes.color.individual.blue.hardware.devicename = result.data.value.color.individual.blue.hardware.devicename;
                            $scope.data.attributes.color.individual.blue.hardware.peripheral = result.data.value.color.individual.blue.hardware.peripheral;
                            $scope.data.attributes.color.individual.blue.hardware.sensorname = result.data.value.color.individual.blue.hardware.sensorname;
                            $scope.data.attributes.color.individual.blue.hardware.attribute  = result.data.value.color.individual.blue.hardware.attribute;
                        }
                    }
                    
                    $scope.data.attributes.fadeouttime = result.data.value.fadeouttime;
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


/*
    // handle hardware endpoint
    get_devices = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            get_i2c_device_properties();
        });
    };

    // handle hardware endpoint
    $scope.changeDevice = function() {
        var devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
        console.log(devicename);
        get_all_i2c_sensors(devicename, null);
    };
    
    // handle hardware endpoint
    get_all_i2c_sensors = function(devicename, sensorname) {
        //
        // GET ALL I2C SENSORS
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
            url: server + '/devices/device/' + devicename + '/i2c/sensors',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.sensors.length > 0) {
                $scope.i2cdevices = result.data.sensors;
                let indexy = 0;
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    $scope.i2cdevices[indexy].id = indexy;
                }
            }
            else {
                $scope.i2cdevices = $scope.i2cdevices_empty;
            }
            
            // select the correct sensor
            if (sensorname !== null) {
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    if ($scope.i2cdevices[indexy].sensorname === sensorname) {
                        $scope.data.hardware_sensorname = indexy;
                        break;
                    }
                }
            }
            if ($scope.data.hardware_sensorname >= result.data.sensors.length) {
                $scope.data.hardware_sensorname = 0;
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
*/



    // VIEW I2C DEVICE
    $scope.viewI2CDevice = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'attributes': $scope.data.attributes,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            console.log($scope.data.source);
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
/*    
    $scope.changeEndpoint = function() {
        if ($scope.data.attributes.endpoint === 1) {
            console.log("changeEndpoint");
            // handle hardware endpoint
            get_devices();    
        }
    };    
*/

    $scope.$on('$ionicView.enter', function(e) {
        if ($scope.data.from === false) {
            $scope.submitRefresh();
        }
    });   

}])
   
.controller('lightRGBCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.colorusages = [
        { "id":0,  "label": "RGB as single unit"   },
        { "id":1,  "label": "RGB as individual units" },
    ];


    $scope.endpoints = [
        { "id":0,  "label": "Manual"   },
        { "id":1,  "label": "Hardware" },
    ];


    $scope.peripherals = [
        { "id":0,  "label": "I2C"    },
        { "id":1,  "label": "ADC"    },
        { "id":2,  "label": "1WIRE"  },
        { "id":3,  "label": "TPROBE" },
    ];


    // handle hardware endpoint
    $scope.devices = [ {"id":0, "devicename": ""} ];
    $scope.i2cdevices = [ {"id":0, "sensorname": ""} ];
    $scope.i2cdevices_empty = [ {"id":0, "sensorname": ""} ];
    $scope.attributes = [ {"id":0, "attribute": ""} ];
    $scope.attributes_empty = [ {"id":0, "attribute": ""} ];


    $scope.datatemp = {
        'colorstr': '#000000',
        'colorRED'  : 0,
        'colorGREEN': 0,
        'colorBLUE' : 0,
        // handle hardware endpoint
        'hardware_devicename': $scope.devices[0].id,
        'hardware_peripheral': $scope.peripherals[0].id,
        'hardware_sensorname': $scope.i2cdevices[0].id,
        'hardware_attribute': $scope.i2cdevices[0].id,
    },


    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'attributes': $stateParams.attributes,
        
        'colortype': $stateParams.colortype,
    };


    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Light RGB failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("enter Light RGB");
        if ($scope.data.colortype === "RGB") {
            $scope.datatemp.colorRED = ($scope.data.attributes.color.single.manual & 0xFF0000) >> 16;
            $scope.datatemp.colorGREEN = ($scope.data.attributes.color.single.manual & 0x00FF00) >> 8; 
            $scope.datatemp.colorBLUE = ($scope.data.attributes.color.single.manual & 0x0000FF) >> 0;
        }
        
        if ($scope.data.colortype === "RGB") {
            if ($scope.data.attributes.color.single.endpoint === 1) {
                get_devices(
                    //$scope.data.attributes.color.single.hardware.deviceid,
                    $scope.data.attributes.color.single.hardware.devicename,
                    $scope.data.attributes.color.single.hardware.sensorname,
                    $scope.data.attributes.color.single.hardware.peripheral
                    );    
            }
        }
        else if ($scope.data.colortype === "RED") {
            if ($scope.data.attributes.color.individual.red.endpoint === 1) {
                get_devices(
                    //$scope.data.attributes.color.individual.red.hardware.deviceid,
                    $scope.data.attributes.color.individual.red.hardware.devicename,
                    $scope.data.attributes.color.individual.red.hardware.sensorname,
                    $scope.data.attributes.color.individual.red.hardware.peripheral
                    );    
            }
        }
        else if ($scope.data.colortype === "GREEN") {
            if ($scope.data.attributes.color.individual.green.endpoint === 1) {
                get_devices(
                    //$scope.data.attributes.color.individual.green.hardware.deviceid,
                    $scope.data.attributes.color.individual.green.hardware.devicename,
                    $scope.data.attributes.color.individual.green.hardware.sensorname,
                    $scope.data.attributes.color.individual.green.hardware.peripheral
                    );    
            }
        }
        else if ($scope.data.colortype === "BLUE") {
            if ($scope.data.attributes.color.individual.blue.endpoint === 1) {
                get_devices(
                    //$scope.data.attributes.color.individual.blue.hardware.deviceid,
                    $scope.data.attributes.color.individual.blue.hardware.devicename,
                    $scope.data.attributes.color.individual.blue.hardware.sensorname,
                    $scope.data.attributes.color.individual.blue.hardware.peripheral
                    );    
            }
        }
        
    });

    $scope.computeHexCode = function() {
        if ($scope.data.colortype === "RGB") {
            let red   = ("0" + parseInt($scope.datatemp.colorRED, 10).toString(16)).slice(-2).toUpperCase();
            let green = ("0" + parseInt($scope.datatemp.colorGREEN, 10).toString(16)).slice(-2).toUpperCase();
            let blue  = ("0" + parseInt($scope.datatemp.colorBLUE, 10).toString(16)).slice(-2).toUpperCase();
            $scope.datatemp.colorstr = "#" + red + green + blue;
            $scope.data.attributes.color.single.manual = parseInt("0x" + red + green + blue, 16);
            console.log($scope.data.attributes.color.single.manual);
        }
        else if ($scope.data.colortype === "RED") {
            let red   = parseInt($scope.data.attributes.color.individual.red.manual, 10);
            $scope.data.attributes.color.individual.red.manual = red;
            console.log($scope.data.attributes.color.individual.red.manual);
        }
        else if ($scope.data.colortype === "GREEN") {
            let green = parseInt($scope.data.attributes.color.individual.green.manual, 10);
            $scope.data.attributes.color.individual.green.manual = green;
            console.log($scope.data.attributes.color.individual.green.manual);
        }
        else if ($scope.data.colortype === "BLUE") {
            let blue  = parseInt($scope.data.attributes.color.individual.blue.manual, 10);
            $scope.data.attributes.color.individual.blue.manual = blue;
            console.log($scope.data.attributes.color.individual.blue.manual);
        }
    };

    //$scope.computeBrightness = function() {
    //    $scope.data.attributes.brightness = parseInt($scope.data.attributes.brightness, 10);
    //};
    
    $scope.computeRGB = function(keyEvent) {
        if (keyEvent.which === 13) {
            if ($scope.data.colortype === "RGB") {
                let color = $scope.datatemp.colorstr.replace("#", "0x");
                $scope.data.attributes.color.single.manual = parseInt(color.replace("#", "0x"), 16);
                $scope.datatemp.colorRED = ($scope.data.attributes.color.single.manual & 0xFF0000) >> 16;
                $scope.datatemp.colorGREEN = ($scope.data.attributes.color.single.manual & 0x00FF00) >> 8; 
                $scope.datatemp.colorBLUE = ($scope.data.attributes.color.single.manual & 0x0000FF) >> 0;
            }
        }
    };
    
    
    $scope.submitContinue = function() {
        console.log("submitContinue");
        console.log($scope.data.attributes);

        // handle hardware endpoint    
        if ($scope.data.colortype==="RGB") {
            if ($scope.data.attributes.color.single.endpoint === 1) {
                if ($scope.datatemp.hardware_devicename >= $scope.devices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_sensorname >= $scope.i2cdevices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_peripheral >= $scope.peripherals.length) {
                    return;
                }
                //$scope.data.attributes.color.single.hardware.deviceid = $scope.devices[$scope.datatemp.hardware_devicename].deviceid;
                $scope.data.attributes.color.single.hardware.devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
                $scope.data.attributes.color.single.hardware.sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
                
                //$scope.data.attributes.color.single.hardware.number = parseInt($scope.i2cdevices[$scope.datatemp.hardware_sensorname].number, 10);
                //if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].source == "i2c") {
                //    $scope.data.attributes.color.single.hardware.address = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].address;
                //}
                //else {
                //    $scope.data.attributes.color.single.hardware.address = 0;
                //}
                
                $scope.data.attributes.color.single.hardware.peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
                $scope.data.attributes.color.single.hardware.attribute = $scope.attributes[$scope.datatemp.hardware_attribute].attribute;
            }
        }
        else if ($scope.data.colortype==="RED") {
            if ($scope.data.attributes.color.individual.red.endpoint === 1) {
                if ($scope.datatemp.hardware_devicename >= $scope.devices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_sensorname >= $scope.i2cdevices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_peripheral >= $scope.peripherals.length) {
                    return;
                }
                //$scope.data.attributes.color.individual.red.hardware.deviceid = $scope.devices[$scope.datatemp.hardware_devicename].deviceid;
                $scope.data.attributes.color.individual.red.hardware.devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
                $scope.data.attributes.color.individual.red.hardware.sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
                
                //$scope.data.attributes.color.individual.red.hardware.number = parseInt($scope.i2cdevices[$scope.datatemp.hardware_sensorname].number, 10);
                //if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].source == "i2c") {
                //    $scope.data.attributes.color.individual.red.hardware.address = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].address;
                //}
                //else {
                //    $scope.data.attributes.color.individual.red.hardware.address = 0;
                //}

                $scope.data.attributes.color.individual.red.hardware.peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
                $scope.data.attributes.color.individual.red.hardware.attribute = $scope.attributes[$scope.datatemp.hardware_attribute].attribute;
            }
        }
        else if ($scope.data.colortype==="GREEN") {
            if ($scope.data.attributes.color.individual.green.endpoint === 1) {
                if ($scope.datatemp.hardware_devicename >= $scope.devices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_sensorname >= $scope.i2cdevices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_peripheral >= $scope.peripherals.length) {
                    return;
                }
                //$scope.data.attributes.color.individual.green.hardware.deviceid = $scope.devices[$scope.datatemp.hardware_devicename].deviceid;
                $scope.data.attributes.color.individual.green.hardware.devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
                $scope.data.attributes.color.individual.green.hardware.sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
                
                //$scope.data.attributes.color.individual.green.hardware.number = parseInt($scope.i2cdevices[$scope.datatemp.hardware_sensorname].number, 10);
                //if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].source == "i2c") {
                //    $scope.data.attributes.color.individual.green.hardware.address = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].address;
                //}
                //else {
                //    $scope.data.attributes.color.individual.green.hardware.address = 0;
                //}

                $scope.data.attributes.color.individual.green.hardware.peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
                $scope.data.attributes.color.individual.green.hardware.attribute = $scope.attributes[$scope.datatemp.hardware_attribute].attribute;
            }
        }
        else if ($scope.data.colortype==="BLUE") {
            if ($scope.data.attributes.color.individual.blue.endpoint === 1) {
                if ($scope.datatemp.hardware_devicename >= $scope.devices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_sensorname >= $scope.i2cdevices.length) {
                    return;
                }
                if ($scope.datatemp.hardware_peripheral >= $scope.peripherals.length) {
                    return;
                }
                //$scope.data.attributes.color.individual.blue.hardware.deviceid = $scope.devices[$scope.datatemp.hardware_devicename].deviceid;
                $scope.data.attributes.color.individual.blue.hardware.devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
                $scope.data.attributes.color.individual.blue.hardware.sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
                
                //$scope.data.attributes.color.individual.blue.hardware.number = parseInt($scope.i2cdevices[$scope.datatemp.hardware_sensorname].number, 10);
                //if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].source == "i2c") {
                //    $scope.data.attributes.color.individual.blue.hardware.address = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].address;
                //}
                //else {
                //    $scope.data.attributes.color.individual.blue.hardware.address = 0;
                //}

                $scope.data.attributes.color.individual.blue.hardware.peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
                $scope.data.attributes.color.individual.blue.hardware.attribute = $scope.attributes[$scope.datatemp.hardware_attribute].attribute;
            }
        }        

        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
            'attributes': $scope.data.attributes,
        };
        device_param.from = true;
        $state.go('light', device_param, {reload: true});
    };



    // handle hardware endpoint
    get_devices = function(devicename, sensorname, peripheral) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };

        console.log("get_devices");

        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
                
                if (devicename === $scope.devices[indexy].devicename) {
                    $scope.datatemp.hardware_devicename = indexy;
                }
                //if (deviceid === $scope.devices[indexy].deviceid) {
                //    $scope.datatemp.hardware_devicename = indexy;
                //}
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            
            // select the correct peripheral
            if (peripheral !== null) {
                $scope.datatemp.hardware_peripheral = 0;
                for (indexy=0; indexy<$scope.peripherals.length; indexy++) {
                    if ($scope.peripherals[indexy].label === peripheral) {
                        $scope.datatemp.hardware_peripheral = indexy;
                        break;
                    }
                }
            }

            //devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
            $scope.changePeripheral(devicename, sensorname);
        });
    };


    // handle hardware endpoint
    $scope.changeDevice = function() {
        var devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
        var sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
        if (sensorname === "") {
            $scope.changePeripheral(devicename, null);
        }
        else {
            $scope.changePeripheral(devicename, sensorname);
        }
    };
    
    $scope.changePeripheral = function(devicename, sensorname) {
        
        console.log("changePeripheral");
        
        if (devicename === undefined) {
            devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
            //console.log("changePeripheral " + $scope.data.hardware_devicename);
        }
        else if (devicename === "") {
            devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
        }
        if (sensorname === undefined) {
            sensorname = null;
        }
        
        var peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
        //console.log(devicename);
        //console.log(peripheral);
        if (peripheral === "I2C") {
            get_all_sensors(devicename, "i2c", sensorname);
        }
        else if (peripheral === "ADC") {
            get_all_sensors(devicename, "adc", sensorname);
        }
        else if (peripheral === "1WIRE") {
            get_all_sensors(devicename, "1wire", sensorname);
        }
        else if (peripheral === "TPROBE") {
            get_all_sensors(devicename, "tprobe", sensorname);
        }
    };
    
    
    // handle hardware endpoint
    get_all_sensors = function(devicename, peripheral, sensorname) {
        console.log("get_all_sensors " + peripheral + " " + sensorname);
        //
        // GET ALL SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        var url = server + '/devices/device/' + devicename + '/' + peripheral + '/sensors';
        if (peripheral === "i2c") {
            url += "/input";
        }
        
        $http({
            method: 'GET',
            url: url,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            // populate the list of sensors
            if (result.data.sensors.length > 0) {
                $scope.i2cdevices = result.data.sensors;
                let indexy = 0;
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    $scope.i2cdevices[indexy].id = indexy;
                }
            }
            else {
                $scope.i2cdevices = $scope.i2cdevices_empty;
            }
            
            // select the correct sensor
            if (sensorname !== null) {
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    if ($scope.i2cdevices[indexy].sensorname === sensorname) {
                        $scope.datatemp.hardware_sensorname = indexy;
                        break;
                    }
                }
            }
            else {
                $scope.datatemp.hardware_sensorname = 0;
            }
            if ($scope.datatemp.hardware_sensorname >= result.data.sensors.length) {
                $scope.datatemp.hardware_sensorname = 0;
            }
            
            $scope.changeSensor();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };

    $scope.changeSensor = function() {
        $scope.attributes = [];
        $scope.datatemp.hardware_attribute = 0;
        if ($scope.i2cdevices.length) {
            console.log("xxx 1");

            // populate the list of attributes
            $scope.attributes.push({
                'id': 0,
                'attribute': $scope.i2cdevices[$scope.datatemp.hardware_sensorname].attributes[0]
            });
            console.log("xxx 2");
            if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].subclass !== undefined) {
                $scope.attributes.push({
                    'id': 1,
                    'attribute': $scope.i2cdevices[$scope.datatemp.hardware_sensorname].subattributes[0]
                });
            }
            
            // select the attribute
            console.log("xxx 3");
            if ($scope.data.colortype==="RGB") {
                let indexy=0;
                for (indexy=0; indexy<$scope.attributes.length; indexy++) {
                console.log("xxx 4");
                    if ($scope.attributes[indexy].attribute === $scope.data.attributes.color.single.hardware.attribute) {
                console.log("xxx 5");
                        $scope.datatemp.hardware_attribute = indexy;
                        break;
                    }
                }
            }
            else if ($scope.data.colortype==="RED") {
                let indexy=0;
                for (indexy=0; indexy<$scope.attributes.length; indexy++) {
                console.log("xxx 4");
                    if ($scope.attributes[indexy].attribute === $scope.data.attributes.color.individual.red.hardware.attribute) {
                console.log("xxx 5");
                        $scope.datatemp.hardware_attribute = indexy;
                        break;
                    }
                }
            }
            else if ($scope.data.colortype==="GREEN") {
                let indexy=0;
                for (indexy=0; indexy<$scope.attributes.length; indexy++) {
                console.log("xxx 4");
                    if ($scope.attributes[indexy].attribute === $scope.data.attributes.color.individual.green.hardware.attribute) {
                console.log("xxx 5");
                        $scope.datatemp.hardware_attribute = indexy;
                        break;
                    }
                }
            }
            else if ($scope.data.colortype==="BLUE") {
                let indexy=0;
                for (indexy=0; indexy<$scope.attributes.length; indexy++) {
                console.log("xxx 4");
                    if ($scope.attributes[indexy].attribute === $scope.data.attributes.color.individual.blue.hardware.attribute) {
                console.log("xxx 5");
                        $scope.datatemp.hardware_attribute = indexy;
                        break;
                    }
                }
            }
            console.log("xxx 6");
            if ($scope.datatemp.hardware_attribute >= $scope.attributes.length) {
                $scope.datatemp.hardware_attribute = 0;
            }
        }
    };



    // EXIT PAGE
    $scope.submitExit = function() {
        console.log("submitExit");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
            'attributes': $scope.data.attributes,
        };
        device_param.from = true;
        $state.go('light', device_param);
    };
    
    $scope.changeEndpoint = function() {
        if ($scope.data.colortype==="RGB") {
            if ($scope.data.attributes.color.single.endpoint === 1) {
                console.log("changeEndpoint");
                get_devices("");
            }
        }
        else if ($scope.data.colortype==="RED") {
            if ($scope.data.attributes.color.individual.red.endpoint === 1) {
                console.log("changeEndpoint");
                get_devices("");    
            }
        }
        else if ($scope.data.colortype==="GREEN") {
            if ($scope.data.attributes.color.individual.green.endpoint === 1) {
                console.log("changeEndpoint");
                get_devices("");    
            }
        }
        else if ($scope.data.colortype==="BLUE") {
            if ($scope.data.attributes.color.individual.blue.endpoint === 1) {
                console.log("changeEndpoint");
                get_devices("");    
            }
        }
    };    
}])
   
.controller('temperatureCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.modes = [
        { "id":0,  "label": "Single Threshold"  },
        { "id":1,  "label": "Dual Threshold"  },
        { "id":2,  "label": "Continuous" },
    ];

    $scope.activates = [
        { "id":0,  "label": "Out of range" },
        { "id":1,  "label": "Within range" },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];    
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        'hardware_devicename': $scope.devices[0].id,
        
        'attributes': {
            'mode': $scope.modes[0].id,
            'threshold': {
                'value': 0,
                'min': 0,
                'max': 100,
                'activate': $scope.activates[0].id,
            },
            'alert': {
                'type': $scope.alerts[0].id,
                'period': 60000,
            },
            'hardware': {
                'devicename': '',  
            },
            
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
        
        'showNotification': 0,       
        
        // support for multiclasses
        //'multiclass_attributes': $stateParams.multiclass_attributes,
        //'multiclass_subattributes': $stateParams.multiclass_subattributes,
        'multiclass': $stateParams.multiclass
    };


    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Temperature failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
        if (i===true) {
            get_devices(false);    
        }    
    };
    
    
    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_devices(true);
    };

    get_xxx_device_properties = function(peripheral) {
        //
        // GET XXX DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.threshold !== undefined) {
                    $scope.data.attributes = result.data.value;
                    
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    
                    if ($scope.data.attributes.mode != 2) {
                        // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                    }
                    else {
                        // CONTINUOUS mode - use hardware.devicename
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                        $scope.data.attributes.alert.type = 1; // always be continuous
                    }
                }
                else {
                    $scope.data.attributes.notification = result.data.value.notification;
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };






    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        if ($scope.data.hardware_devicename >= $scope.devices.length) {
            return;
        }
        if ($scope.data.attributes.mode!=2) {
            // SINGLE/DUAL THRESHOLD modes
            $scope.data.attributes.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        else {
            // CONTINUOUS mode
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        
        
        if ($scope.data.sensor.subclass !== undefined) {
            var classname = "temperature";
            
            // support for multiclasses
            var param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': $scope.data.devicename,
                'devicestatus': $scope.data.devicestatus,
                'deviceid': $scope.data.deviceid,
                'serialnumber': $scope.data.serialnumber,
                'sensor': $scope.data.sensor,
                'source': $scope.data.source,
                'multiclass': $scope.data.multiclass,             
            };

            if ($scope.data.sensor.class === classname) {
                param.multiclass.attributes = $scope.data.attributes;
            }
            else if ($scope.data.sensor.subclass === classname) {
                param.multiclass.subattributes = $scope.data.attributes;
            }
            $state.go('multiclass', param, {reload: true});
        }
        else {
            
            // Add prompt when setting properties
            $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
                buttons: [
                    { text: 'No', type: 'button-assertive', },
                    { text: 'Yes', type: 'button-positive',
                        onTap: function(e) {
                            
                            if ($scope.data.source === "I2C") {
                                set_i2c_properties();
                            }
                            else if ($scope.data.source === "TPROBE") {
                                set_tprobe_properties();
                            }
                            else if ($scope.data.source === "1WIRE") {
                                set_1wire_properties();
                            }
                        }
                    }
                ]            
            });
        }
    };

    set_i2c_properties = function() {
        //
        // SET I2C PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    
    set_tprobe_properties = function() {
        //
        // SET TPROBE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/tprobe/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'TPROBE device',
                template: $scope.data.sensor.sensorname + ' on TPROBE ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

    set_1wire_properties = function() {
        //
        // SET 1WIRE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/1wire/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: '1WIRE device',
                template: $scope.data.sensor.sensorname + ' on 1WIRE ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };




    get_devices = function(flag) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            if (flag) {
                if ($scope.data.source === "I2C") {
                    get_xxx_device_properties("i2c");
                }
                else if ($scope.data.source === "ADC") {
                    get_xxx_device_properties("adc");
                }
                else if ($scope.data.source === "TPROBE") {
                    get_xxx_device_properties("tprobe");
                }
                else if ($scope.data.source === "1WIRE") {
                    get_xxx_device_properties("1wire");
                }
            }
        });
    };

    // VIEW I2C DEVICE
    $scope.viewXXXDevice = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
            'multiclass': $scope.data.multiclass,             
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeMode = function() {
        console.log("changeMode");
        get_devices(false);    
    };    
    
    $scope.submitRefresh();  
}])
   
.controller('humidityCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.modes = [
        { "id":0,  "label": "Single Threshold"  },
        { "id":1,  "label": "Dual Threshold"  },
        { "id":2,  "label": "Continuous" },
    ];

    $scope.activates = [
        { "id":0,  "label": "Out of range" },
        { "id":1,  "label": "Within range" },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];    
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        'hardware_devicename': $scope.devices[0].id,
        
        'attributes': {
            'mode': $scope.modes[0].id,
            'threshold': {
                'value': 0,
                'min': 0,
                'max': 100,
                'activate': $scope.activates[0].id,
            },
            'alert': {
                'type': $scope.alerts[0].id,
                'period': 60000,
            },
            'hardware': {
                'devicename': '',  
            },
            
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
        
        'showNotification': 0,  
        
        // support for multiclasses
        //'multiclass_attributes': $stateParams.multiclass_attributes,
        //'multiclass_subattributes': $stateParams.multiclass_subattributes,
        'multiclass': $stateParams.multiclass
    };

    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Humidity failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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

    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
        if (i===true) {
            get_devices(false);    
        }    
    };
    
    
    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_devices(true); 
    };

    get_xxx_device_properties = function(peripheral) {
        //
        // GET xxx DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.subattributes === undefined) {
                    if (result.data.value.threshold !== undefined) {
                        $scope.data.attributes = result.data.value;
                        
                        $scope.data.hardware_devicename = 0;
                        let indexy = 0;

                        if ($scope.data.attributes.mode != 2) {
                            // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                                if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                    $scope.data.hardware_devicename = indexy;
                                    break;
                                }
                            }
                        }
                        else {
                            // CONTINUOUS mode - use hardware.devicename
                            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                                if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                    $scope.data.hardware_devicename = indexy;
                                    break;
                                }
                            }
                            $scope.data.attributes.alert.type = 1; // always be continuous
                        }                        
                    }
                    else {
                        $scope.data.attributes.notification = result.data.value.notification;
                    }
                }
                else {
                    if (result.data.value.subattributes.threshold !== undefined) {
                        $scope.data.attributes = result.data.value.subattributes;
                        
                        $scope.data.hardware_devicename = 0;
                        let indexy = 0;
                        
                        if ($scope.data.attributes.mode != 2) {
                            // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                                if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                    $scope.data.hardware_devicename = indexy;
                                    break;
                                }
                            }
                        }
                        else {
                            // CONTINUOUS mode - use hardware.devicename
                            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                                if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                    $scope.data.hardware_devicename = indexy;
                                    break;
                                }
                            }
                            $scope.data.attributes.alert.type = 1; // always be continuous
                        }                        
                    }
                    else {
                        $scope.data.attributes.notification = result.data.value.subattributes.notification;
                    }
                    
                    if ($scope.data.sensor.class === "humidity") {
                        $scope.data.multiclass.attributes = $scope.data.attributes;
                    }
                    else if ($scope.data.sensor.subclass === "humidity") {
                        $scope.data.multiclass.subattributes = $scope.data.attributes;
                    }
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        if ($scope.data.hardware_devicename >= $scope.devices.length) {
            return;
        }
        if ($scope.data.attributes.mode!=2) {
            // SINGLE/DUAL THRESHOLD modes
            $scope.data.attributes.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        else {
            // CONTINUOUS mode
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        
        
        if ($scope.data.sensor.subclass !== undefined) {
            var classname = "humidity";
            
            // support for multiclasses
            var param = {
                'username': $scope.data.username,
                'token': $scope.data.token,
                'devicename': $scope.data.devicename,
                'devicestatus': $scope.data.devicestatus,
                'deviceid': $scope.data.deviceid,
                'serialnumber': $scope.data.serialnumber,
                'sensor': $scope.data.sensor,
                'source': $scope.data.source,
                'multiclass': $scope.data.multiclass,             
            };

            if ($scope.data.sensor.class === classname) {
                param.multiclass.attributes = $scope.data.attributes;
            }
            else if ($scope.data.sensor.subclass === classname) {
                param.multiclass.subattributes = $scope.data.attributes;
            }
            $state.go('multiclass', param, {reload: true});
        }
        else {
            
            // Add prompt when setting properties
            $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
                buttons: [
                    { text: 'No', type: 'button-assertive', },
                    { text: 'Yes', type: 'button-positive',
                        onTap: function(e) {
                            
                            if ($scope.data.source === "I2C") {
                                set_i2c_properties();
                            }
                            else if ($scope.data.source === "TPROBE") {
                                set_tprobe_properties();
                            }
                            else if ($scope.data.source === "1WIRE") {
                                set_1wire_properties();
                            }
                        }
                    }
                ]            
            });
        }
    };

    set_i2c_properties = function() {
        //
        // SET I2C PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    
    set_tprobe_properties = function() {
        //
        // SET TPROBE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/tprobe/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: 'TPROBE device',
                template: $scope.data.sensor.sensorname + ' on TPROBE ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

    set_1wire_properties = function() {
        //
        // SET 1WIRE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/1wire/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            $ionicPopup.alert({
                title: '1WIRE device',
                template: $scope.data.sensor.sensorname + ' on 1WIRE ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };




    get_devices = function(flag) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            if (flag) {
                if ($scope.data.source === "I2C") {
                    get_xxx_device_properties("i2c");
                }
                else if ($scope.data.source === "ADC") {
                    get_xxx_device_properties("adc");
                }
                else if ($scope.data.source === "TPROBE") {
                    get_xxx_device_properties("tprobe");
                }
                else if ($scope.data.source === "1WIRE") {
                    get_xxx_device_properties("1wire");
                }
            }
        });
    };

    // VIEW I2C DEVICE
    $scope.viewXXXDevice = function() {
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
            'multiclass': $scope.data.multiclass,             
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeMode = function() {
        console.log("changeMode");
        get_devices(false);    
    };    
    
    $scope.submitRefresh();  
}])
   
.controller('displayCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.endpoints = [
        { "id":0,  "label": "Manual"   },
        { "id":1,  "label": "Hardware" },
    ];

    $scope.formats = [
        { "id":0,  "label": "0x00 to 0xFF" },
        { "id":1,  "label": "0 to 99"      },
        { "id":2,  "label": "0.0 to 9.9"   },
    ];

    $scope.peripherals = [
        { "id":0,  "label": "I2C"    },
        { "id":1,  "label": "ADC"    },
        { "id":2,  "label": "1WIRE"  },
        { "id":3,  "label": "TPROBE" },
    ];

    // handle hardware endpoint
    $scope.devices = [ {"id":0, "devicename": ""} ];
    $scope.i2cdevices = [ {"id":0, "sensorname": ""} ];
    $scope.i2cdevices_empty = [ {"id":0, "sensorname": ""} ];
    $scope.attributes = [ {"id":0, "attribute": ""} ];
    $scope.attributes_empty = [ {"id":0, "attribute": ""} ];

    $scope.datatemp = {
        'brightness': 255,
        // handle hardware endpoint
        'hardware_devicename': $scope.devices[0].id,
        'hardware_peripheral': $scope.peripherals[0].id,
        'hardware_sensorname': $scope.i2cdevices[0].id,
        'hardware_attribute': $scope.i2cdevices[0].id,        
    };

    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'attributes': {
            'endpoint': $scope.endpoints[0].id,
            'hardware': {
                //'deviceid': '',  
                'devicename': '',  
                'peripheral': '',  
                'sensorname': '',  
                'attribute': '',  
                //'number': 0,  
                //'address': 0,
            },
            'brightness': 255,
            'format': $scope.formats[0].id,
            'text': '23',
        },
    };


    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Display failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    $scope.computeBrightness = function() {
        let brightness   = parseInt($scope.datatemp.brightness, 10);
        $scope.data.attributes.brightness = brightness;
        console.log($scope.data.attributes.brightness);
    };
    
    $scope.checkboxSelect = function(event) {
        console.log(event);
        console.log(event.checked);
    };


    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        // handle hardware endpoint    
        if ($scope.data.attributes.endpoint == 1) {
            if ($scope.datatemp.hardware_devicename >= $scope.devices.length) {
                return;
            }
            if ($scope.datatemp.hardware_sensorname >= $scope.i2cdevices.length) {
                return;
            }
            if ($scope.datatemp.hardware_peripheral >= $scope.peripherals.length) {
                return;
            }
            //$scope.data.attributes.hardware.deviceid   = $scope.devices[$scope.datatemp.hardware_devicename].deviceid;
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
            $scope.data.attributes.hardware.sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
            $scope.data.attributes.hardware.peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
            $scope.data.attributes.hardware.attribute  = $scope.attributes[$scope.datatemp.hardware_attribute].attribute;
            //$scope.data.attributes.hardware.number     = parseInt($scope.i2cdevices[$scope.datatemp.hardware_sensorname].number, 10);
            //if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].source == "i2c") {
            //    $scope.data.attributes.hardware.address    = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].address;
            //}
        }


        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        
                        set_i2c_properties();
                    }
                }
            ]            
        });
    };

    set_i2c_properties = function() {
        //
        // SET I2C PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_i2c_device_properties();
    };

    get_i2c_device_properties = function() {
        //
        // GET I2C DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                $scope.data.attributes = result.data.value;

                $scope.datatemp.brightness = $scope.data.attributes.brightness;

                // handle hardware endpoint
                if ($scope.data.attributes.endpoint == 1) {
                    get_devices(
                        $scope.data.attributes.hardware.devicename, 
                        $scope.data.attributes.hardware.sensorname, 
                        $scope.data.attributes.hardware.peripheral
                    );
                }

/*                
                // handle hardware endpoint
                if ($scope.data.attributes.endpoint == 1) {
                    
                    // pick the device
                    let indexy = 0;
                    for (indexy=0; indexy<$scope.devices.length; indexy++) {
                        if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                            $scope.data.hardware_devicename = indexy;
                            break;
                        }
                    }

                    // pick the peripheral    
                    for (indexy=0; indexy<$scope.peripherals.length; indexy++) {
                        if ($scope.peripherals[indexy].label === $scope.data.attributes.hardware.peripheral) {
                            $scope.data.hardware_peripheral = indexy;
                            break;
                        }
                    }
                    
                    // get all the sensors given the devicename and peripheral
                    get_all_sensors($scope.data.attributes.hardware.devicename, $scope.data.attributes.hardware.peripheral);
                }
*/                
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    // handle hardware endpoint
    get_devices = function(devicename, sensorname, peripheral) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            // populate the list of devices
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
                
                if (devicename === $scope.devices[indexy].devicename) {
                    $scope.datatemp.hardware_devicename = indexy;
                }
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            // select the correct peripheral
            if (peripheral !== null) {
                $scope.datatemp.hardware_peripheral = 0;
                for (indexy=0; indexy<$scope.peripherals.length; indexy++) {
                    if ($scope.peripherals[indexy].label === peripheral) {
                        $scope.datatemp.hardware_peripheral = indexy;
                        break;
                    }
                }
            }

            $scope.changePeripheral(devicename, sensorname);
        });
    };

    // handle hardware endpoint
    $scope.changeDevice = function() {
        var devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
        var sensorname = $scope.i2cdevices[$scope.datatemp.hardware_sensorname].sensorname;
        if (sensorname === "") {
            $scope.changePeripheral(devicename, null);
        }
        else {
            $scope.changePeripheral(devicename, sensorname);
        }
    };
    
    $scope.changePeripheral = function(devicename, sensorname) {
        
        console.log("changePeripheral");
        
        if (devicename === undefined) {
            devicename = $scope.devices[$scope.datatemp.hardware_devicename].devicename;
            //console.log("changePeripheral " + $scope.data.hardware_devicename);
        }
        if (sensorname === undefined) {
            sensorname = null;
        }
        
        var peripheral = $scope.peripherals[$scope.datatemp.hardware_peripheral].label;
        console.log(devicename);
        console.log(peripheral);
        if (peripheral === "I2C") {
            get_all_sensors(devicename, "i2c", sensorname);
        }
        else if (peripheral === "ADC") {
            get_all_sensors(devicename, "adc", sensorname);
        }
        else if (peripheral === "1WIRE") {
            get_all_sensors(devicename, "1wire", sensorname);
        }
        else if (peripheral === "TPROBE") {
            get_all_sensors(devicename, "tprobe", sensorname);
        }
    };
    
    // handle hardware endpoint
    get_all_sensors = function(devicename, peripheral, sensorname) {
        console.log("get_all_sensors " + peripheral + " " + sensorname);
        //
        // GET ALL SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        var url = server + '/devices/device/' + devicename + '/' + peripheral + '/sensors';
        if (peripheral === "i2c") {
            url += "/input";
        }
        
        $http({
            method: 'GET',
            url: url,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            // populate the list of sensors
            if (result.data.sensors.length > 0) {
                $scope.i2cdevices = result.data.sensors;
                let indexy = 0;
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    $scope.i2cdevices[indexy].id = indexy;
                }
            }
            else {
                $scope.i2cdevices = $scope.i2cdevices_empty;
            }
            
            // select the correct sensor
            if (sensorname !== null) {
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    if ($scope.i2cdevices[indexy].sensorname === sensorname) {
                        $scope.datatemp.hardware_sensorname = indexy;
                        break;
                    }
                }
            }
            if ($scope.datatemp.hardware_sensorname >= result.data.sensors.length) {
                $scope.datatemp.hardware_sensorname = 0;
            }
            
            $scope.changeSensor();
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    $scope.changeSensor = function() {
        $scope.attributes = [];
        $scope.datatemp.hardware_attribute = 0;
        if ($scope.i2cdevices.length) {

            // populate the list of attributes
            $scope.attributes.push({
                'id': 0,
                'attribute': $scope.i2cdevices[$scope.datatemp.hardware_sensorname].attributes[0]
            });
            if ($scope.i2cdevices[$scope.datatemp.hardware_sensorname].subclass !== undefined) {
                $scope.attributes.push({
                    'id': 1,
                    'attribute': $scope.i2cdevices[$scope.datatemp.hardware_sensorname].subattributes[0]
                });
            }
            
            // select the attribute
            let indexy=0;
            for (indexy=0; indexy<$scope.attributes.length; indexy++) {
                if ($scope.attributes[indexy].attribute === $scope.data.attributes.hardware.attribute) {
                    $scope.datatemp.hardware_attribute = indexy;
                    break;
                }
            }
            if ($scope.datatemp.hardware_attribute >= $scope.attributes.length) {
                $scope.datatemp.hardware_attribute = 0;
            }
        }
    };
    
    // VIEW I2C DEVICE
    $scope.viewI2CDevice = function() {
        console.log("viewI2CDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeEndpoint = function() {
        if ($scope.data.attributes.endpoint === 1) {
            console.log("changeEndpoint");
            // handle hardware endpoint
            get_devices();    
        }
    };    
    
    $scope.submitRefresh();
}])
   
.controller('speakerCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.endpoints = [
        { "id":0,  "label": "Manual"   },
        { "id":1,  "label": "Hardware" },
    ];
    
    $scope.peripherals = [
        { "id":0,  "label": "I2C"    },
        { "id":1,  "label": "ADC"    },
        { "id":2,  "label": "1WIRE"  },
        { "id":3,  "label": "TPROBE" },
    ];    
    
    // handle hardware endpoint
    $scope.devices = [ {"id":0, "devicename": ""} ];
    $scope.i2cdevices = [ {"id":0, "sensorname": ""} ];
    $scope.i2cdevices_empty = [ {"id":0, "sensorname": ""} ];
    $scope.types = [ {"id":0, "type": "midi"} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'attributes': {
            'endpoint': $scope.endpoints[0].id,
            'hardware': {
                'deviceid': '',  
                'devicename': '',  
                'peripheral': '',  
                'sensorname': '',  
                'attribute': '',  
                'number': 0,  
                'address': 0,
            },
            'type': $scope.types[0].id,
            'values': {
                'duration': 100,
                'pitch': 55,
                'delay': 100,
            }
        },
        
        // handle hardware endpoint
        'hardware_devicename': $scope.devices[0].id,
        'hardware_peripheral': $scope.peripherals[0].id,
        'hardware_sensorname': $scope.i2cdevices[0].id,
        'hardware_attribute' : $scope.i2cdevices[0].id,
    };


    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Speaker failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        // handle hardware endpoint    
        if ($scope.data.attributes.endpoint == 1) {
            if ($scope.data.hardware_devicename >= $scope.devices.length) {
                return;
            }
            if ($scope.data.hardware_sensorname >= $scope.i2cdevices.length) {
                return;
            }
            if ($scope.data.hardware_peripheral >= $scope.peripherals.length) {
                return;
            }
            $scope.data.attributes.hardware.deviceid   = $scope.devices[$scope.data.hardware_devicename].deviceid;
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
            $scope.data.attributes.hardware.sensorname = $scope.i2cdevices[$scope.data.hardware_sensorname].sensorname;
            $scope.data.attributes.hardware.peripheral = $scope.peripherals[$scope.data.hardware_peripheral].label;
            $scope.data.attributes.hardware.number     = $scope.i2cdevices[$scope.data.hardware_sensorname].number;
            if ($scope.i2cdevices[$scope.data.hardware_sensorname].source == "i2c") {
                $scope.data.attributes.hardware.address    = $scope.i2cdevices[$scope.data.hardware_sensorname].address;
            }
        }

        // Set input to integer
        $scope.data.attributes.values.duration = parseInt($scope.data.attributes.values.duration, 10);
        $scope.data.attributes.values.pitch = parseInt($scope.data.attributes.values.pitch, 10);
        if ($scope.data.attributes.values.pitch < 55) {
            $scope.data.attributes.values.pitch = 55;
        }
        if ($scope.data.attributes.values.pitch >126) {
            $scope.data.attributes.values.pitch = 126;
        }
        $scope.data.attributes.values.delay = parseInt($scope.data.attributes.values.delay, 10);


        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        
                        set_i2c_properties();
                    }
                }
            ]            
        });
    };

    set_i2c_properties = function() {
        //
        // SET I2C PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };


    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_i2c_device_properties();
    };

    get_i2c_device_properties = function() {
        //
        // GET I2C DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                $scope.data.attributes = result.data.value;
                
                // handle hardware endpoint
                if ($scope.data.attributes.endpoint == 1) {
                    let indexy = 0;
                    for (indexy=0; indexy<$scope.devices.length; indexy++) {
                        if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                            $scope.data.hardware_devicename = indexy;
                            break;
                        }
                    }
                    for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                        if ($scope.i2cdevices[indexy].sensorname === $scope.data.attributes.hardware.sensorname) {
                            $scope.data.hardware_sensorname = indexy;
                            break;
                        }
                    }
                    get_all_i2c_sensors($scope.data.attributes.hardware.devicename, $scope.data.attributes.hardware.sensorname);
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };



    // handle hardware endpoint
    get_devices = function() {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            get_all_i2c_sensors($scope.devices[0].devicename);
        });
    };

    // handle hardware endpoint
    $scope.changeDevice = function() {
        var devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
        console.log(devicename);
        $scope.changePeripheral(devicename, null);
    };
    
    $scope.changePeripheral = function(devicename) {
        if (devicename === undefined) {
            devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
            //console.log("changePeripheral " + $scope.data.hardware_devicename);
        }
        
        var peripheral = $scope.peripherals[$scope.data.hardware_peripheral].label;
        //console.log(devicename);
        //console.log(peripheral);
        if (peripheral === "I2C") {
            get_all_sensors(devicename, "i2c", null);
        }
        else if (peripheral === "ADC") {
            get_all_sensors(devicename, "adc", null);
        }
        else if (peripheral === "1WIRE") {
            get_all_sensors(devicename, "1wire", null);
        }
        else if (peripheral === "TPROBE") {
            get_all_sensors(devicename, "tprobe", null);
        }
    };
    
    
    // handle hardware endpoint
    get_all_sensors = function(devicename, peripheral, sensorname) {
        //
        // GET ALL SENSORS
        //
        // - Request:
        //   GET /devices/device/DEVICENAME/i2c/sensors
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'timestamp': string}, ...]}
        //   { 'status': 'NG', 'message': string }
        //
        var url = server + '/devices/device/' + devicename + '/' + peripheral + '/sensors';
        if (peripheral === "i2c") {
            url += "/input";
        }

        $http({
            method: 'GET',
            url: url,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
            
            if (result.data.sensors.length > 0) {
                $scope.i2cdevices = result.data.sensors;
                let indexy = 0;
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    $scope.i2cdevices[indexy].id = indexy;
                }
            }
            else {
                $scope.i2cdevices = $scope.i2cdevices_empty;
            }
            
            // select the correct sensor
            if (sensorname !== null) {
                for (indexy=0; indexy<$scope.i2cdevices.length; indexy++) {
                    if ($scope.i2cdevices[indexy].sensorname === sensorname) {
                        $scope.data.hardware_sensorname = indexy;
                        break;
                    }
                }
            }
            if ($scope.data.hardware_sensorname >= result.data.sensors.length) {
                $scope.data.hardware_sensorname = 0;
            }
        })
        .catch(function (error) {
            handle_error(error);
        }); 
    };
    
    
    
    // VIEW I2C DEVICE
    $scope.viewI2CDevice = function() {
        console.log("viewI2CDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };

    
    $scope.changeEndpoint = function() {
        if ($scope.data.attributes.endpoint === 1) {
            console.log("changeEndpoint");
            // handle hardware endpoint
            get_devices();    
        }
    };
    
    $scope.submitRefresh();
    
}])
   
.controller('potentiometerCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.ranges = [
        { "id":0,  "label": "0-255" },
        { "id":1,  "label": "0-99"  },
        { "id":2,  "label": "0-15"  },
        { "id":3,  "label": "0-9"   },
    ];

    $scope.modes = [
        { "id":0,  "label": "Single Threshold"  },
        { "id":1,  "label": "Dual Threshold"  },
        { "id":2,  "label": "Continuous" },
    ];

    $scope.activates = [
        { "id":0,  "label": "Out of range" },
        { "id":1,  "label": "Within range" },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];    
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'hardware_devicename': $scope.devices[0].id,
        
        'attributes': {
            'range': $scope.ranges[0].id,
            'mode': $scope.modes[0].id,
            'threshold': {
                'value': 0,
                'min': 0,
                'max': 100,
                'activate': $scope.activates[0].id,
            },
            'alert': {
                'type': $scope.alerts[0].id,
                'period': 60000,
            },
            'hardware': {
                'devicename': '',  
            },
            
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
        
        'showNotification': 0,        
    };

    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Potentiometer failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    
    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
        if (i===true) {
            get_devices(false);    
        }    
    };
    
    
    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_devices(true); 
    };

    get_xxx_device_properties = function(peripheral) {
        //
        // GET XXX DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        time_start = Date.now();
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(Date.now()-time_start);
            
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.threshold !== undefined) {
                    $scope.data.attributes = result.data.value;
                    
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    
                    if ($scope.data.attributes.mode != 2) {
                        // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                    }
                    else {
                        // CONTINUOUS mode - use hardware.devicename
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                        $scope.data.attributes.alert.type = 1; // always be continuous
                    }
                }
                else {
                    $scope.data.attributes.notification = result.data.value.notification;
                }
            }
        })
        .catch(function (error) {
            console.log(Date.now()-time_start);
            handle_error(error, true);
        }); 
    };
    
    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        if ($scope.data.attributes.mode!=2) {
            // SINGLE/DUAL THRESHOLD modes
            $scope.data.attributes.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        else {
            // CONTINUOUS mode
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
            $scope.data.attributes.alert.type = 1; // always be continuous
        }


        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        
                        if ($scope.data.source === "I2C") {
                            set_xxx_device_properties("i2c");
                        }
                        else if ($scope.data.source === "ADC") {
                            set_xxx_device_properties("adc");
                        }
                        else if ($scope.data.source === "TPROBE") {
                            set_xxx_device_properties("tprobe");
                        }
                        else if ($scope.data.source === "1WIRE") {
                            set_xxx_device_properties("1wire");
                        }
                    }
                }
            ]            
        });
    };

    set_xxx_device_properties = function(peripheral) {
        //
        // SET XXX DEVICE PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        time_start = Date.now();
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(Date.now()-time_start);
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'I2C device',
                template: $scope.data.sensor.sensorname + ' on I2C ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            console.log(Date.now()-time_start);
            handle_error(error, true);
        }); 
    };

   
    get_devices = function(flag) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
           
            if (flag) {
                if ($scope.data.source === "I2C") {
                    get_xxx_device_properties("i2c");
                }
                else if ($scope.data.source === "ADC") {
                    get_xxx_device_properties("adc");
                }
                else if ($scope.data.source === "TPROBE") {
                    get_xxx_device_properties("tprobe");
                }
                else if ($scope.data.source === "1WIRE") {
                    get_xxx_device_properties("1wire");
                }
            }
        });
    };

    // VIEW I2C DEVICE
    $scope.viewI2CDevice = function() {
        console.log("viewI2CDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeMode = function() {
        console.log("changeMode");
        get_devices(false);    
    };    
    
    $scope.submitRefresh();  
}])
   
.controller('anemometerCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.modes = [
        { "id":0,  "label": "Single Threshold"  },
        { "id":1,  "label": "Dual Threshold"  },
        { "id":2,  "label": "Continuous" },
    ];

    $scope.activates = [
        { "id":0,  "label": "Out of range" },
        { "id":1,  "label": "Within range" },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];    
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'hardware_devicename': $scope.devices[0].id,
        
        'attributes': {
            'mode': $scope.modes[0].id,
            'threshold': {
                'value': 0,
                'min': 0,
                'max': 100,
                'activate': $scope.activates[0].id,
            },
            'alert': {
                'type': $scope.alerts[0].id,
                'period': 60000,
            },
            'hardware': {
                'devicename': '',  
            },
            
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
        
        'showNotification': 0,        
    };

    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Anemometer failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
        if (i===true) {
            get_devices(false);    
        }    
    };
    
    
    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_devices(true);
    };

    get_xxx_device_properties = function(peripheral) {
        //
        // GET XXX DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.threshold !== undefined) {
                    $scope.data.attributes = result.data.value;
                    
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    
                    if ($scope.data.attributes.mode != 2) {
                        // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                    }
                    else {
                        // CONTINUOUS mode - use hardware.devicename
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                        $scope.data.attributes.alert.type = 1; // always be continuous
                    }
                }
                else {
                    $scope.data.attributes.notification = result.data.value.notification;
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    
    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        if ($scope.data.attributes.mode!=2) {
            // SINGLE/DUAL THRESHOLD modes
            $scope.data.attributes.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        else {
            // CONTINUOUS mode
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
            $scope.data.attributes.alert.type = 1; // always be continuous
        }

        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        set_adc_properties();
                    }
                }
            ]            
        });
    };

    set_adc_properties = function() {
        //
        // SET ADC PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'ADC device',
                template: $scope.data.sensor.sensorname + ' on ADC ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

   
    get_devices = function(flag) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            if (flag) {
                if ($scope.data.source === "I2C") {
                    get_xxx_device_properties("i2c");
                }
                else if ($scope.data.source === "ADC") {
                    get_xxx_device_properties("adc");
                }
                else if ($scope.data.source === "TPROBE") {
                    get_xxx_device_properties("tprobe");
                }
                else if ($scope.data.source === "1WIRE") {
                    get_xxx_device_properties("1wire");
                }
            }
        });
    };

    // VIEW ADC DEVICE
    $scope.viewADCDevice = function() {
        console.log("viewADCDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeMode = function() {
        console.log("changeMode");
        get_devices(false);    
    };    
    
    $scope.submitRefresh();  
}])
   
.controller('batteryCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.modes = [
        { "id":0,  "label": "Single Threshold"  },
        { "id":1,  "label": "Dual Threshold"  },
        { "id":2,  "label": "Continuous" },
    ];

    $scope.activates = [
        { "id":0,  "label": "Out of range" },
        { "id":1,  "label": "Within range" },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];    
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'hardware_devicename': $scope.devices[0].id,
        
        'attributes': {
            'mode': $scope.modes[0].id,
            'threshold': {
                'value': 0,
                'min': 0,
                'max': 100,
                'activate': $scope.activates[0].id,
            },
            'alert': {
                'type': $scope.alerts[0].id,
                'period': 60000,
            },
            'hardware': {
                'devicename': '',  
            },
            
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
        
        'showNotification': 0,        
    };

    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Anemometer failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
        if (i===true) {
            get_devices(false);    
        }    
    };
    
    
    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_devices(true);
    };

    get_xxx_device_properties = function(peripheral) {
        //
        // GET XXX DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.threshold !== undefined) {
                    $scope.data.attributes = result.data.value;
                    
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    
                    if ($scope.data.attributes.mode != 2) {
                        // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                    }
                    else {
                        // CONTINUOUS mode - use hardware.devicename
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                        $scope.data.attributes.alert.type = 1; // always be continuous
                    }
                }
                else {
                    $scope.data.attributes.notification = result.data.value.notification;
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    
    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        if ($scope.data.attributes.mode!=2) {
            // SINGLE/DUAL THRESHOLD modes
            $scope.data.attributes.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        else {
            // CONTINUOUS mode
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
            $scope.data.attributes.alert.type = 1; // always be continuous
        }

        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        set_adc_properties();
                    }
                }
            ]            
        });
    };

    set_adc_properties = function() {
        //
        // SET ADC PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'ADC device',
                template: $scope.data.sensor.sensorname + ' on ADC ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

   
    get_devices = function(flag) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            if (flag) {
                if ($scope.data.source === "I2C") {
                    get_xxx_device_properties("i2c");
                }
                else if ($scope.data.source === "ADC") {
                    get_xxx_device_properties("adc");
                }
                else if ($scope.data.source === "TPROBE") {
                    get_xxx_device_properties("tprobe");
                }
                else if ($scope.data.source === "1WIRE") {
                    get_xxx_device_properties("1wire");
                }
            }
        });
    };

    // VIEW ADC DEVICE
    $scope.viewADCDevice = function() {
        console.log("viewADCDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeMode = function() {
        console.log("changeMode");
        get_devices(false);    
    };    
    
    $scope.submitRefresh();  
}])
   
.controller('fluidCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', 'Devices', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token, Devices) {

    var server = Server.rest_api;

    $scope.modes = [
        { "id":0,  "label": "Single Threshold"  },
        { "id":1,  "label": "Dual Threshold"  },
        { "id":2,  "label": "Continuous" },
    ];

    $scope.activates = [
        { "id":0,  "label": "Out of range" },
        { "id":1,  "label": "Within range" },
    ];
    
    $scope.alerts = [
        { "id":0,  "label": "Once"         },
        { "id":1,  "label": "Continuously" },
    ];    
    
    $scope.devices = [ {"id":0, "devicename": ""} ];
    
    $scope.data = {
        'username': User.get_username(),
        'token': User.get_token(),
        'devicename': $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid': $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
        
        'sensor': $stateParams.sensor,
        'source': $stateParams.source,
        
        'hardware_devicename': $scope.devices[0].id,
        
        'attributes': {
            'mode': $scope.modes[0].id,
            'threshold': {
                'value': 0,
                'min': 0,
                'max': 100,
                'activate': $scope.activates[0].id,
            },
            'alert': {
                'type': $scope.alerts[0].id,
                'period': 60000,
            },
            'hardware': {
                'devicename': '',  
            },
            
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
        
        'showNotification': 0,        
    };

    handle_error = function(error, showerror) {
        if (error.data !== null) {
            console.log("ERROR: Anemometer failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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


    $scope.changeNotification = function(i) {
        $scope.data.showNotification = i;
        if (i===true) {
            get_devices(false);    
        }    
    };
    
    
    $scope.submitRefresh = function() {
        console.log("submitRefresh");
        console.log($scope.data.attributes);
        get_devices(true);
    };

    get_xxx_device_properties = function(peripheral) {
        //
        // GET XXX DEVICE PROPERTIES
        //
        // - Request:
        //   GET /devices/device/<devicename>/<peripheral>/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'GET',
            url: server + '/devices/device/' + $scope.data.devicename + '/' + peripheral + '/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access },
        })
        .then(function (result) {
            console.log(result.data);
            if (result.data.value !== undefined) {
                if (result.data.value.threshold !== undefined) {
                    $scope.data.attributes = result.data.value;
                    
                    $scope.data.hardware_devicename = 0;
                    let indexy = 0;
                    
                    if ($scope.data.attributes.mode != 2) {
                        // SINGLE/DUAL THRESHOLD modes - use notification.endpoints.modem.recipients
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.notification.endpoints.modem.recipients) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                    }
                    else {
                        // CONTINUOUS mode - use hardware.devicename
                        for (indexy=0; indexy<$scope.devices.length; indexy++) {
                            if ($scope.devices[indexy].devicename === $scope.data.attributes.hardware.devicename) {
                                $scope.data.hardware_devicename = indexy;
                                break;
                            }
                        }
                        $scope.data.attributes.alert.type = 1; // always be continuous
                    }
                }
                else {
                    $scope.data.attributes.notification = result.data.value.notification;
                }
            }
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };
    
    
    $scope.submit = function() {
        console.log("submit");
        console.log($scope.data.attributes);
        
        if ($scope.data.attributes.mode!=2) {
            // SINGLE/DUAL THRESHOLD modes
            $scope.data.attributes.notification.endpoints.modem.recipients = $scope.devices[$scope.data.hardware_devicename].devicename;
        }
        else {
            // CONTINUOUS mode
            $scope.data.attributes.hardware.devicename = $scope.devices[$scope.data.hardware_devicename].devicename;
            $scope.data.attributes.alert.type = 1; // always be continuous
        }

        // Add prompt when setting properties
        $ionicPopup.alert({ title: 'Set Properties', template: 'Are you sure you want to set this properties?',
            buttons: [
                { text: 'No', type: 'button-assertive', },
                { text: 'Yes', type: 'button-positive',
                    onTap: function(e) {
                        set_adc_properties();
                    }
                }
            ]            
        });
    };

    set_adc_properties = function() {
        //
        // SET ADC PROPERTIES
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/<number>/sensors/sensor/<sensorname>/properties
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: 
        //   { 
        //      'endpoint': int,
        //      'color': int,
        //      'brightness': int,
        //      'timeout': int,
        //      'hardware': { 'devicename': string, 'sensorname': string }
        //   }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }        
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.sensor.number.toString() + '/sensors/sensor/' + $scope.data.sensor.sensorname + '/properties',
            headers: { 'Authorization': 'Bearer ' + $scope.data.token.access, 'Content-Type': 'application/json' },
            data: $scope.data.attributes
        })
        .then(function (result) {
            console.log(result.data);
            //set_gpio_voltage();
            $ionicPopup.alert({
                title: 'ADC device',
                template: $scope.data.sensor.sensorname + ' on ADC ' + $scope.data.sensor.number.toString() + ' was configured successfully!',
            });            
        })
        .catch(function (error) {
            handle_error(error, true);
        }); 
    };

   
    get_devices = function(flag) {
        
        param = {
            'username': $scope.data.username,
            'token': $scope.data.token     
        };
        
        // Fetch devices
        Devices.fetch(param, "").then(function(res) {
            $scope.devices = res;
            
            let indexy = 0;
            for (indexy=0; indexy<$scope.devices.length; indexy++) {
                $scope.devices[indexy].id = indexy;
            }
            
            console.log($scope.devices);
            $scope.data.token = User.get_token();
            
            if (flag) {
                if ($scope.data.source === "I2C") {
                    get_xxx_device_properties("i2c");
                }
                else if ($scope.data.source === "ADC") {
                    get_xxx_device_properties("adc");
                }
                else if ($scope.data.source === "TPROBE") {
                    get_xxx_device_properties("tprobe");
                }
                else if ($scope.data.source === "1WIRE") {
                    get_xxx_device_properties("1wire");
                }
            }
        });
    };

    // VIEW ADC DEVICE
    $scope.viewADCDevice = function() {
        console.log("viewADCDevice");
        var device_param = {
            'username': $scope.data.username,
            'token': $scope.data.token,
            'devicename': $scope.data.devicename,
            'devicestatus': $scope.data.devicestatus,
            'deviceid': $scope.data.deviceid,
            'serialnumber': $scope.data.serialnumber,
            'sensor': $scope.data.sensor,
            'source': $scope.data.source,
        };
        if ($scope.data.source === "I2C") {
            console.log("viewI2CDevice");
            $state.go('viewI2CDevice', device_param);
        }
        else if ($scope.data.source === "ADC") {
            console.log("viewADCDevice");
            $state.go('viewADCDevice', device_param);
        }
        else if ($scope.data.source === "TPROBE") {
            console.log("viewTPROBEDevice");
            $state.go('viewTPROBEDevice', device_param);
        }
        else if ($scope.data.source === "1WIRE") {
            console.log("view1WIREDevice");
            $state.go('view1WIREDevice', device_param);
        }
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
        
        if ($scope.data.sensor.subclass !== undefined) {
            device_param.sensor = $scope.data.sensor;
            device_param.source = $scope.data.source;
            device_param.multiclass = $scope.data.multiclass;
            $state.go('multiclass', device_param);
        }
        else {
            if ($scope.data.source === "I2C") {
               $state.go('deviceI2C', device_param);
            }
            else if ($scope.data.source === "ADC") {
               $state.go('deviceADC', device_param);
            }
            else if ($scope.data.source === "TPROBE") {
               $state.go('deviceTPROBE', device_param);
            }
            else if ($scope.data.source === "1WIRE") {
               $state.go('device1WIRE', device_param);
            }
        }
    };
    
    $scope.changeMode = function() {
        console.log("changeMode");
        get_devices(false);    
    };    
    
    $scope.submitRefresh();  
}])
   
.controller('addI2CDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.manufacturers = [
        { "id":0,  "name": "Adafruit" },
        { "id":1,  "name": "Sparkfun" },
        { "id":2,  "name": "Electronic Dollar Store" },
    ];

    $scope.devicetypes = [
        { "id":0,  "type": "input" },
        { "id":1,  "type": "output" }
    ];

    $scope.devicemodels_ada = [{ "id":0,  "model": "N/A" }];
    $scope.devicemodels_spf = [{ "id":0,  "model": "N/A" }];
    $scope.devicemodels_eds = [
        { 
            "id":0,  
            "model": "BEEP", 
            "name": "Piezoelectric Beeper", 
            "desc": "Beeps a MIDI tone",
            "link": "https://electricdollarstore.com/beep.html",
            "class": "speaker",
            "type": "output",
            "units": [],
            "formats": [],
            "addresses": { "default": 0x30, "max": 0x36 },
            "attributes": [],
        },
        {   
            "id":1,  
            "model": "DIG2", 
            "name": "Digit Display",        
            "desc": "2-digit seven segment display",  
            "link": "https://electricdollarstore.com/dig2.html",
            "class": "display",
            "type": "output",
            "units": [],
            "formats": [],
            "addresses": { "default": 0x14, "max": 0x1A },
            "attributes": [],
        },
        { 
            "id":2,  
            "model": "LED",  
            "name": "RGB LED",
            "desc": "LED brightness control capable",  
            "link": "https://electricdollarstore.com/led.html",
            "class": "light",
            "type": "output",
            "units": [],
            "formats": [],
            "addresses": { "default": 0x08, "max": 0x0F },
            "attributes": [],
        },
        { 
            "id":3,  
            "model": "POT",  
            "name": "Potentiometer",
            "desc": "Input range device",  
            "link": "https://electricdollarstore.com/pot.html",
            "class": "potentiometer",
            "type": "input",
            "units": [""],
            "formats": ["int"],
            "addresses": { "default": 0x28, "max": 0x2F },
            "attributes": ["Range"],
        },
        {   
            "id":4,  
            "model": "TEMP", 
            "name": "Temperature Sensor",   
            "desc": "Input thresholded device",   
            "link": "https://electricdollarstore.com/temp.html",
            "class": "temperature",
            "type": "input",
            "units": ["C"],
            "formats": ["float"],
            "addresses": { "default": 0x48, "max": 0x4F },
            "attributes": ["Temperature"],
        },
    ];
    $scope.devicemodels = $scope.devicemodels_eds;
 
 
    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
     
        'i2cnumber'   : $stateParams.i2cnumber,
        'i2c': {
            'manufacturerid'     : $scope.manufacturers[2].id,
            'devicemodelid'      : $scope.devicemodels[0].id,

            'manufacturer' : $scope.manufacturers[2].name,
            'model'        : $scope.devicemodels[0].model,
            'name'  : $scope.devicemodels[0].name,
            'desc'  : $scope.devicemodels[0].desc,
            'link'  : $scope.devicemodels[0].link,
            'class' : $scope.devicemodels[0].class,
            'type'  : $scope.devicetypes[0].type,
            'units' : $scope.devicetypes[0].units,
            'formats' : $scope.devicetypes[0].formats,
            "addresses": $scope.devicetypes[0].addresses,
            'attributes' : $scope.devicemodels[0].attributes,
        }
    };


    $scope.submitAdd = function() {
        console.log("submitAdd");
        
        if ($scope.data.i2c.manufacturerid != 2) {
            $ionicPopup.alert({ title: 'Error', template: 'Selected choice is invalid!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }
        
        $scope.data.i2c.manufacturer = $scope.manufacturers[$scope.data.i2c.manufacturerid].name;
        $scope.data.i2c.model        = $scope.devicemodels[$scope.data.i2c.devicemodelid].model;
        $scope.data.i2c.name         = $scope.devicemodels[$scope.data.i2c.devicemodelid].name;
        $scope.data.i2c.desc         = $scope.devicemodels[$scope.data.i2c.devicemodelid].desc;
        $scope.data.i2c.link         = $scope.devicemodels[$scope.data.i2c.devicemodelid].link;
        $scope.data.i2c.class        = $scope.devicemodels[$scope.data.i2c.devicemodelid].class;
        $scope.data.i2c.type         = $scope.devicemodels[$scope.data.i2c.devicemodelid].type;
        $scope.data.i2c.units        = $scope.devicemodels[$scope.data.i2c.devicemodelid].units;
        $scope.data.i2c.formats      = $scope.devicemodels[$scope.data.i2c.devicemodelid].formats;
        $scope.data.i2c.addresses    = $scope.devicemodels[$scope.data.i2c.devicemodelid].addresses;
        $scope.data.i2c.attributes   = $scope.devicemodels[$scope.data.i2c.devicemodelid].attributes;
        
        $state.go('addI2CDeviceDetails', $scope.data);        
    };
    
    

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    

    // GET SUPPORTED I2C DEVICES
    $scope.getSupportedI2CDevices = function() {
        console.log("getSupportedI2CDevices");
        get_supported_i2c_devices();
    };

    get_supported_i2c_devices = function() {
        //
        // GET SUPPORTED I2C DEVICES
        //
        // - Request:
        //   GET /others/i2cdevices
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'document': json_object }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/others/i2cdevices',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
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
    
    $scope.getSupportedI2CDevices();
}])
   
.controller('addADCDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.manufacturers = [
        { "id":0,  "name": "China PLC Center" },
        { "id":1,  "name": "Bridgetek" },
        { "id":2,  "name": "Milone Technologies" },
    ];

    $scope.devicetypes = [
        { "id":0,  "type": "input" },
        { "id":1,  "type": "output" }
    ];

    $scope.devicemodels_chn = [
        { 
            "id":0,  
            "model": "QS-FS Wind sensor", 
            "name": "ADC Anemometer", 
            "desc": "Measures wind speed",
            "link": "https://lollette.com/support/pdf/Sensor/QS-FS-en.pdf",
            "class": "anemometer",
            "type": "input",
            "units": ["m/s"],
            "formats": ["float"],
            "attributes": ["Wind Speed"],
        },
        { 
            "id":1,  
            "model": "ADC Potentiometer", 
            "name": "ADC Potentiometer", 
            "desc": "Input range device",
            "link": "Unknown",
            "class": "potentiometer",
            "type": "input",
            "units": [""],
            "formats": ["int"],
            "attributes": ["Range"],
        }
    ];
    $scope.devicemodels_brt = [
        { 
            "id":0,  
            "model": "Battery sensor",
            "name":  "ADC Battery Level sensor",
            "desc":  "Measure battery level",
            "link":  "N/A",
            "class": "battery",
            "type":  "input",
            "units": ["mV"],
            "formats": ["float"],
            "attributes": ["Battery Level"],
        }
    ];
    $scope.devicemodels_mil = [
        { 
            "id":0,  
            "model": "eTape Fluid sensor",
            "name":  "ADC Fluid Level sensor",
            "desc":  "Measure fluid level",
            "link":  "https://cdn-shop.adafruit.com/datasheets/eTape+Datasheet+12110215TC-12_040213.pdf",
            "class": "fluid",
            "type":  "input",
            "units": ["ml"],
            "formats": ["float"],
            "attributes": ["Fluid Level"]
        }
    ];
    $scope.devicemodels = $scope.devicemodels_chn;
 
 
    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
     
        'adcnumber'   : $stateParams.adcnumber,
        'adc': {
            'manufacturerid'     : $scope.manufacturers[0].id,
            'devicemodelid'      : $scope.devicemodels[0].id,

            'manufacturer' : $scope.manufacturers[0].name,
            'model'        : $scope.devicemodels[0].model,
            'name'  : $scope.devicemodels[0].name,
            'desc'  : $scope.devicemodels[0].desc,
            'link'  : $scope.devicemodels[0].link,
            'class' : $scope.devicemodels[0].class,
            'type'  : $scope.devicetypes[0].type,
            'units' : $scope.devicemodels[0].units,
            'formats' : $scope.devicemodels[0].formats,
            'attributes' : $scope.devicemodels[0].attributes,
        }
    };


    $scope.submitAdd = function() {
        console.log("submitAdd");
        
        $scope.data.adc.manufacturer = $scope.manufacturers[$scope.data.adc.manufacturerid].name;
        if ($scope.data.adc.manufacturerid === 0) {
            $scope.devicemodels = $scope.devicemodels_chn;
        }
        else if ($scope.data.adc.manufacturerid === 1) {
            $scope.devicemodels = $scope.devicemodels_brt;
        }
        else if ($scope.data.adc.manufacturerid === 2) {
            $scope.devicemodels = $scope.devicemodels_mil;
        }

        $scope.data.adc.model        = $scope.devicemodels[$scope.data.adc.devicemodelid].model;
        $scope.data.adc.name         = $scope.devicemodels[$scope.data.adc.devicemodelid].name;
        $scope.data.adc.desc         = $scope.devicemodels[$scope.data.adc.devicemodelid].desc;
        $scope.data.adc.link         = $scope.devicemodels[$scope.data.adc.devicemodelid].link;
        $scope.data.adc.class        = $scope.devicemodels[$scope.data.adc.devicemodelid].class;
        $scope.data.adc.type         = $scope.devicemodels[$scope.data.adc.devicemodelid].type;
        $scope.data.adc.units        = $scope.devicemodels[$scope.data.adc.devicemodelid].units;
        $scope.data.adc.formats      = $scope.devicemodels[$scope.data.adc.devicemodelid].formats;
        $scope.data.adc.attributes   = $scope.devicemodels[$scope.data.adc.devicemodelid].attributes;
        
        $state.go('addADCDeviceDetails', $scope.data);        
    };
    
    

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    

    // GET SUPPORTED ADC DEVICES
    $scope.getSupportedADCDevices = function() {
        console.log("getSupportedADCDevices");
        get_supported_adc_devices();
    };

    get_supported_adc_devices = function() {
        //
        // GET SUPPORTED ADC DEVICES
        //
        // - Request:
        //   GET /others/adcdevices
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'document': json_object }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/others/adcdevices',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
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
        $state.go('deviceADC', device_param);
    };
    
    $scope.getSupportedADCDevices();
}])
   
.controller('addTPROBEDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.manufacturers = [
        { "id":0,  "name": "ITEAD Studio" },
    ];

    $scope.devicetypes = [
        { "id":0,  "type": "input" },
        { "id":1,  "type": "output" }
    ];

    $scope.devicemodels_its = [
        { 
            "id":0,  
            "model": "SONOFF TH16", 
            "name": "Temperature and Humidity", 
            "desc": "Wi-Fi Smart Switch",
            "link": "https://sonoff.tech/product/wifi-diy-smart-switches/th10-th16",
            "class": "temperature",
            "type": "input",
            "units": ["C", "%"],
            "formats": ["float", "float"],
            "attributes": ["Temperature"],
            "subclass": "humidity",
            "subattributes": ["Humidity"],
        }
    ];
    $scope.devicemodels = $scope.devicemodels_its;
 
 
    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
     
        'tprobenumber'   : $stateParams.tprobenumber,
        'tprobe': {
            'manufacturerid'     : $scope.manufacturers[0].id,
            'devicemodelid'      : $scope.devicemodels[0].id,

            'manufacturer' : $scope.manufacturers[0].name,
            'model'        : $scope.devicemodels[0].model,
            'name'  : $scope.devicemodels[0].name,
            'desc'  : $scope.devicemodels[0].desc,
            'link'  : $scope.devicemodels[0].link,
            'class' : $scope.devicemodels[0].class,
            'type'  : $scope.devicetypes[0].type,
            'units' : $scope.devicemodels[0].units,
            'formats' : $scope.devicemodels[0].formats,
            'attributes' : $scope.devicemodels[0].attributes,
        }
    };


    $scope.submitAdd = function() {
        console.log("submitAdd");
        
        $scope.data.tprobe.manufacturer = $scope.manufacturers[$scope.data.tprobe.manufacturerid].name;
        $scope.data.tprobe.model        = $scope.devicemodels[$scope.data.tprobe.devicemodelid].model;
        $scope.data.tprobe.name         = $scope.devicemodels[$scope.data.tprobe.devicemodelid].name;
        $scope.data.tprobe.desc         = $scope.devicemodels[$scope.data.tprobe.devicemodelid].desc;
        $scope.data.tprobe.link         = $scope.devicemodels[$scope.data.tprobe.devicemodelid].link;
        $scope.data.tprobe.class        = $scope.devicemodels[$scope.data.tprobe.devicemodelid].class;
        $scope.data.tprobe.type         = $scope.devicemodels[$scope.data.tprobe.devicemodelid].type;
        $scope.data.tprobe.units        = $scope.devicemodels[$scope.data.tprobe.devicemodelid].units;
        $scope.data.tprobe.formats      = $scope.devicemodels[$scope.data.tprobe.devicemodelid].formats;
        $scope.data.tprobe.attributes   = $scope.devicemodels[$scope.data.tprobe.devicemodelid].attributes;

        // handle multiclass
        if ($scope.devicemodels[$scope.data.tprobe.devicemodelid].subclass !== undefined) {
            $scope.data.tprobe.subclass = $scope.devicemodels[$scope.data.tprobe.devicemodelid].subclass;
        }
        else {
            $scope.data.tprobe.subclass = "None";
        }
        if ($scope.devicemodels[$scope.data.tprobe.devicemodelid].subattributes !== undefined) {
            $scope.data.tprobe.subattributes= $scope.devicemodels[$scope.data.tprobe.devicemodelid].subattributes;
        }
        else {
            $scope.data.tprobe.subattributes = [];
        }
        
        $state.go('addTPROBEDeviceDetails', $scope.data);        
    };
    
    

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    

    // GET SUPPORTED TPROBE DEVICES
    $scope.getSupportedTPROBEDevices = function() {
        console.log("getSupportedTPROBEDevices");
        get_supported_tprobe_devices();
    };

    get_supported_tprobe_devices = function() {
        //
        // GET SUPPORTED TPROBE DEVICES
        //
        // - Request:
        //   GET /others/tprobedevices
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'document': json_object }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/others/tprobedevices',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
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
        $state.go('deviceTPROBE', device_param);
    };
    
    $scope.getSupportedTPROBEDevices();
}])
   
.controller('add1WIREDeviceCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Token) {

    var server = Server.rest_api;

    $scope.manufacturers = [
        { "id":0,  "name": "Maxim Integrated" },
    ];

    $scope.devicetypes = [
        { "id":0,  "type": "input" },
        { "id":1,  "type": "output" }
    ];

    $scope.devicemodels_mxi = [
        { 
            "id":0,  
            "model": "DS18B20", 
            "name": "Programmable Resolution 1-Wire Digital Thermometer", 
            "desc": "Direct-to digital temperature sensor",
            "link": "https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf",
            "class": "temperature",
            "type": "input",
            "units": ["C"],
            "formats": ["float"],
            "attributes": ["Temperature"],
        }
    ];
    $scope.devicemodels = $scope.devicemodels_mxi;
 
 
    $scope.data = {
        'username'    : User.get_username(),
        'token'       : User.get_token(),
        'devicename'  : $stateParams.devicename,
        'devicestatus': $stateParams.devicestatus,
        'deviceid'    : $stateParams.deviceid,
        'serialnumber': $stateParams.serialnumber,
     
        'onewirenumber'   : $stateParams.onewirenumber,
        'onewire': {
            'manufacturerid'     : $scope.manufacturers[0].id,
            'devicemodelid'      : $scope.devicemodels[0].id,

            'manufacturer' : $scope.manufacturers[0].name,
            'model'        : $scope.devicemodels[0].model,
            'name'  : $scope.devicemodels[0].name,
            'desc'  : $scope.devicemodels[0].desc,
            'link'  : $scope.devicemodels[0].link,
            'type'  : $scope.devicetypes[0].type,
            'class' : $scope.devicemodels[0].class,
            'units' : $scope.devicemodels[0].units,
            'formats' : $scope.devicemodels[0].formats,
            'attributes' : $scope.devicemodels[0].attributes,
        }
    };


    $scope.submitAdd = function() {
        console.log("submitAdd");
        
        $scope.data.onewire.manufacturer = $scope.manufacturers[$scope.data.onewire.manufacturerid].name;
        $scope.data.onewire.model        = $scope.devicemodels[$scope.data.onewire.devicemodelid].model;
        $scope.data.onewire.name         = $scope.devicemodels[$scope.data.onewire.devicemodelid].name;
        $scope.data.onewire.desc         = $scope.devicemodels[$scope.data.onewire.devicemodelid].desc;
        $scope.data.onewire.link         = $scope.devicemodels[$scope.data.onewire.devicemodelid].link;
        $scope.data.onewire.class        = $scope.devicemodels[$scope.data.onewire.devicemodelid].class;
        $scope.data.onewire.type         = $scope.devicemodels[$scope.data.onewire.devicemodelid].type;
        $scope.data.onewire.units        = $scope.devicemodels[$scope.data.onewire.devicemodelid].units;
        $scope.data.onewire.formats      = $scope.devicemodels[$scope.data.onewire.devicemodelid].formats;
        $scope.data.onewire.attributes   = $scope.devicemodels[$scope.data.onewire.devicemodelid].attributes;
        
        $state.go('add1WIREDeviceDetails', $scope.data);        
    };
    
    

    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

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
    

    // GET SUPPORTED 1WIRE DEVICES
    $scope.getSupported1WIREDevices = function() {
        console.log("getSupported1WIREDevices");
        get_supported_1wire_devices();
    };

    get_supported_1wire_devices = function() {
        //
        // GET SUPPORTED 1WIRE DEVICES
        //
        // - Request:
        //   GET /others/1wiredevices
        //   headers: { 'Authorization': 'Bearer ' + token.access }
        //
        // - Response:
        //   { 'status': 'OK', 'message': string, 'document': json_object }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'GET',
            url: server + '/others/1wiredevices',
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access}
        })
        .then(function (result) {
            console.log(result.data);
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
        $state.go('device1WIRE', device_param);
    };
    
    $scope.getSupported1WIREDevices();
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
     
        'i2cnumber'   : $stateParams.i2cnumber,
        'i2c'         : $stateParams.i2c,
        
        'sensorname' : $stateParams.i2c.model + ' 1',
        'sensor' : {
            'manufacturer': $stateParams.i2c.manufacturer,
            'model': $stateParams.i2c.model,
            'address': $stateParams.i2c.addresses.default,

            'class': $stateParams.i2c.class,
            'type': $stateParams.i2c.type,
            'units': $stateParams.i2c.units,
            'formats': $stateParams.i2c.formats,
            'addresses': $stateParams.i2c.addresses,
            'attributes': $stateParams.i2c.attributes,
            //'name': $stateParams.i2c.name,
            //'desc': $stateParams.i2c.desc,
            //'link': $stateParams.i2c.link,
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
            else if (error.status == 409 || error.status == 400) {
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
        
        console.log($scope.data.sensor.class);
        console.log($scope.data.sensor.type);
        console.log($scope.data.sensor.units);
        console.log($scope.data.sensor.formats);
        console.log($scope.data.sensor.attributes);
        
        // Address must be within the address range
        if ($scope.data.sensor.address > $scope.data.sensor.addresses.max ||
            $scope.data.sensor.address < $scope.data.sensor.addresses.default) {
            let template = "Invalid address. Address must be within the address range.";
            $ionicPopup.alert({ title: 'Error', template: template, buttons: [{text: 'OK', type: 'button-assertive'}] });
            return;
        }
        //console.log($scope.data.sensor.name);
        //console.log($scope.data.sensor.desc);
        //console.log($scope.data.sensor.link);


        sensor_param = $scope.data.sensor;
        add_i2c_sensor(sensor_param);
    };
    
    add_i2c_sensor = function(sensor_param) {
        //
        // ADD I2C SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/i2c/<number>/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'address': int, 'manufacturer': string, 'model': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/i2c/' + $scope.data.i2cnumber.toString() + '/sensors/sensor/' + $scope.data.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
            data: sensor_param
        })
        .then(function (result) {
            console.log(result.data);
            
            template = 'Sensor added successfully to I2C ' + $scope.data.i2cnumber.toString() + '!';
            $ionicPopup.alert({ title: 'Success', template: template,
                buttons: [{ text: 'OK', type: 'button-positive',
                    onTap: function(e) {
                        $state.go(
                            'deviceI2C', {
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
   
.controller('addADCDeviceDetailsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
     
        'adcnumber'   : $stateParams.adcnumber,
        'adc'         : $stateParams.adc,
        
        'sensorname' : $stateParams.adc.model + ' 1',
        'sensor' : {
            'manufacturer': $stateParams.adc.manufacturer,
            'model': $stateParams.adc.model,

            'class': $stateParams.adc.class,
            'type': $stateParams.adc.type,
            'units': $stateParams.adc.units,
            'formats': $stateParams.adc.formats,
            'attributes': $stateParams.adc.attributes,
            //'name': $stateParams.adc.name,
            //'desc': $stateParams.adc.desc,
            //'link': $stateParams.adc.link,
        }
    };


    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Add ADC Device Details failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status == 409 || error.status == 400) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };


    // ADD ADC SENSOR
    $scope.addADCSensor = function() {
        
        if ($scope.data.sensorname === undefined) {
            console.log("ERROR: Add ADC Sensor name is empty!");
            alert("ERROR: Add ADC Sensor name is empty!");
            return;
        }        
        else if ($scope.data.sensorname.length === 0) {
            console.log("ERROR: Add ADC Sensor name is empty!");
            alert("ERROR: Add ADC Sensor name is empty!");
            return;
        }

        console.log("addADCSensor");
        
        console.log($scope.data.sensorname);
        console.log($scope.data.sensor.manufacturer);
        console.log($scope.data.sensor.model);

        console.log($scope.data.sensor.class);
        console.log($scope.data.sensor.type);
        console.log($scope.data.sensor.units);
        console.log($scope.data.sensor.formats);
        console.log($scope.data.sensor.attributes);
        //console.log($scope.data.sensor.name);
        //console.log($scope.data.sensor.desc);
        //console.log($scope.data.sensor.link);


        sensor_param = $scope.data.sensor;
        add_adc_sensor(sensor_param);
    };
    
    add_adc_sensor = function(sensor_param) {
        //
        // ADD ADC SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/adc/<number>/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'manufacturer': string, 'model': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/adc/' + $scope.data.adcnumber.toString() + '/sensors/sensor/' + $scope.data.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
            data: sensor_param
        })
        .then(function (result) {
            console.log(result.data);
            
            template = 'Sensor added successfully to ADC ' + $scope.data.adcnumber.toString() + '!';
            $ionicPopup.alert({ title: 'Success', template: template,
                buttons: [{ text: 'OK', type: 'button-positive',
                    onTap: function(e) {
                        $state.go(
                            'deviceADC', {
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
        $state.go('deviceADC', device_param);
    };    
}])
   
.controller('addTPROBEDeviceDetailsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
     
        'tprobenumber'   : $stateParams.tprobenumber,
        'tprobe'         : $stateParams.tprobe,
        
        'sensorname' : $stateParams.tprobe.model + ' 1',
        'sensor' : {
            'manufacturer': $stateParams.tprobe.manufacturer,
            'model': $stateParams.tprobe.model,

            'class': $stateParams.tprobe.class,
            'type': $stateParams.tprobe.type,
            'units': $stateParams.tprobe.units,
            'formats': $stateParams.tprobe.formats,
            'attributes': $stateParams.tprobe.attributes,
            
            'subclass': $stateParams.tprobe.subclass,
            'subattributes': $stateParams.tprobe.subattributes,
            
            //'name': $stateParams.tprobe.name,
            //'desc': $stateParams.tprobe.desc,
            //'link': $stateParams.tprobe.link,
        }
    };


    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Add TPROBE Device Details failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status == 409 || error.status == 400) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };


    // ADD TPROBE SENSOR
    $scope.addTPROBESensor = function() {
        
        if ($scope.data.sensorname === undefined) {
            console.log("ERROR: Add TPROBE Sensor name is empty!");
            alert("ERROR: Add TPROBE Sensor name is empty!");
            return;
        }        
        else if ($scope.data.sensorname.length === 0) {
            console.log("ERROR: Add TPROBE Sensor name is empty!");
            alert("ERROR: Add TPROBE Sensor name is empty!");
            return;
        }

        console.log("addTPROBESensor");
        
        console.log($scope.data.sensorname);
        console.log($scope.data.sensor.manufacturer);
        console.log($scope.data.sensor.model);

        console.log($scope.data.sensor.class);
        console.log($scope.data.sensor.type);
        console.log($scope.data.sensor.units);
        console.log($scope.data.sensor.formats);
        console.log($scope.data.sensor.attributes);
        
        // handle multiclass
        if ($scope.data.sensor.subclass !== undefined) {
            console.log($scope.data.sensor.subclass);
        }
        if ($scope.data.sensor.subattributes !== undefined) {
            console.log($scope.data.sensor.subattributes);
        }

        sensor_param = $scope.data.sensor;
        add_tprobe_sensor(sensor_param);
    };
    
    add_tprobe_sensor = function(sensor_param) {
        //
        // ADD TPROBE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/tprobe/<number>/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'manufacturer': string, 'model': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/tprobe/' + $scope.data.tprobenumber.toString() + '/sensors/sensor/' + $scope.data.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
            data: sensor_param
        })
        .then(function (result) {
            console.log(result.data);
            
            //template = 'Sensor added successfully to TPROBE ' + $scope.data.tprobenumber.toString() + '!';
            template = 'Sensor added successfully to TPROBE!';
            $ionicPopup.alert({ title: 'Success', template: template,
                buttons: [{ text: 'OK', type: 'button-positive',
                    onTap: function(e) {
                        $state.go(
                            'deviceTPROBE', {
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
        $state.go('deviceTPROBE', device_param);
    };    
}])
   
.controller('add1WIREDeviceDetailsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Token', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
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
     
        'onewirenumber'   : $stateParams.onewirenumber,
        'onewire'         : $stateParams.onewire,
        
        'sensorname' : $stateParams.onewire.model + ' 1',
        'sensor' : {
            'manufacturer': $stateParams.onewire.manufacturer,
            'model': $stateParams.onewire.model,

            'class': $stateParams.onewire.class,
            'type': $stateParams.onewire.type,
            'units': $stateParams.onewire.units,
            'formats': $stateParams.onewire.formats,
            'attributes': $stateParams.onewire.attributes,
            //'name': $stateParams.onewire.name,
            //'desc': $stateParams.onewire.desc,
            //'link': $stateParams.onewire.link,
        }
    };


    handle_error = function(error) {
        if (error.data !== null) {
            console.log("ERROR: Add 1WIRE Device Details failed with " + error.status + " " + error.statusText + "! " + error.data.message); 

            if (error.data.message === "Token expired") {
                Token.refresh({'username': $scope.data.username, 'token': $scope.data.token});
                $scope.data.token = User.get_token();
            }
            
            if (error.status == 503) {
                $ionicPopup.alert({ title: 'Error', template: 'Device is unreachable!', buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
            else if (error.status == 409 || error.status == 400) {
                $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
            }
        }
        else {
            console.log("ERROR: Server is down!"); 
            $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
        }
    };


    // ADD 1WIRE SENSOR
    $scope.add1WIRESensor = function() {
        
        if ($scope.data.sensorname === undefined) {
            console.log("ERROR: Add 1WIRE Sensor name is empty!");
            alert("ERROR: Add 1WIRE Sensor name is empty!");
            return;
        }        
        else if ($scope.data.sensorname.length === 0) {
            console.log("ERROR: Add 1WIRE Sensor name is empty!");
            alert("ERROR: Add 1WIRE Sensor name is empty!");
            return;
        }

        console.log("add1WIRESensor");
        
        console.log($scope.data.sensorname);
        console.log($scope.data.sensor.manufacturer);
        console.log($scope.data.sensor.model);

        console.log($scope.data.sensor.class);
        console.log($scope.data.sensor.type);
        console.log($scope.data.sensor.units);
        console.log($scope.data.sensor.formats);
        console.log($scope.data.sensor.attributes);
        //console.log($scope.data.sensor.name);
        //console.log($scope.data.sensor.desc);
        //console.log($scope.data.sensor.link);


        sensor_param = $scope.data.sensor;
        add_1wire_sensor(sensor_param);
    };
    
    add_1wire_sensor = function(sensor_param) {
        //
        // ADD 1WIRE SENSOR
        //
        // - Request:
        //   POST /devices/device/<devicename>/1wire/<number>/sensors/sensor/<sensorname>
        //   headers: { 'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json' }
        //   data: {'manufacturer': string, 'model': string}
        //
        // - Response:
        //   { 'status': 'OK', 'message': string }
        //   { 'status': 'NG', 'message': string }
        //
        $http({
            method: 'POST',
            url: server + '/devices/device/' + $scope.data.devicename + '/1wire/' + $scope.data.onewirenumber.toString() + '/sensors/sensor/' + $scope.data.sensorname,
            headers: {'Authorization': 'Bearer ' + $scope.data.token.access},
            data: sensor_param
        })
        .then(function (result) {
            console.log(result.data);
            
            //template = 'Sensor added successfully to 1WIRE ' + $scope.data.onewirenumber.toString() + '!';
            template = 'Sensor added successfully to 1WIRE!';
            $ionicPopup.alert({ title: 'Success', template: template,
                buttons: [{ text: 'OK', type: 'button-positive',
                    onTap: function(e) {
                        $state.go(
                            'device1WIRE', {
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
        $state.go('device1WIRE', device_param);
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
        
        'status': $stateParams.status,
        
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
 

        if ($scope.data.status !== 'Online') {
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
            
            'status': $scope.data.status,
        };
        $state.go('configureDevice', device_param);
    };
    
}])
   
.controller('troubleshootingCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Devices', 'Histories', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Devices, Histories) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    };
    
    $scope.hide_settings = false;
    
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
    
        // status
        "get_status", 
        "set_status",

        // settings
        "get_settings", 
        "set_settings",
        
        // uart
        "get_uarts",
        "get_uart_prop",
        "set_uart_prop",
        "enable_uart",

        // gpio
        "get_gpios",
        "get_gpio_prop",
        "set_gpio_prop",
        "enable_gpio",
        "get_gpio_voltage",
        "set_gpio_voltage",

        // i2c
        "get_i2c_devs",
        "enable_i2c_dev",
        "get_i2c_dev_prop",
        "set_i2c_dev_prop",

        // adc
        "get_adc_devs",
        "enable_adc_dev",
        "get_adc_dev_prop",
        "set_adc_dev_prop",
        "get_adc_voltage",
        "set_adc_voltage",

        // 1wire
        "get_1wire_devs",
        "enable_1wire_dev",
        "get_1wire_dev_prop",
        "set_1wire_dev_prop",

        // tprobe
        "get_tprobe_devs",
        "enable_tprobe_dev",
        "get_tprobe_dev_prop",
        "set_tprobe_dev_prop",
        
        // notification
        "get_devs",
        
        // notification
        "recv_notification",
        "trigger_notification",
        "status_notification",
        
        // sensor reading
        "rcv_sensor_reading",
        "req_sensor_reading",
        "sensor_reading",

        // configuration
        "rcv_configuration",
        "req_configuration",
        "del_configuration",
        "set_configuration"
        
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
    
        Devices.fetch($scope.data, "").then(function(res) {
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
   
.controller('alertsCtrl', ['$scope', '$stateParams', '$state', '$http', '$ionicPopup', 'Server', 'User', 'Devices', 'Notifications', // The following is the constructor function for this page's controller. See https://docs.angularjs.org/guide/controller
// You can include any angular dependencies as parameters for this function
// TIP: Access Route Parameters for your page via $stateParams.parameterName
function ($scope, $stateParams, $state, $http, $ionicPopup, Server, User, Devices, Notifications) {

    var server = Server.rest_api;
    
    $scope.data = {
        'username': User.get_username(), //$stateParams.username,
        'token': User.get_token()        //$stateParams.token
    };
    
    $scope.hide_settings = false;
    
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
    
    // Filter by types
    $scope.types = [ 
        "All types",
        "Mobile", 
        "Email",
        "Notification",
        "Modem",
        "Storage"
    ];
    $scope.type = "All types";

    // Filter by peripherals
    $scope.peripherals = [ 
        "All peripherals",
        "UART", 
        "GPIO1",
        "GPIO2",
        "GPIO3",
        "GPIO4",
        "I2C1",
        "I2C2",
        "I2C3",
        "I2C4",
        "ADC1",
        "ADC2",
        "1WIRE1",
        "TPROBE1"
    ];
    $scope.peripheral = "All peripherals";

    // Filter by date    
    $scope.date = {
        'begin': "",
        'end': ""
    };
    
    
    
    $scope.applyFilter = function(deviceidx, type, peripheral) {

        var devicename = null;
        var deviceid = null;
        var datebegin = 0;
        var dateend = 0;
        
        console.log(type);
        
        if (deviceidx) {
            devicename = $scope.devices[deviceidx];
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

        //console.log(devicename);
        //console.log(type);
        //console.log(peripheral);
        //console.log(datebegin);
        //console.log(dateend);


        var type_use = null;
        if (type !== "All types") {
            type_use = type;
        }
        var source_use = null;
        if (peripheral !== "All peripherals") {
            source_use = peripheral;
        }
        Notifications.fetch_filtered($scope.data, devicename, type_use, source_use, datebegin, dateend).then(function(res) {
            $scope.items = res;
            $scope.data.token = User.get_token();
        }); 
    };
    
    
    $scope.submitRefresh = function() {
    
        Devices.fetch($scope.data, "").then(function(res) {
            var i;
            for (i=0; i<res.length; i++) {
                var result = $scope.devices.includes(res[i].devicename);
                if (result === false) {
                    $scope.devices.push(res[i].devicename);
                }
            }
            $scope.data.token = User.get_token();
        });
    
        Notifications.fetch($scope.data).then(function(res) {
            $scope.items = res;
            $scope.data.token = User.get_token();
        }); 
    };
    
    $scope.$on('$ionicView.enter', function(e) {
        console.log("DEVICES enter ionicView REFRESH LIST");
        $scope.submitRefresh();
    });    
}])
 