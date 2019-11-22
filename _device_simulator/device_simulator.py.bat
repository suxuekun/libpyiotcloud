set DEVICE_ID="PH80XXRR112219EF"
set DEVICE_CA="cert_ecc/rootca.pem"
set DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
set DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"


set HOST="richmondu.com"
::set HOST="localhost"
::set HOST="192.168.99.100"

set PORT="8883"
::set PORT="30883"

set USER=""
set PASS=""


python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_PORT %PORT% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause
