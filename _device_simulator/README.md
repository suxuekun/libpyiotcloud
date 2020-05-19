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

	Notes:

	A. DEVICE_SECRETKEY - Please ask https://github.com/richmondu

	B. HOST - Server to connect to.

		- If connecting to cloud DEVELOPMENT setup, use the DEV URL.
		- If connecting to cloud PRODUCTION setup, use the PROD URL.
		- If connecting to Windows docker local setup, the default value is 192.168.99.100. Double check with docker-machine ip.
		- If connecting to MacOS docker local setup, the default value is 127.0.0.1 or localhost
		- If connecting to Windows non-docker local setup, the default value is 127.0.0.1 or localhost

	<img src="../_images/device_simulator_py.png" width="600"/>


### Run

1. Run the device simulator. You should see "Device is now ready! ..."

	This means the device simulator is now connected to the server as indicated in the HOST variable in the batch/bash script files.
