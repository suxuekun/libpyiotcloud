set PASSCODE=""
set FIRMWARE_BIN="new_firmware/iotmodem_0.4.bin"
set FIRMWARE_DESC="new_firmware/new_firmware.json"

python.exe ota_uploader.py --USE_PASSCODE %PASSCODE% --USE_FIRMWARE_BIN %FIRMWARE_BIN% --USE_FIRMWARE_DESC %FIRMWARE_DESC%
pause
