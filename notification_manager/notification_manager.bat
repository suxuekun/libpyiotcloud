set DEVICE_ID="notification_manager"
set DEVICE_CA="../cert/rootca.pem"
set DEVICE_CERT="../cert/notification_manager_cert.pem"
set DEVICE_PKEY="../cert/notification_manager_pkey.pem"

set HOST="localhost"

python.exe notification_manager.py --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause
