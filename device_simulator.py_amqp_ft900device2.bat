set DEVICE_ID="b92ac493b92eb996e53fcd534ab261bec7518e60"
::set DEVICE_ID="bf9bd22361e66e2fef8e93de01652e22c400e6a7"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device2_cert.pem"
set DEVICE_PKEY="cert/ft900device2_pkey.pem"

set HOST="localhost"
set USER="guest"
set PASS="guest"

python.exe device_simulator.py --USE_AMQP 1 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause