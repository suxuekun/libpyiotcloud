/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('histories', [])

.service('Histories', ['$http', 'Server', 'User', 'Token', function($http, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {
            
            console.log(userdata);
            
            //
            // GET HISTORIES
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
        },
        
        fetch_filtered: function(userdata, devicename, direction, topic, datebegin, dateend) {

            var filter = {};
            if (devicename !== null) {
                filter.devicename = devicename;
            }
            if (direction !== null) {
                filter.direction = direction;
            }
            if (topic !== null) {
                filter.topic = topic;
            }
            if (datebegin !== null) {
                filter.datebegin = datebegin;
                if (dateend !== null) {
                    filter.dateend = dateend;
                }
            }

            //
            // GET HISTORIES FILTERED
            //
            // - Request:
            //   POST /devices/histories
            //   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
            //   data: { 'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 
            //           'datebegin': int, 'dateend': int }
            //
            // - Response:
            //   { 'status': 'OK', 'message': string, 
            //     'histories': array[
            //       {'devicename': string, 'deviceid': string, 
            //        'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
            //   { 'status': 'NG', 'message': string}
            //            
            return $http({
                method: 'POST',
                url: server + '/devices/histories',
                headers: {'Authorization': 'Bearer ' + userdata.token.access, 'Content-Type': 'application/json'},
                data: filter
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
