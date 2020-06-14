# OTA Firmware Uploader

This tool allows the firmware device team to easily upload new firmware files for testing.


### Instructions:

0. Install requirements.txt
   - pip install -r requirements.txt

1. Check the <b>OTA Firmware JSON file</b> at 
   - https://ft900-iot-portal.s3.amazonaws.com/latest_firmware_updates.json

2. <b>Add the FIRMWARE BINARY</b> in new_firmware/<newfirmware.bin>

3. <b>Update the FIRMWARE DESCRIPTION</b> in new_firmware/new_firmware.json

4. <b>Update the script</b> ota_uploader.bat
   - Update the firmware filename and description filename
   - Add the PASSCODE [please ask Richmond]

5. Check the <b>OTA Firmware JSON file</b>

