set DEVICE_ID="48ce3d08c604ffae7e9f8c66d3142cd7395e5ce4"
set DEVICE_CA="cert_ecc/rootca.pem"
set DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
set DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"

set HOST="richmondu.com"
::set HOST="3.89.74.84"
::set HOST="ec2-3-89-74-84.compute-1.amazonaws.com"

python.exe device_simulator.py --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause