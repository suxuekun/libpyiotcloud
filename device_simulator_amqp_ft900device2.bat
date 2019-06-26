set DEVICE_NAME="ft900device2"
set DEVICE_CERT="cert/ft900device2_cert.pem"
set DEVICE_PKEY="cert/ft900device2_pkey.pem"

python.exe device_simulator.py --USE_AMQP 1 --USE_DEVICE_NAME %DEVICE_NAME% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY%