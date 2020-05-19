# User Guide:

This page contains a tutorial on <b>how to setup and run the device simulators</b> in Windows or Linux/MacOS. 

1. Access the IoT portal, create an account and login.
2. <b>Register a device</b> and then copy the DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD.
3. Prepare, setup and run the device simulator using the output from previous step.


### Prepare

1. Install the latest Python 3.X.X from https://www.python.org/downloads/ [I'm using Python 3.6.6]

2. Install the required python libraries of the application. [pip install -r requirements.py.txt]


### Setup

1. Use <b>device_simulator.py.bat</b> for Windows or <b>device_simulator.py.sh</b> for Linux/MacOS.

2. Update <b>DEVICE_ID, DEVICE_SERIAL, DEVICE_MACADD</b> together with <b>DEVICE_SECRETKEY and HOST</b>

   Please ask https://github.com/richmondu for the DEVICE_SECRETKEY.

    <img src="../_images/device_simulator_py.png" width="600"/>



