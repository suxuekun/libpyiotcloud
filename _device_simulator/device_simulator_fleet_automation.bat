set HOST="localhost"
set PORT="443"
set USER=""
set PASS=""
set DEVICE_SECRETKEY=""
set DEVICE_COUNT="1"
set DEVICE_NAME_PREFIX="DeviceFleet"

python.exe device_simulator_fleet_automation.py --USE_HOST %HOST% --USE_PORT %PORT% --USE_USERNAME %USER% --USE_PASSWORD %PASS% --USE_DEVICE_SECRETKEY %DEVICE_SECRETKEY% --USE_DEVICE_COUNT %DEVICE_COUNT% --USE_DEVICE_NAMEPREFIX %DEVICE_NAME_PREFIX%
pause

