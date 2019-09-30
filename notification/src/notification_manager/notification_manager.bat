set DEVICE_ID="notification_manager"
set DEVICE_CA="../cert_ecc/rootca.pem"
set DEVICE_CERT="../cert_ecc/notification_manager_cert.pem"
set DEVICE_PKEY="../cert_ecc/notification_manager_pkey.pem"

set HOST="192.168.100.5"

python.exe notification_manager.py --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause
