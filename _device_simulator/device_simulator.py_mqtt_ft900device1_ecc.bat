set DEVICE_ID="4eea8ff26c09cf68cdf237cef80004f3c0b16866"
set DEVICE_CA="cert_ecc/rootca.pem"
set DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
set DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"

set HOST="richmondu.com"
::set HOST="192.168.99.100"

python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST%
pause
