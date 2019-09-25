/* !!! IMPORTANT: Rename "mymodule" below and add your module to Angular Modules above. */

angular.module('server', [])

.service('Server', [function(){

    //////////////////////////////////////////////////////////////////////////////////////////////
    // TODO: UPDATE ME!!!
    // This should point to the MACHINE ADDRESS, not the NGINX DOCKER ADDRESS (172.18.0.6)
    // When using locally, https://192.168.99.100:443 will work!
    // When using EC2, should contain the public IP address!
    // When not using docker, this should point to the Flask REST API address
    //////////////////////////////////////////////////////////////////////////////////////////////
    var rest_api = 'https://192.168.99.100';

    console.log(rest_api);
    var result = { 'rest_api': rest_api }
    return result;
}]);

