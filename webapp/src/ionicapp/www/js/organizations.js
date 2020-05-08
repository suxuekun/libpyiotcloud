angular.module('organizations', [])

.service('Organizations', ['$http', '$ionicPopup', 'Server', 'User', 'Token', function($http, $ionicPopup, Server, User, Token){
    
    var server = Server.rest_api;

    var ret = {

        //////////////////////////////////////////////////////////////
        // GET ORGANIZATIONS
        // SET ACTIVE ORGANIZATION
        // GET ORGANIZATION
        // ACCEPT INVITATION
        // DECLINE INVITATION
        // LEAVE ORGANIZATION
        //////////////////////////////////////////////////////////////

        // GET ORGANIZATIONS
        get_all: function(userdata) {
            return $http({
                method: 'GET',
                url: server + '/user/organizations',
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
        
        // SET ACTIVE ORGANIZATION
        set_active: function(userdata, orgname, orgid) {
            return $http({
                method: 'POST',
                url: server + '/user/organizations',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: {'orgname': orgname, 'orgid': orgid}
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Set active organization failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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
        
        // GET ORGANIZATION
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

        // ACCEPT INVITATION
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

        // DECLINE INVITATION
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

        // LEAVE ORGANIZATION
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


        create: function(userdata, orgname) {
            console.log(orgname);
            return $http({
                method: 'POST',
                url: server + '/organization',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: {'orgname': orgname}
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
        
        delete: function(userdata) {
            return $http({
                method: 'DELETE',
                url: server + '/organization',
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


        create_invitation: function(userdata, email_list, cancel=0) {
            var data = {'emails': email_list};
            if (cancel === 1) {
                data.cancel = 1;
            }
            return $http({
                method: 'POST',
                url: server + '/organization/invitation',
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


        update_membership: function(userdata, email_list, remove=0) {
            var data = {'emails': email_list};
            if (remove === 1) {
                data.remove = 1;
            }
            return $http({
                method: 'POST',
                url: server + '/organization/membership',
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
        // GROUPS
        //////////////////////////////////////////////////////////////

        get_groups: function(userdata) {
            return $http({
                method: 'GET',
                url: server + '/organization/groups',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get organization groups failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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

        create_group: function(userdata, groupname) {
            return $http({
                method: 'POST',
                url: server + '/organization/groups/group/' + groupname,
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

        delete_group: function(userdata, groupname) {
            return $http({
                method: 'DELETE',
                url: server + '/organization/groups/group/' + groupname,
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
        
        
        get_group_members: function(userdata, groupname) {
            console.log("get_group_members " + groupname);
            return $http({
                method: 'GET',
                url: server + '/organization/groups/group/' + groupname + "/members",
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
        
        add_group_member: function(userdata, groupname, membername) {
            return $http({
                method: 'POST',
                url: server + '/organization/groups/group/' + groupname + '/members/member/' + membername,
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
        
        update_group_members: function(userdata, groupname, members) {
            return $http({
                method: 'POST',
                url: server + '/organization/groups/group/' + groupname + '/members',
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


        //////////////////////////////////////////////////////////////
        // POLICIES
        //////////////////////////////////////////////////////////////

        get_policies: function(userdata) {
            return $http({
                method: 'GET',
                url: server + '/organization/policies',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get organization policies failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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
        
        create_policy: function(userdata, policyname) {
            return $http({
                method: 'POST',
                url: server + '/organization/policies/policy/' + policyname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Create organization policy failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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

        delete_policy: function(userdata, policyname) {
            return $http({
                method: 'DELETE',
                url: server + '/organization/policies/policy/' + policyname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Delete organization policy failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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


        get_group_policies: function(userdata, groupname) {
            console.log("get_group_policies " + groupname);
            return $http({
                method: 'GET',
                url: server + '/organization/groups/group/' + groupname + "/policies",
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Get organization group policies failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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
        
        add_group_policy: function(userdata, groupname, policyname) {
            return $http({
                method: 'POST',
                url: server + '/organization/groups/group/' + groupname + '/policies/policy/' + policyname,
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Add organization group policy failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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
        
        update_group_policies: function(userdata, groupname, policies) {
            return $http({
                method: 'POST',
                url: server + '/organization/groups/group/' + groupname + '/policies',
                headers: {'Authorization': 'Bearer ' + userdata.token.access},
                data: {'policies': policies}
            })
            .then(function (result) {
                console.log(result.data);
                return result.data;
            })
            .catch(function (error) {
                if (error.data !== null) {
                    console.log("ERROR: Add organization group policy failed with " + error.status + " " + error.statusText + "! " + error.data.message); 
                    
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