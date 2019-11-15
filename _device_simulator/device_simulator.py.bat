set DEVICE_ID="efa4c8663739c4b380e25164e58ff89bfbd27976"
set DEVICE_CA="cert_ecc/rootca.pem"
set DEVICE_CERT="cert_ecc/ft900device1_cert.pem"
set DEVICE_PKEY="cert_ecc/ft900device1_pkey.pem"


set HOST="richmondu.com"     ::For production testing
::set HOST="localhost"       ::For development testing with local non-Docker setup
::set HOST="192.168.99.100"  ::For development testing with local Docker setup 

set PORT="8883"
::set PORT="30883"           ::For development testing with Minikube Kubernetes

set USER=""
set PASS=""


python.exe device_simulator.py --USE_ECC 1 --USE_AMQP 0 --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_PORT %PORT% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause
