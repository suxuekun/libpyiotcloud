/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('histories', [])

.service('Histories', ['$http', 'Server', 'User', function($http, Server, User){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {        
            //
            // GET DEVICE TRANSACTION HISTORIES
            //
            // - Request:
            //   POST /user/histories
            //   { 'username': string, 'token': {'access': string, 'id': string, 'refresh': string} }
            //
            // - Response:
            //   { 'status': 'OK', 'message': string, 
            //     'histories': array[
            //       {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
            //   { 'status': 'NG', 'message': string}
            //            
            return $http({
                method: 'POST',
                url: server + '/user/histories',
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
