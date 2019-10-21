/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('user', [])

.service('User', [function(){
    
    var ret = {
        set: function(user_data) {
            //console.log("set " + user_data.username);
            window.localStorage.user_data = JSON.stringify(user_data);  
            //console.log("get " + JSON.parse(window.localStorage.user_data).username);
        },
        
        clear: function() {
            window.localStorage.user_data = JSON.stringify({"username": "", "token": ""});  
        },
        
        get_username: function() {
            return JSON.parse(window.localStorage.user_data).username;
        },

        get_token: function() {
            return JSON.parse(window.localStorage.user_data).token;
        }
    }
    
    ret.clear();
    
    return ret;
}]);