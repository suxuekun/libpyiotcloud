/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('devices', [])

.service('Devices', ['$http', '$ionicPopup', 'Server', 'User', 'Token', function($http, $ionicPopup, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata, filter) {
            
            filter_string = filter.trim();
            if (filter_string.length > 0) {
                //
                // GET DEVICES FILTERED
                //
                // - Request:
                //   GET /devices/filter/FILTERSTRING
                //   headers: {'Authorization': 'Bearer ' + token.access}
                //
                // - Response:
                //   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, ...}, ...]}
                //   {'status': 'NG', 'message': string}
                //
                return $http({
                    method: 'GET',
                    url: server + '/devices/filter/' + filter_string,
                    headers: {'Authorization': 'Bearer ' + userdata.token.access}
                })
                .then(function (result) {
                    // Handle successful login
                    console.log(result.data);
                    return result.data.devices;
                })
                .catch(function (error) {
                    // Handle failed login
                    if (error.data !== null) {
                        console.log("ERROR: Get Devices failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                        
                        if (error.data.message === "Token expired") {
                            Token.refresh(userdata);
                            $ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }
                    }
                    else {
                        console.log("ERROR: Server is down!"); 
                        $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    
                    return [];
                });
                
            }
            else {
                //
                // GET DEVICES
                //
                // - Request:
                //   GET /devices
                //   headers: {'Authorization': 'Bearer ' + token.access}
                //
                // - Response:
                //   {'status': 'OK', 'message': string, 'devices': array[{'devicename': string, 'deviceid': string, ...}, ...]}
                //   {'status': 'NG', 'message': string}
                //
                return $http({
                    method: 'GET',
                    url: server + '/devices',
                    headers: {'Authorization': 'Bearer ' + userdata.token.access}
                })
                .then(function (result) {
                    // Handle successful login
                    console.log(result.data);
                    return result.data.devices;
                })
                .catch(function (error) {
                    // Handle failed login
                    if (error.data !== null) {
                        console.log("ERROR: Get Devices failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                        
                        if (error.data.message === "Token expired") {
                            Token.refresh(userdata);
                            $ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }
                    }
                    else {
                        console.log("ERROR: Server is down!"); 
                        $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    
                    return [];
                });
            }
        }
    }
    
    return ret;
}]);
