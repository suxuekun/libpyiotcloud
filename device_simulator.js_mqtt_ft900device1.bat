set DEVICE_NAME="ft900device1"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device1_cert.pem"
set DEVICE_PKEY="cert/ft900device1_pkey.pem"

node device_simulator.js --USE_DEVICE_NAME %DEVICE_NAME% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY%
pause