# User Guide:

This page contains a step-by-step tutorial on <b>how to use the IoT Portal</b> including <b>how to use the device simulators</b> or FT900 device module. 


### Step-by-step guide:

0. Access the IoT portal.

1. Create an account and login.

2. Register a device (Registering a device will return a unique DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD).

    <img src="../_images/tutorial_adddevice.png" width="600"/>

    To add a device, click on the "+" button on the top right of the window.

    <img src="../_images/tutorial_adddevice_2.png" width="600"/>

    Type a name for the device. Ex. "Smart Device 1"

    <img src="../_images/tutorial_adddevice_3.png" width="600"/>

    Wait for the device to be registered. A popup up window will appear that the device has been registered.

    <img src="../_images/tutorial_adddevice_4.png" width="600"/>

    Copy the DEVICE ID by double clicking on it and typing Ctrl+C.
    

3. Set the DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD and DEVICE_SECRETKEY on the device then run it.

    <b>Refer to corresponding sections below for setup instructions for the device simulators and FT900 device.</b>
    
    - Device simulator (Python) - <b>device_simulator.py.bat</b>
    
        <img src="../_images/device_simulator_deviceid_py.png" width="600"/>
    
    - FT900 device (FT900RevC or IoTModule) - <b>iot_config.h</b>

        <img src="../_images/code_ft90Xiotbrtcloud.png" width="600"/>



# Device simulator (Python):

### Setup

1. Install the latest Python 3.X.X from https://www.python.org/downloads/

    <img src="../_images/device_simulator_py.png" width="600"/>

    After installation, open a command prompt and type "Python". You should see the version of the "Python" installed.
    Note that I'm using Python 3.6.6.


2. Install the required python libraries of the application:

    - pip install -r requirements.py.txt OR
    - python pip install -r requirements.py.txt

    <img src="../_images/device_simulator_requirements_py.png" width="600"/>


### Test

1. Update DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD and DEVICE_SECRETKEY in <b>device_simulator.py.bat</b> (or device_simulator.py.sh for Linux/MacOS)

   NOTE: To get a DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD, you must first register a device in the IoT Portal.

    <img src="../_images/device_simulator_deviceid_py.png" width="600"/>

2. Update USER and PASS in <b>device_simulator.py.bat</b> (or device_simulator.py.sh for Linux/MacOS)

    <b> NOTE: After implementing additional security measures in the backend, device also needs to provide the MQTT username and MQTT password with the UUID and SerialNumber, respectively. </b>

    - DEVICE_ID = UUID
    - USER = UUID
    - PASS = Serial Number
    - HOST = Use prod or dev hostname

3. Run <b>device_simulator.py.bat</b> (or device_simulator.py.sh for Linux/MacOS)

    <img src="../_images/device_simulator_bootup_py.png" width="600"/>



