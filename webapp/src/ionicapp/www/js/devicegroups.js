/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('devicegroups', [])

.service('DeviceGroups', ['$http', '$ionicPopup', 'Server', 'User', 'Token', function($http, $ionicPopup, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        fetch: function(userdata, filter) {

/*            
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
                    console.log(result.data);
                    return result.data.devices;
                })
                .catch(function (error) {
                    if (error.data !== null) {
                        console.log("ERROR: Get Devices failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                        
                        if (error.data.message === "Token expired") {
                            Token.refresh(userdata);
                            //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }
                    }
                    else {
                        console.log("ERROR: Server is down!"); 
                        $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    
                    return [];
                });
                
            }
            else */
            {
                //
                // GET DEVICE GROUPS
                //
                // - Request:
                //   GET /devicegroups
                //   headers: {'Authorization': 'Bearer ' + token.access}
                //
                // - Response:
                //   {'status': 'OK', 'message': string, 'devicegroups': array[{'groupname': string, 'devices': ['devicename': string, ...], ...}, ...]}
                //   {'status': 'NG', 'message': string}
                //
                return $http({
                    method: 'GET',
                    url: server + '/devicegroups',
                    headers: {'Authorization': 'Bearer ' + userdata.token.access}
                })
                .then(function (result) {
                    console.log(result.data);
                    return result.data.devicegroups;
                })
                .catch(function (error) {
                    if (error.data !== null) {
                        console.log("ERROR: Get Device Groups failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                        
                        if (error.data.message === "Token expired") {
                            Token.refresh(userdata);
                            //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }
                        else if (error.status == 401 && error.data.message.includes('Please check with the organization owner') === true ) {
                            $ionicPopup.alert({ title: 'Error', template: error.data.message, buttons: [{text: 'OK', type: 'button-assertive'}] });
                        }         
                        
                    }
                    else {
                        console.log("ERROR: Server is down!"); 
                        $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                    
                    return [];
                });
            }
        },
        
        get: function(userdata, groupname) {

            //
            // GET DEVICE GROUP
            //
            // - Request:
            //   GET /devicegroups/GROUPNAME
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'GET',
                url: server + '/devicegroups/group/' + groupname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        get_detailed: function(userdata, groupname) {

            //
            // GET DEVICE GROUP DETAILED
            //
            // - Request:
            //   GET /devicegroups/GROUPNAME/devices
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'GET',
                url: server + '/devicegroups/group/' + groupname + '/devices',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        get_ungrouped_devices: function(userdata) {

            //
            // GET UNGROUPED DEVICES
            //
            // - Request:
            //   GET /devicegroups/ungrouped
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'GET',
                url: server + '/devicegroups/ungrouped',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result.data.devices;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        get_mixed_devices: function(userdata) {

            //
            // GET MIXED DEVICES
            //
            // - Request:
            //   GET /devicegroups/mixed
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'GET',
                url: server + '/devicegroups/mixed',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result.data.devices;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get Mixed devices failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        add: function(userdata, groupname, devices) {

            //
            // ADD DEVICE GROUP
            //
            // - Request:
            //   POST /devicegroups/GROUPNAME
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //   data: {'devices': []}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'POST',
                url: server + '/devicegroups/group/' + groupname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: {'devices': devices}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Add Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        delete: function(userdata, groupname) {

            //
            // DELETE DEVICE GROUP
            //
            // - Request:
            //   DELETE /devicegroups/GROUPNAME
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'DELETE',
                url: server + '/devicegroups/group/' + groupname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Delete Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        add_device: function(userdata, groupname, devicename) {

            //
            // ADD DEVICE TO DEVICE GROUP
            //
            // - Request:
            //   POST /devicegroups/GROUPNAME/device/DEVICENAME
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'POST',
                url: server + '/devicegroups/group/' + groupname + "/device/" + devicename,
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Add Device to Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        remove_device: function(userdata, groupname, devicename) {

            //
            // REMOVE DEVICE FROM DEVICE GROUP
            //
            // - Request:
            //   DELETE /devicegroups/GROUPNAME/device/DEVICENAME
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'DELETE',
                url: server + '/devicegroups/group/' + groupname + "/device/" + devicename,
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Remove Device from Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },

        set_devices: function(userdata, groupname, devices) {

            //
            // SET DEVICES TO DEVICE GROUP
            //
            // - Request:
            //   POST /devicegroups/GROUPNAME/devices
            //   headers: {'Authorization': 'Bearer ' + token.access}
            //   data: {'devices': ['devicenames']}
            //
            // - Response:
            //   {'status': 'OK', 'message': string}
            //   {'status': 'NG', 'message': string}
            //
            return $http({
                method: 'POST',
                url: server + '/devicegroups/group/' + groupname + "/devices",
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: {'devices': devices}
            })
            .then(function (result) {
                console.log(result.data);
                return result;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Set Devices to Device Group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error;
            });
        },
        
    };
    
    return ret;
}]);
