set DEVICE_ID="9dfa09de9c360f6f7b61da26efd75cbb6e77526a"
::set DEVICE_ID="37601281d3fcba385c22d1758cb5f96116db62d3"
set DEVICE_CA="cert/rootca.pem"
set DEVICE_CERT="cert/ft900device1_cert.pem"
set DEVICE_PKEY="cert/ft900device1_pkey.pem"

set HOST="localhost"
set USER="guest"
set PASS="guest"

node device_simulator.js --USE_DEVICE_ID %DEVICE_ID% --USE_DEVICE_CA %DEVICE_CA% --USE_DEVICE_CERT %DEVICE_CERT% --USE_DEVICE_PKEY %DEVICE_PKEY% --USE_HOST %HOST% --USE_USERNAME %USER% --USE_PASSWORD %PASS%
pause