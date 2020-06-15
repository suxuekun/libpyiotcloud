# OTA Firmware Uploader

This tool allows you to easily upload new firmware files to AWS S3.
The backend automatically synchronizes with the changes in AWS S3.

Please read the instructions below for more details.


### Instructions:

0. Install requirements.txt [pip install -r requirements.txt]

1. Check the [OTA Firmware JSON file](https://ft900-iot-portal.s3.amazonaws.com/latest_firmware_updates.json) at 

2. <b>Add the FIRMWARE BINARY</b> in new_firmware/<newfirmware.bin>

3. <b>Update the FIRMWARE DESCRIPTION</b> in new_firmware/new_firmware.json
   - Make sure to verify that the JSON file is valid via https://jsonlint.com/

4. <b>Update and run the script</b> ota_uploader.bat
   - Update the firmware filename and description filename
   - Add the PASSCODE [please ask Richmond]

5. Verify the OTA Firmware JSON file

