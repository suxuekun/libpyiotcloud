/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('histories', [])

.service('Histories', ['$http', 'Server', 'User', 'Token', function($http, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {        
            //
            // GET DEVICE TRANSACTION HISTORIES
            //
            // - Request:
            //   GET /devices/histories
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   { 'status': 'OK', 'message': string, 
            //     'histories': array[
            //       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
            //   { 'status': 'NG', 'message': string}
            //            
            return $http({
                method: 'GET',
                url: server + '/devices/histories',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                // Handle successful login
                console.log(result.data);
                return result.data.histories;
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
        }
    };
    
    return ret;
}]);
