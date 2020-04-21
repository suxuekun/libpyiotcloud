angular.module('organizations', [])

.service('Organizations', ['$http', '$ionicPopup', 'Server', 'User', 'Token', function($http, $ionicPopup, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        get: function(userdata) {
            return $http({
                method: 'GET',
                url: server + '/user/organization',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get organization failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },


        //////////////////////////////////////////////////////////////


        create: function(userdata, orgname) {
            return $http({
                method: 'POST',
                url: server + '/organizations/organization/' + orgname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Create organization failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },
        
        delete: function(userdata, orgname) {
            return $http({
                method: 'DELETE',
                url: server + '/organizations/organization/' + orgname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Delete organization failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },
        
    
        //////////////////////////////////////////////////////////////


        create_invitation: function(userdata, orgname, email_list, cancel=0) {
            var data = {'emails': email_list};
            if (cancel === 1) {
                data.cancel = 1;
            }
            return $http({
                method: 'POST',
                url: server + '/organizations/organization/' + orgname + '/invitation',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: data
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Create invitation failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },    


        update_membership: function(userdata, orgname, email_list, remove=0) {
            var data = {'emails': email_list};
            if (remove === 1) {
                data.remove = 1;
            }
            return $http({
                method: 'POST',
                url: server + '/organizations/organization/' + orgname + '/membership',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: data
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Update membership failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },    

        //////////////////////////////////////////////////////////////
    

        accept_invitation: function(userdata) {
            return $http({
                method: 'POST',
                url: server + '/user/organization/invitation',
                headers: {'Authorization': 'Bearer ' + userdata.token.access}
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Accept invitation failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },    

        decline_invitation: function(userdata) {
            return $http({
                method: 'DELETE',
                url: server + '/user/organization/invitation',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Decline invitation failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },

        leave: function(userdata) {
            return $http({
                method: 'DELETE',
                url: server + '/user/organization',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Leave organization failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },
        
        
        //////////////////////////////////////////////////////////////


        get_groups: function(userdata, orgname) {
            return $http({
                method: 'GET',
                url: server + '/organizations/organization/' + orgname + '/groups',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get organizations failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },

        create_group: function(userdata, orgname, groupname) {
            return $http({
                method: 'POST',
                url: server + '/organizations/organization/' + orgname + '/groups/group/' + groupname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Create organization group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },

        delete_group: function(userdata, orgname, groupname) {
            return $http({
                method: 'DELETE',
                url: server + '/organizations/organization/' + orgname + '/groups/group/' + groupname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Delete organization group failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },


        //////////////////////////////////////////////////////////////
        
        
        get_group_members: function(userdata, orgname, groupname) {
            console.log("get_group_members " + orgname + " " + groupname);
            return $http({
                method: 'GET',
                url: server + '/organizations/organization/' + orgname + '/groups/group/' + groupname + "/members",
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get organization group members failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },
        
        
        add_group_member: function(userdata, orgname, groupname, membername) {
            return $http({
                method: 'POST',
                url: server + '/organizations/organization/' + orgname + '/groups/group/' + groupname + '/members/member/' + membername,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Add organization group member failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },
        
        update_group_members: function(userdata, orgname, groupname, members) {
            return $http({
                method: 'POST',
                url: server + '/organizations/organization/' + orgname + '/groups/group/' + groupname + '/members',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: {'members': members}
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Add organization group member failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
                    if (error.data.message === "Token expired") {
                        Token.refresh(userdata);
                        //$ionicPopup.alert({ title: 'Error', template: 'Token expired!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                    }
                }
                else {
                    console.log("ERROR: Server is down!"); 
                    $ionicPopup.alert({ title: 'Error', template: 'Server is down!', buttons: [{text: 'OK', type: 'button-assertive'}] });
                }
                
                return error.data;
            });
        },
        
    };
    
    return ret;
}]);