/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('user', [])

.service('User', [function(){
    
    var ret = {
        set: function(user_data) {
            window.localStorage.setItem("user_data", JSON.stringify(user_data));
        },

        clear: function() {
            window.localStorage.setItem("user_data", JSON.stringify({"username": "", "token": "", "name": ""}));
        },

        get_username: function() {
            return JSON.parse(window.localStorage.getItem("user_data")).username;
        },

        get_token: function() {
            return JSON.parse(window.localStorage.getItem("user_data")).token;
        },

        get_name: function() {
            return JSON.parse(window.localStorage.getItem("user_data")).name;
        },
        get_auth_header:function(){
            var token = this.get_token()
            return {'Authorization': 'Bearer ' + token.access}
        },
    };

    return ret;
}]);