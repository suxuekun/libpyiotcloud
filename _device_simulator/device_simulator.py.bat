:::::::::::::::::::::::::::
:: Device credentials
:::::::::::::::::::::::::::
set DEVICE_ID=""
set DEVICE_SERIAL=""
set DEVICE_MACADD=""
set DEVICE_SECRETKEY=""
::NO NEED TO SPECIFY USERNAME AND PASSWORD NO. Application will generate based on DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD
::set USER=""
::set PASS=""


:::::::::::::::::::::::::::
:: Device certificates
:::::::::::::::::::::::::::
set DEVICE_CA="cert_ecc/rootca.pem"
set DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
set DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"


:::::::::::::::::::::::::::
:: Backend message broker
:::::::::::::::::::::::::::
set PORT="8883"
set HOST="ec2-54-88-41-145.compute-1.amazonaws.com"
::set HOST="localhost"
::set HOST="richmondu.com"
::set HOST="192.168.99.100"
::set PORT="30883"


python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_PORT %PORT% --USE_DEVICE_SERIAL %DEVICE_SERIAL% --USE_DEVICE_MACADD %DEVICE_MACADD% --USE_DEVICE_SECRETKEY %DEVICE_SECRETKEY% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause
