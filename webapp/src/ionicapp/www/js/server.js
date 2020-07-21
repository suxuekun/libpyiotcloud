/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('server', [])

.service('Server', [function(){

    //////////////////////////////////////////////////////////////////////////////////////////////
    // Note: Update env.js
    //////////////////////////////////////////////////////////////////////////////////////////////
    var rest_api = 'http://' + window.__env.apiUrl + ":8000" ;
    // var rest_api = 'https://' + window.__env.apiUrl ;
    console.log(rest_api);

    var result = { 'rest_api': rest_api };
    return result;
}]);
