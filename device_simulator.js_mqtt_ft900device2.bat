set DEVICE_ID="047975f752b51b6e99413ef69bd6dadc0ece8ede"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device2_cert.pem"
set DEVICE_PKEY="cert/ft900device2_pkey.pem"

set HOST="localhost"
set USER="guest"
set PASS="guest"

node device_simulator.js --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause