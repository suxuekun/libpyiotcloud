set DEVICE_ID="e2da8fffa35f8a470af3675e11a48966f2d6ddf6"
set DEVICE_CA="../cert/rootca.pem"
set DEVICE_CERT="../cert/ft900device1_cert.pem"
set DEVICE_PKEY="../cert/ft900device1_pkey.pem"

set HOST="192.168.99.100"

node device_simulator.js --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause