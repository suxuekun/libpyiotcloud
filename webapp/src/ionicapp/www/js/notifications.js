/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('notifications', [])

.service('Notifications', ['$http', 'Server', 'User', 'Token', function($http, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata) {
            
            console.log(userdata);
            
            //
            // GET MENOS HISTORIES
            //
            // - Request:
            //   GET /devices/menos
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
                url: server + '/devices/menos',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                // Handle successful login
                console.log(result.data);
                
                for (var indexy=0; indexy<result.data.transactions.length; indexy++) {
                    let timestamp = new Date(result.data.transactions[indexy].timestamp * 1000); 
                    result.data.transactions[indexy].timestamp = "" + timestamp;
                }
                
                return result.data.transactions;
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
        
        fetch_filtered: function(userdata, devicename, type, datebegin, dateend) {

            var filter = {};
            if (devicename !== null) {
                filter.devicename = devicename;
            }
            if (type !== null) {
                filter.type = type;
            }
            if (datebegin !== null) {
                filter.datebegin = datebegin;
                if (dateend !== null) {
                    filter.dateend = dateend;
                }
            }

            //
            // GET MENOS HISTORIES FILTERED
            //
            // - Request:
            //   POST /devices/menos
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
                url: server + '/devices/menos',
                headers: {'Authorization': 'Bearer ' + userdata.token.access, 'Content-Type': 'application/json'},
                data: filter
            })
            .then(function (result) {
                // Handle successful login
                console.log(result.data);
                
                for (var indexy=0; indexy<result.data.transactions.length; indexy++) {
                    let timestamp = new Date(result.data.transactions[indexy].timestamp * 1000); 
                    result.data.transactions[indexy].timestamp = "" + timestamp;
                }
                
                return result.data.transactions;
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
