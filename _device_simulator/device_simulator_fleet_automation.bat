:: NOTE: All empty strings are required to be set

:: Account user name and password
set USER=""
set PASS=""

:: Server to connect to
set HOST=""
set PORT="443"
set SECRETKEY=""

:: Number of device to register and run
:: Max of 255
set DEVICE_COUNT="2"

:: Name prefix to be used for devicenames
set DEVICE_NAME_PREFIX="DeviceFleet"

:: Key assignment ::
:: 000-009
:: 010-019 Rich
:: 020-029 Prabu
:: 030-039 Karan
:: 040-049 Sino
:: 050-059 Ajith
:: 060-069 Su
:: 070-079 Thang
:: 080-089 Khang
:: 090-089 Trung
:: 100-109 Pham
:: 110-119 Hoa
:: 110-255
set UID_KEY=""


python.exe device_simulator_fleet_automation.py --USE_HOST %HOST% --USE_PORT %PORT% --USE_USERNAME %USER% --USE_PASSWORD %PASS% --USE_DEVICE_SECRETKEY %SECRETKEY% --USE_DEVICE_COUNT %DEVICE_COUNT% --USE_DEVICE_NAMEPREFIX %DEVICE_NAME_PREFIX% --USE_UID_KEY %UID_KEY%
pause

