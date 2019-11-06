# How To Guide:

0. Access the IoT portal [here](https://richmondu.com). (iOS/Android app simulators are also available [here](https://creator.ionic.io/share/8f86e2005ba5).)

1. Create an account and login.

2. Register a device (Registering a device will return a unique DEVICE_ID).

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice.png" width="600"/>
    
    To add a device, click on the "+" button on the top right of the window.
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice_2.png" width="600"/>

    Type a name for the device. Ex. "Smart Device 1"
    
    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice_3.png" width="600"/>
    
    Wait for the device to be registered. A popup up window will appear that the device has been registered.

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/tutorial_adddevice_4.png" width="600"/>

    Copy the DEVICE ID by double clicking on it and typing Ctrl+C.
    

3. Set the DEVICE_ID on the device.

    - Device simulator (Python)
    - Device simulator (NodeJS)
    - FT900 device (FT900RevC or IoTModule)

4. Run the device.

5. Access and control the device via the IoT portal. (GPIO, RTC, UART, IP/MAC, etc)



# Device simulator (Python):

### Setup

1. Install the latest Python 3.X.X from https://www.python.org/downloads/

2. Install the required python libraries of the application:

    - pip install -r requirements.py.txt OR
    - python pip install -r requirements.py.txt

### Test

1. Update DEVICE_ID in <b>device_simulator.py.bat</b>

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_py.png" width="600"/>

2. Run <b>device_simulator.py.bat</b>



# Device simulator (NodeJS):

### Setup

1. Install the latest NodeJS from https://nodejs.org/en/download/

2. Go to device_simulator folder and install the required nodejs libraries of the application:

    - cd __device_simulator
    - npm install mqtt
    - npm install fs
    - npm install system-sleep
    - npm install os
    - npm install argparse

### Test

1. Update DEVICE_ID in <b>device_simulator.js.bat</b>

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/device_simulator_deviceid_js.png" width="600"/>
    
2. Run <b>device_simulator.js.bat</b>



# FT900 device (FT900RevC or IoTModule)

### Setup

1. Get the FT900 code [here](https://github.com/richmondu/FT900/tree/master/IoT/ft90x_iot_brtcloud).

### Test

1. Update DEVICE_ID in <b>iot_config.h</b>

    <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/code_ft90Xiotbrtcloud.png" width="600"/>
    
2. Compile code and load the binary.


