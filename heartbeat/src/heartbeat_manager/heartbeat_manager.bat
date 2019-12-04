set DEVICE_ID="heartbeat_manager"
set DEVICE_CA="../cert_ecc/rootca.pem"
set DEVICE_CERT="../cert_ecc/heartbeat_manager_cert.pem"
set DEVICE_PKEY="../cert_ecc/heartbeat_manager_pkey.pem"

set HOST="localhost"
set DBHOST="localhost"

python.exe heartbeat_manager.py --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_DBHOST %DBHOST%
pause
