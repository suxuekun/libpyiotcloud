# Developer Guide

Below contains a step-by-step instructions on installing and setting up the frontend and backend web infrastructure of <b>IoT Portal on local machine</b>.

It also contains the documentation of <b>REST APIs</b> to be used by Android/IOS mobile apps to communicate with the backend.


### Development Tools

Please install the following tools to get the IoT Portal running on your local machine.

1. Git

    A. [Windows](https://git-scm.com/download/win)

    B. [Mac OS](https://git-scm.com/download/mac)


2. (Optional) Github Desktop

    A. [Windows](https://central.github.com/deployments/desktop/desktop/latest/win32)

    B. [Mac OS](https://central.github.com/deployments/desktop/desktop/latest/darwin)


3. Docker Toolbox or Docker Desktop

    A. Windows 7 - [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)

    B. Windows 10 Home - [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)

    C. Windows 10 Pro - [Docker Desktop](https://docs.docker.com/docker-for-windows/) 

    D. Mac OS - [Docker Desktop](https://docs.docker.com/docker-for-mac/)

    Note that I'm using both A and B on my PC and laptop, respectively.


4. Python 3.X.X

    A. [Windows](https://www.python.org/downloads/windows/)

    B. [Mac OS](https://www.python.org/downloads/mac-osx/)   


5. NodeJS 12.X.X

    A. [Windows](https://nodejs.org/dist/v12.13.0/node-v12.13.0-x64.msi)

    B. [Mac OS](https://nodejs.org/dist/v12.13.0/node-v12.13.0.pkg)


6. (Optional) [RabbitMQ](https://www.rabbitmq.com/download.html) 

    To be used for non-Docker version.
    Note that the configuration file needs to be updated. Refer to <b>rabbitmq.config</b> and <b>cert_ecc</b> folder in libpyiotcloud/rabbitmq/src


7. (Optional) [MongoDB](https://www.mongodb.com/download-center/community)

    To be used for non-Docker version.


### Development Setup

Please follow the steps below to get the IoT Portal running on your local machine.

1. Download the code from the repository.

		A. Run Docker Toolbox/Desktop as administrator.

		B. Type "git clone https://github.com/richmondu/libpyiotcloud"
		   In Mac OS, make sure the folder has permission. Refer to [this](https://stackoverflow.com/questions/16376035/fatal-could-not-create-work-tree-dir-kivy).

		C. Type "docker-machine ip"
		   Take note of the value as this will be used in the next steps.


2. Set the following environment system variables.

		A. AWS_ACCESS_KEY_ID
		B. AWS_SECRET_ACCESS_KEY

		C. AWS_COGNITO_CLIENT_ID
		D. AWS_COGNITO_USERPOOL_ID
		E. AWS_COGNITO_USERPOOL_REGION

		F. AWS_PINPOINT_ID
		G. AWS_PINPOINT_REGION
		H. AWS_PINPOINT_EMAIL

		I. CONFIG_USE_ECC

		J. PAYPAL_CLIENT_ID
		K. PAYPAL_CLIENT_SECRET

		L. TWILIO_ACCOUNT_SID
		M. TWILIO_AUTH_TOKEN
		N. TWILIO_NUMBER_FROM

		O. NEXMO_KEY
		P. NEXMO_SECRET

		Q. CONFIG_USE_EMAIL_MODEL
		R. CONFIG_USE_SMS_MODEL

		S. CONFIG_USE_CERTS
		T. CONFIG_USE_APIURL <b>// Refer to value of "docker-machine ip"</b>

    Please request for the values of the environment variables from me.


    In Linux/MacOS, use <b>export ENVIRONMENT_SYSTEM_VARIABLE="ENVIRONMENT_SYSTEM_VALUE"</b>

    In Windows, always <b>restart the Docker Toolbox/Desktop</b> after adding or updating an environment system variable.


3. Run the Docker images using the following commands.

		A. Type "cd libpyiotcloud"

		B. Type "docker-compose -f docker-compose.yml config"
		C. Type "docker-compose build" // To rebuild from scratch, add "--no-cache"
		D. Type "docker-compose up" // To run asynchronously, add "-d"

		E. Open a browser and browse https://docker-machine_ip // Refer to value of "docker-machine ip"


    <b>Note to stop the docker containers, do the following:</b>

		F. Type "Ctrl+C"

		G. Type "docker-compose down"
		H. Type "docker-compose rm"
		I. Type "docker network prune -f"


4. Run a device simulator.

		A. Type "cd _device_simulator"


    <b>PYTHON device simulator</b>

		B. Type "pip install -r requirements.py.txt"
		
		C. In Windows, update HOST variable in device_simulator.py.bat to the docker-machine ip
		   In Mac OS,  update HOST variable in device_simulator.py.sh to the docker-machine ip
		
		D. In Windows, run device_simulator.py.bat
		   In Mac OS,  run device_simulator.py.sh
		
		E. You should see "Device is now ready! ..."


    <b>NODEJS device simulator</b>

		F. Type "npm install -g mqtt" 
		G. Type "npm install -g argparse" 
		H. Type "npm install -g system-sleep" 
		I. Type "npm install -g os" 
		J. Type "npm install -g fs"

		K. In Windows, update HOST variable in device_simulator.js.bat to the docker-machine ip
		   In Mac OS,  update HOST variable in device_simulator.js.sh to the docker-machine ip
		
		L. In Windows, run device_simulator.js.bat
		   In Mac OS,  run device_simulator.js.sh    
		
		M. You should see "Device is now ready! ..."


### REST API Documentation

There are 3 ways to access the REST APIs.

1. Access directly from the live backend https://richmondu.com
2. Setup the docker containers of the backend on local machine and access via https://192.168.99.100 or https://ipofdocker
3. Setup the non-Docker version of the backend on local machine and access via https://localhost

Below contains a summary and a detailed description of all the current REST APIs.
More APIs will be added to support the new requirements.


SUMMARY:

	1. User sign-up/sign-in

		A. SIGN-UP                  - POST /user/signup
		B. CONFIRM SIGN-UP          - POST /user/confirm_signup
		C. RESEND CONFIRMATION CODE - POST /user/resend_confirmation_code
		D. FORGOT PASSWORD          - POST /user/forgot_password
		E. CONFIRM FORGOT PASSWORD  - POST /user/confirm_forgot_password
		F. LOGIN                    - POST /user/login
		G. LOGOUT                   - POST /user/logout
		H. GET USER INFO            - GET  /user

	2. Account subscription and payment

		A. GET SUBSCRIPTION     - GET  /account/subscription
		B. SET SUBSCRIPTION     - POST /account/subscription
		C. PAYPAL SETUP         - POST /account/payment/paypalsetup
		D. PAYPAL EXECUTE       - POST /account/payment/paypalexecute
		E. PAYPAL VERIFY        - POST /account/payment/paypalverify

	3. Device registration and management

		A. GET DEVICES          - GET    /devices
		B. ADD DEVICE           - POST   /devices/device
		C. DELETE DEVICE        - DELETE /devices/device
		D. GET DEVICE           - GET    /devices/device/DEVICENAME

	4. Device access and control

		A. GET DEVICE HISTORIES - GET  /devices/histories
		B. GET STATUS           - GET  /devices/device/DEVICENAME/status
		C. SET STATUS           - POST /devices/device/status
		D. GET IP               - GET  /devices/device/DEVICENAME/ip
		E. GET SUBNET           - GET  /devices/device/DEVICENAME/subnet
		F. GET GATEWAY          - GET  /devices/device/DEVICENAME/gateway
		G. GET MAC              - GET  /devices/device/DEVICENAME/mac
		H. GET GPIO             - GET  /devices/device/DEVICENAME/gpio/NUMBER
		I. SET GPIO             - POST /devices/device/gpio
		J. GET RTC              - GET  /devices/device/DEVICENAME/rtc
		K. SET UART             - POST /devices/device/uart
		L. SET NOTIFICATION     - POST /devices/device/notification



DETAILED:

	1. User sign-up/sign-in

		A. SIGN-UP
		-  Request:
		   POST /user/signup
		   data: { 'username': string, 'password': string, 'email': string, 'givenname': string, 'familyname': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		B. CONFIRM SIGN-UP
		-  Request:
		   POST /user/confirm_signup
		   data: { 'username': string, 'confirmationcode': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		C. RESEND CONFIRMATION CODE
		-  Request:
		   POST /user/resend_confirmation_code
		   data: { 'username': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		D. FORGOT PASSWORD
		-  Request:
		   POST /user/forgot_password
		   data: { 'email': string }
		-  Response:
		   {'status': 'OK', 'message': string, 'username': string}
		   {'status': 'NG', 'message': string}

		E. CONFIRM FORGOT PASSWORD
		-  Request:
		   POST /user/confirm_forgot_password
		   data: { 'username': string, 'confirmationcode': string, 'password': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		F. LOGIN
		-  Request:
		   POST /user/login
		   data: { 'username': string, 'password': string }
		-  Response:
		   {'status': 'OK', 'token': {'access': string, 'id': string, 'refresh': string} }
		   {'status': 'NG', 'message': string}

		G. LOGOUT
		-  Request:
		   POST /user/logout
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		H. GET USER INFO
		-  Request:
		   GET /user
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'info': {'email': string, 'family_name': string, 'given_name': string} }
		   {'status': 'NG', 'message': string}


	2. Account subscription and payment

		A. GET SUBSCRIPTION
		-  Request:
		   GET /account/subscription
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': string} }
		   {'status': 'NG', 'message': string}

		B. SET SUBSCRIPTION
		-  Request:
		   POST /account/subscription
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'credits': string }
		-  Response:
		   {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }
		   {'status': 'NG', 'message': string}

		C. PAYPAL SETUP
		-  Request:
		   POST /account/payment/paypalsetup
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'payment': {'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string} }
		-  Response:
		   {'status': 'OK', 'message': string, , 'approval_url': string, 'paymentId': string, 'token': string}
		   {'status': 'NG', 'message': string}

		D. PAYPAL EXECUTE
		-  Request:
		   POST /account/payment/paypalexecute
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'payment': {'paymentId': string, 'payerId': string, 'token': string} }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		E. PAYPAL VERIFY
		-  Request:
		   POST /account/payment/paypalverify
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'payment': {'paymentId': string} }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}


	3. Device registration and management

		A. GET DEVICES
		-  Request:
		   GET /devices
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
			 'devices': array[{'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}, ...]}
		   { 'status': 'NG', 'message': string}

		B. ADD DEVICE
		-  Request:
		   POST /devices/device
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}}
		   { 'status': 'NG', 'message': string}

		C. DELETE DEVICE
		-  Request:
		   DELETE /devices/device
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string }
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		D. GET DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey}}
		   { 'status': 'NG', 'message': string}


	4. Device access and control

		A. GET DEVICE TRANSACTION HISTORIES
		-  Request:
		   GET /devices/histories
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
			 'histories': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
		   { 'status': 'NG', 'message': string}

		B. GET STATUS
		-  Request:
		   GET /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		C. SET STATUS
		-  Request:
		   POST /devices/device/status
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string, 'value': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string}
		   { 'status': 'NG', 'message': string}

		D. GET IP
		-  Request:
		   GET /devices/device/DEVICENAME/ip
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		E. GET SUBNET
		-  Request:
		   GET /devices/device/DEVICENAME/subnet
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		F. GET GATEWAY
		-  Request:
		   GET /devices/device/DEVICENAME/gateway
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		G. GET MAC
		-  Request:
		   GET /devices/device/DEVICENAME/mac
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		H. GET GPIO
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/NUMBER
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		I. SET GPIO
		-  Request:
		   POST /devices/device/gpio
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string, 'number': string, 'value': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		J. GET RTC
		-  Request:
		   GET /devices/device/DEVICENAME/rtc
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		K. SET UART
		-  Request:
		   POST /devices/device/uart
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string, 'value': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		L. SET NOTIFICATION
		-  Request:
		   POST /devices/device/notification
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string, 'recipient': string, 'message': string }
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}



### Database Documentation

1. TODO

