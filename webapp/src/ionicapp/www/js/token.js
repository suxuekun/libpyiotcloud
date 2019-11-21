/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('token', [])

.service('Token', ['$http', 'Server', 'User', function($http, Server, User){

    var server = Server.rest_api;

    var ret = {
        update: function(userdata, result) {
            if (result !== null) {
                if (result.data.new_token !== undefined) {
                    console.log("New Token exists!");
                    User.set({
                        'username': userdata.username,
                        'token': result.data.new_token
                    });
                }
            }
            return null;
        },
    
        refresh: function(userdata) {
            //
            // REFRESH TOKEN
            //
            // - Request:
            //   POST /user/token
            //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
            //   data: { 'token': {'refresh': string, 'id: string'} }
            //
            // - Response:
            //   {'status': 'OK', 'message': string, 'token' : {'access': string, 'refresh': string, 'id: string'} }
            //   {'status': 'NG', 'message': string}
            //   
            $http({
                method: 'POST',
                url: server + '/user/token',
                headers: {'Authorization': 'Bearer ' + userdata.token.access, 'Content-Type': 'application/json'},
                data: {'token': {'refresh': userdata.token.refresh, 'id': userdata.token.id} }
            })
            .then(function (result) {
                // Handle successful login
                console.log(result.data);
                ret.update(userdata, result);
            })
            .catch(function (error) {
                // Handle failed login
                if (error.data !== null) {
                    console.log("ERROR: Refresh Token failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                }
                else {
                    console.log("ERROR: Server is down!"); 
                }
            }); 
        },
    }
    
    return ret;
}]);