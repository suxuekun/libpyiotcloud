/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('devices', [])

.service('Devices', ['$http', 'Server', 'User', 'Token', function($http, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {
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
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    // TODO: replace alert with ionic alert
                    //alert("ERROR: Server is down!");
                }
                
                return [];
            });
        }
    }
    
    return ret;
}]);
