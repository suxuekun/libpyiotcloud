///////////////////////////////////////////////////////////////////////////////////
// TODO: UPDATE ME!!! This should point to the Flask REST API service
// When using on AWS EC2 docker, use richmondu.com:443 or the EC2 public IP address
// When using locally on docker, use 192.168.99.100:443
// When using locally on Windows, use localhost:443
///////////////////////////////////////////////////////////////////////////////////

(function (window) {
    window.__env = window.__env || {};
    window.__env.apiUrl = 'richmondu.com';
}(this));
