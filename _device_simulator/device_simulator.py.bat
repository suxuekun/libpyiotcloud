::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: Device credentials
::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: For new devices, set the following values:
:: Application will now generate USERNAME AND PASSWORD based on DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD
::
:: DEVICE_ID        - should match UUID during device registration      
:: DEVICE_SERIAL    - should match Serial Number during device registration 
:: DEVICE_MACADD    - should match POE MAC Address during device registration 
:: DEVICE_SECRETKEY - [CONFIDENTIAL] please ASK ME directly or check the SKYPE GROUP
::
:: For existing devices (backward compatibility), set the following values:
::
:: DEVICE_ID        - should match UUID during device registration   
:: USER             - should match UUID during device registration   
:: PASS             - should match Serial Number during device registration 
::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set DEVICE_ID=""

:: For new devices
set DEVICE_SERIAL=""
set DEVICE_MACADD=""
set DEVICE_SECRETKEY=""

:: For existing devices (backward compatibility)
set USER=""
set PASS=""



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: Device certificates
::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set DEVICE_CA="cert_ecc/rootca.pem"
set DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
set DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"



::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: Backend message broker
::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: DEV environment              - set HOST to ec2-54-88-41-145.compute-1.amazonaws.com
:: PROD/TEST environment        - set HOST to richmondu.com
::
:: LOCAL non-docker environment - set HOST to localhost
:: LOCAL docker environment     - set HOST to 192.168.99.100 [double check with docker-machine ip]
::
:: KUBERNETES environment       - set PORT to 30883
::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

set PORT="8883"
set HOST="ec2-54-88-41-145.compute-1.amazonaws.com"




python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_PORT %PORT% --USE_DEVICE_SERIAL %DEVICE_SERIAL% --USE_DEVICE_MACADD %DEVICE_MACADD% --USE_DEVICE_SECRETKEY %DEVICE_SECRETKEY% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause

