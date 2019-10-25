/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('devices', [])

.service('Devices', ['$http', 'Server', 'User', function($http, Server, User){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {        
            // Send HTTP request to REST API
            return $http({
                method: 'POST',
                url: server + '/devices',
                headers: {'Content-Type': 'application/json'},
                data: userdata //$scope.data
            })
            .then(function (result) {
                // Handle successful login
                console.log(result.data);
                
                if (result !== null) {
                    if (result.data.new_token !== undefined) {
                        console.log("New Token exists!")
                        User.set({
                            'username': userdata.username,
                            'token': result.data.new_token
                        });
                    }
                }    
                
                return result.data.devices;
            })
            .catch(function (error) {
                // Handle failed login
                if (error.data !== null) {
                    console.log("ERROR: Login failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    // TODO: replace alert with ionic alert
                    //alert("ERROR: Login failed with " + error.status + " " + error.statusText +"! " + error.data.message); 
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
