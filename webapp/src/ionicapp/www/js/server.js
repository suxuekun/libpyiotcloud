/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('server', [])

.service('Server', [function(){

    //////////////////////////////////////////////////////////////////////////////////////////////
    // TODO: UPDATE ME!!! This should point to the Flask REST API service
    // When using on AWS EC2 docker, use https://richmondu.com or the EC2 public IP address
    // When using locally on docker, use https://192.168.99.100:443
    // When using locally on Windows, use https://localhost:443
    //////////////////////////////////////////////////////////////////////////////////////////////
    var rest_api = 'https://richmondu.com';

    console.log(rest_api);
    var result = { 'rest_api': rest_api }
    return result;
}]);

