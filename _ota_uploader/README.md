# OTA Firmware Uploader

This tool allows the firmware device team to easily upload new firmware files for testing.


### Instructions: (for the firmware team)

0. Install requirements.txt
   pip install -r requirements.txt

1. Check the OTA Firmware JSON file at 
   https://ft900-iot-portal.s3.amazonaws.com/latest_firmware_updates.json

2. Add the FIRMWARE BINARY in new_firmware/<newfirmware.bin>

3. Update the FIRMWARE DESCRIPTION in new_firmware/new_firmware.json

4. Update the script ota_uploader.bat
   a. Update the firmware filename and description filename
   b. Add the PASSCODE [please ask Richmond]

5. Check the OTA Firmware JSON file at 
   https://ft900-iot-portal.s3.amazonaws.com/latest_firmware_updates.json

