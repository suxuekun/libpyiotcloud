Notes for PRODUCTION:


Production:

0. Set the environment variables

1. Update webapp\src\ionicapp\www\js\server.js 
   - use richmondu.com instead of 192.168.99.100

2. Update nginx\src\nginx.conf 
   - use cert_prod folder instead of cert_test
   - update cert_prod/cert.pem
   - update cert_prod/pkey.pem
   - cert.pem and pkey.pem must be signed by trusted certificates bought from GoDaddy.com or etc
     cert.pem and pkey.pem are usually linked to a specific domain (iotportal.brtchip.com)


Dev Testing On Docker Toolbox:

0. Set the environment variables

1. Update webapp\src\ionicapp\www\js\server.js 
   - use 192.168.99.100 instead of richmondu.com

2. Update nginx\src\nginx.conf 
   - use cert_test folder instead of cert_prod


Dev Testing On Windows

0. Set the environment variables

1. Update webapp\src\ionicapp\www\js\server.js 
   - use localhost instead of richmondu.com

2. Update nginx\src\nginx.conf 
   - use cert_test folder instead of cert_prod


