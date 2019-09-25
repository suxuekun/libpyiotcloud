set DEVICE_ID="48ce3d08c604ffae7e9f8c66d3142cd7395e5ce4"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device2_cert.pem"
set DEVICE_PKEY="cert/ft900device2_pkey.pem"

set HOST="richmondu.com"
::set HOST="192.168.99.100"

python.exe device_simulator.py --USE_ECC 0 --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause