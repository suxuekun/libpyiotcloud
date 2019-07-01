set DEVICE_ID="c2bfb6ec02f4bb0cb146fe4b2c7752a90d02f79d"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device1_cert.pem"
set DEVICE_PKEY="cert/ft900device1_pkey.pem"

set HOST="localhost"
set USER="guest"
set PASS="guest"

node device_simulator.js --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause