set DEVICE_ID="31a71e7c8877173123219dcc87c37db813954c1e"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device1_cert.pem"
set DEVICE_PKEY="cert/ft900device1_pkey.pem"

set HOST="ec2-54-85-32-68.compute-1.amazonaws.com"

python.exe device_simulator.py --USE_AMQP 1 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause