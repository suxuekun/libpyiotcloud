# User Guide:

This page contains a tutorial on <b>how to use setup and run the device simulators</b> in Windows or Linux/MacOS. 

1. Access the IoT portal, create an account and login.
2. <b>Register a device</b> (Registering a device will return a unique DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD).
3. Prepare, setup and run the device simulator using the DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD.
   Use <b>device_simulator.py.bat</b> for Windows or <b>device_simulator.py.sh</b> for Linux/MacOS.


### Prepare

1. Install the latest Python 3.X.X from https://www.python.org/downloads/ [I'm using Python 3.6.6]

2. Install the required python libraries of the application. [pip install -r requirements.py.txt]


### Setup

1. Update <b>DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD</b> together with DEVICE_SECRETKEY and HOST

    <img src="../_images/device_simulator_py.png" width="600"/>

   Please ask https://github.com/richmondu for the DEVICE_SECRETKEY.


