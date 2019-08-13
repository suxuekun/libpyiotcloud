/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('histories', [])

.service('Histories', ['$http', 'Server', function($http, Server){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {        
            // Send HTTP request to REST API
            return $http({
                method: 'POST',
                url: server + '/user/histories',
                headers: {'Content-Type': 'application/json'},
                data: userdata //$scope.data
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
