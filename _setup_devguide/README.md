# Developer Guide

Below contains a step-by-step instructions on installing and setting up the frontend and backend web infrastructure of <b>IoT Portal on local machine</b>.

It also contains the documentation of <b>REST APIs</b> to be used by Android/IOS mobile apps to communicate with the backend and 3rd-party services. 

It also contains the documentation of <b>Device Firmware Messaging APIs</b> to be used by device firmware to communicate with the backend message broker. 


## Development Tools

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


## Development Setup

Please follow the steps below to get the IoT Portal running on your local machine.

Having the backend running on your local machine will enable you 
to eventually do code modifications as needed while developing the mobile applications.
This means you'll be able to update or add new APIs as the mobile app requires.
Or at the least be able to experiment before proposing new or modified APIs.

1. Download the code from the repository.

		A. Run Docker Toolbox/Desktop as administrator.

		B. Type "git clone https://github.com/richmondu/libpyiotcloud"
		   In Mac OS, make sure the folder has permission. Refer to https://stackoverflow.com/questions/16376035/fatal-could-not-create-work-tree-dir-kivy.

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
		T. CONFIG_USE_APIURL // Refer to value of "docker-machine ip"

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
		   // Refer to value of "docker-machine ip"
		   
		D. In Windows, run device_simulator.py.bat
		   In Mac OS,  run device_simulator.py.sh
		
		E. You should see "Device is now ready! ..."
		   This means the device simulator is now connected to the dockerized backend on local machine.

    <b>NODEJS device simulator</b>

		F. Type "npm install -g mqtt" 
		G. Type "npm install -g argparse" 
		H. Type "npm install -g system-sleep" 
		I. Type "npm install -g os" 
		J. Type "npm install -g fs"

		K. In Windows, update HOST variable in device_simulator.js.bat to the docker-machine ip
		   In Mac OS,  update HOST variable in device_simulator.js.sh to the docker-machine ip
		   // Refer to value of "docker-machine ip"
		   
		L. In Windows, run device_simulator.js.bat
		   In Mac OS,  run device_simulator.js.sh    
		
		M. You should see "Device is now ready! ..."
		   This means the device simulator is now connected to the dockerized backend on local machine.



To run tests with the device simulator, please refer to the usage guide in https://github.com/richmondu/libpyiotcloud/tree/master/_device_simulator.



## REST API Documentation

This is for the front-end developers.

The REST APIs are the gateway of the frontend (mobile apps, web app) to the backend (3rd party APIs and services). <b>The frontend will not directly access any 3rd party APIs and services for security reasons.</b> The frontend will only communicate with the REST APIs.

  <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/architecture_frontend.png" width="1000"/>

  <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/architecture_backend.png" width="1000"/>


There are 3 ways to access the REST APIs.

1. Access directly from the live backend https://richmondu.com
2. Setup the docker containers of the backend on local machine and access via https://192.168.99.100 or https://ipofdocker
3. Setup the non-Docker version of the backend on local machine and access via https://localhost

Below contains a summary and a detailed description of all the current REST APIs.
More APIs will be added to support the new requirements.


SUMMARY:

	1. User sign-up/sign-in APIs

		A. SIGN-UP                     - POST   /user/signup
		B. CONFIRM SIGN-UP             - POST   /user/confirm_signup
		C. RESEND CONFIRMATION CODE    - POST   /user/resend_confirmation_code
		D. FORGOT PASSWORD             - POST   /user/forgot_password
		E. CONFIRM FORGOT PASSWORD     - POST   /user/confirm_forgot_password
		F. LOGIN                       - POST   /user/login
		G. LOGOUT                      - POST   /user/logout
		H. GET USER INFO               - GET    /user
		I. UPDATE USER INFO            - POST   /user
		J. DELETE USER                 - DELETE /user
		K. REFRESH USER TOKEN          - POST   /user/token
		L. VERIFY PHONE NUMBER         - POST   /user/verify_phone_number
		M. CONFIRM VERIFY PHONE NUMBER - POST   /user/confirm_verify_phone_number
		N. CHANGE PASSWORD             - POST   /user/change_password

	2. Device registration and management APIs

		A. GET DEVICES                 - GET    /devices
		B. ADD DEVICE                  - POST   /devices/device/DEVICENAME
		C. DELETE DEVICE               - DELETE /devices/device/DEVICENAME
		D. GET DEVICE                  - GET    /devices/device/DEVICENAME

	3. Device access and control APIs

		New requirements:
		A. GET STATUS                  - GET    /devices/device/DEVICENAME/status
		B. SET STATUS                  - POST   /devices/device/DEVICENAME/status
		C. GET UART PROPERTIES         - GET    /devices/device/DEVICENAME/uart/NUMBER/properties
		D. SET UART PROPERTIES         - POST   /devices/device/DEVICENAME/uart/NUMBER/properties
		E. GET GPIO VOLTAGE            - GET    /devices/device/DEVICENAME/gpio/voltage
		F. SET GPIO VOLTAGE            - POST   /devices/device/DEVICENAME/gpio/voltage
		G. GET GPIO PROPERTIES         - GET    /devices/device/DEVICENAME/gpio/NUMBER/properties
		H. SET GPIO PROPERTIES         - POST   /devices/device/DEVICENAME/gpio/NUMBER/properties

		Old requirements:
		A. GET STATUS                  - GET    /devices/device/DEVICENAME/status
		B. SET STATUS                  - POST   /devices/device/DEVICENAME/status
		C. GET IP                      - GET    /devices/device/DEVICENAME/ip
		D. GET SUBNET                  - GET    /devices/device/DEVICENAME/subnet
		E. GET GATEWAY                 - GET    /devices/device/DEVICENAME/gateway
		F. GET MAC                     - GET    /devices/device/DEVICENAME/mac
		G. GET GPIO                    - GET    /devices/device/DEVICENAME/gpio/NUMBER
		H. SET GPIO                    - POST   /devices/device/DEVICENAME/gpio/NUMBER
		I. GET RTC                     - GET    /devices/device/DEVICENAME/rtc
		J. SET UART                    - POST   /devices/device/DEVICENAME/uart
		K. SET NOTIFICATION            - POST   /devices/device/DEVICENAME/notification

	4. Device transaction recording APIs

		A. GET HISTORIES               - GET    /devices/histories
		B. GET HISTORIES FILTERED      - POST   /devices/histories
		   (filter by device name, direction, topic, date start, date end)

	5. Account subscription and payment APIs

		A. GET SUBSCRIPTION            - GET    /account/subscription
		B. SET SUBSCRIPTION            - POST   /account/subscription
		C. PAYPAL SETUP                - POST   /account/payment/paypalsetup
		D. PAYPAL EXECUTE              - POST   /account/payment/paypalexecute
		E. PAYPAL VERIFY               - POST   /account/payment/paypalverify



DETAILED:

	1. User sign-up/sign-in APIs

		A. SIGN-UP
		-  Request:
		   POST /user/signup
		   headers: {'Authorization': 'Bearer ' + jwtEncode(email, password), 'Content-Type': 'application/json'}
		   data: { 'email': string, 'phone_number': string, 'name': string }
		   // email must be unique for all users (Cognito will fail already used email)
		   // email is treated as username in all succeeding APIs
		   // phone_number is optional
		   // phone number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
		   // name can be 1 or multiple words
		   // password length is 6 characters minimum as set in Cognito
		   // OTP will be sent in the registered email
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		-  Details:
		   How to compute the JWT token using Javascript
		   base64UrlEncodedHeader = urlEncode(base64Encode(JSON.stringify({
		     "alg": "HS256",
		     "typ": "JWT"
		   })));
		   base64UrlEncodedPayload = urlEncode(base64Encode(JSON.stringify({
		     "username": email,
		     "password": password,
		     "iat": Math.floor(Date.now() / 1000), // epoch time in seconds
		     "exp": iat + 10,                      // expiry in seconds
		   })));
		   base64UrlEncodedSignature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(
		     base64UrlEncode(header) + "." + base64UrlEncode(payload),
		     SECRET_KEY                            // message me for the value of the secret key
		     )));
		   JWT = base64UrlEncodedHeader + "." base64UrlEncodedPayload + "." + base64UrlEncodedSignature
		   Double check your results here: https://jwt.io/

		B. CONFIRM SIGN-UP
		-  Request:
		   POST /user/confirm_signup
		   headers: {'Content-Type': 'application/json'}
		   data: { 'username': string, 'confirmationcode': string }
		   // confirmationcode refers to the OTP code sent via email triggered by SIGN-UP
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		C. RESEND CONFIRMATION CODE
		-  Request:
		   POST /user/resend_confirmation_code
		   headers: {'Content-Type': 'application/json'}
		   data: { 'username': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		D. FORGOT PASSWORD
		-  Request:
		   POST /user/forgot_password
		   headers: {'Content-Type': 'application/json'}
		   data: { 'email': string }
		-  Response:
		   {'status': 'OK', 'message': string, 'username': string}
		   {'status': 'NG', 'message': string}

		E. CONFIRM FORGOT PASSWORD
		-  Request:
		   POST /user/confirm_forgot_password
		   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password), 'Content-Type': 'application/json'}
		   data: { 'confirmationcode': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		-  Details:
		   How to compute the JWT token using Javascript
		   base64UrlEncodedHeader = urlEncode(base64Encode(JSON.stringify({
		     "alg": "HS256",
		     "typ": "JWT"
		   })));
		   base64UrlEncodedPayload = urlEncode(base64Encode(JSON.stringify({
		     "username": username,
		     "password": password,
		     "iat": Math.floor(Date.now() / 1000), // epoch time in seconds
		     "exp": iat + 10,                      // expiry in seconds
		   })));
		   base64UrlEncodedSignature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(
		     base64UrlEncode(header) + "." + base64UrlEncode(payload),
		     SECRET_KEY                            // message me for the value of the secret key
		     )));
		   JWT = base64UrlEncodedHeader + "." base64UrlEncodedPayload + "." + base64UrlEncodedSignature
		   Double check your results here: https://jwt.io/

		F. LOGIN
		-  Request:
		   POST /user/login
		   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password)}
		-  Response:
		   {'status': 'OK', 'message': string, 'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
		   {'status': 'NG', 'message': string}
		   // name is now included in the response as per special UX requirement
		-  Details:
		   How to compute the JWT token using Javascript
		   base64UrlEncodedHeader = urlEncode(base64Encode(JSON.stringify({
		     "alg": "HS256",
		     "typ": "JWT"
		   })));
		   base64UrlEncodedPayload = urlEncode(base64Encode(JSON.stringify({
		     "username": username,
		     "password": password,
		     "iat": Math.floor(Date.now() / 1000), // epoch time in seconds
		     "exp": iat + 10,                      // expiry in seconds
		   })));
		   base64UrlEncodedSignature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(
		     base64UrlEncode(header) + "." + base64UrlEncode(payload),
		     SECRET_KEY                            // message me for the value of the secret key
		     )));
		   JWT = base64UrlEncodedHeader + "." base64UrlEncodedPayload + "." + base64UrlEncodedSignature
		   Double check your results here: https://jwt.io/

		G. LOGOUT
		-  Request:
		   POST /user/logout
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		H. GET USER INFO
		-  Request:
		   GET /user
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 
		    'info': {'name': string, 'email': string, 'phone_number': string, 'email_verified': boolean, 'phone_number_verified': boolean} }
		   // phone_number and phone_number_verified are not included if no phone_number has been added yet
		   // phone_number can be added using SIGN UP or UPDATE USER INFO
		   // phone_number_verified will return true once it has been verified using VERIFY PHONE NUMBER and CONFIRM VERIFY PHONE NUMBER
		   {'status': 'NG', 'message': string}

		I. UPDATE USER INFO
		-  Request:
		   POST /user
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'name': string, 'phone_number': string}
		   // phone_number is optional
		   // phone_number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
		   // When user changes or adds phone_number, phone_number_verified returned by GET USER INFO will always return false
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		J. DELETE USER
		-  Request:
		   DELETE /user
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		K. REFRESH USER TOKEN
		-  Request:
		   POST /user/token
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'refresh': string, 'id: string' }
		-  Response:
		   {'status': 'OK', 'message': string, 'token' : {'access': string, 'refresh': string, 'id': string}}
		   {'status': 'NG', 'message': string}

		L. VERIFY PHONE NUMBER
		-  Request:
		   POST /user/verify_phone_number
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // OTP will be sent via SMS in the registered phone_number
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		M. CONFIRM VERIFY PHONE NUMBER
		-  Request:
		   POST /user/confirm_verify_phone_number
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'confirmationcode': string}
		   // confirmationcode refers to the OTP code sent via SMS triggered by VERIFY PHONE NUMBER
		   // after this step, GET USER INFO will return phone_number_verified as true 
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		N. CHANGE PASSWORD
		-  Request:
		   POST /user/change_password
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'token': jwtEncode(password, newpassword)}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		-  Details:
		   How to compute the JWT token using Javascript
		   base64UrlEncodedHeader = urlEncode(base64Encode(JSON.stringify({
		     "alg": "HS256",
		     "typ": "JWT"
		   })));
		   base64UrlEncodedPayload = urlEncode(base64Encode(JSON.stringify({
		     "username": password,
		     "password": newpassword,
		     "iat": Math.floor(Date.now() / 1000), // epoch time in seconds
		     "exp": iat + 10,                      // expiry in seconds
		   })));
		   base64UrlEncodedSignature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(
		     base64UrlEncode(header) + "." + base64UrlEncode(payload),
		     SECRET_KEY                            // message me for the value of the secret key
		     )));
		   JWT = base64UrlEncodedHeader + "." base64UrlEncodedPayload + "." + base64UrlEncodedSignature
		   Double check your results here: https://jwt.io/


	2. Device registration and management APIs

		A. GET DEVICES
		-  Request:
		   GET /devices
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // deviceid refers to UUID
		   // timestamp refers to the epoch time the device was registered/added

		B. ADD DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'deviceid': string, 'serialnumber': string}
		   // deviceid refers to UUID
		   // format of UUID and Serial Number has not yet been finalized by Sree
		   // currently no checking is performed on the UUID and Serial Number format
		   // web prototype temporarily uses the format from PanL
		   //   UUID: PH80XXRRMMDDYYzz (16 characters)
		   //   SerialNumber: SSSSS (5 digits)
		   //   where ZZ hexadecimal is equivalent to SSSSS in decimal
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		C. DELETE DEVICE
		-  Request:
		   DELETE /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		D. GET DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string}}
		   { 'status': 'NG', 'message': string}
		   // deviceid refers to UUID
		   // timestamp refers to the epoch time the device was registered/added


	3. Device access and control APIs

		For device APIs, note that DEVICENAME is used instead of DEVICEID.
		This strategy is more secure as the unique DEVICEID is not easily exposed in the HTTP packets.
		The APIs perform the DEVICENAME and DEVICEID mapping appropriately.

		DEVICEID is unique for all devices.
		DEVICENAME is unique for all devices of a user.
		Two users can have the same DEVICENAME. 
		But this will not cause conflict because each API call provides a token which contains user's USERNAME.

		New requirements:

		A. GET STATUS
		-  Request:
		   GET /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string }
		   // value can be any of the following: restarting, stopping, stopped, starting, running

		B. SET STATUS
		-  Request:
		   POST /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'value': string }
		   // value can be any of the following: restart, stop, start
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string}
		   { 'status': 'NG', 'message': string }

		C. GET UART PROPERTIES
		-  Request:
		   GET /devices/device/DEVICENAME/uart/NUMBER/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { 'baudrate': int, 'parity': int } }
		   { 'status': 'NG', 'message': string }
		   // baudrate is an index of the value in the list of baudrates
		   // parity is an index of the value in the list of parities
		   // sending only the index saves memory on the device and computation on frontend

		D. SET UART PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/uart/NUMBER/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'baudrate': int, 'parity': int }
		   // baudrate is an index of the value in the list of baudrates
		   // parity is an index of the value in the list of parities
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		E. GET GPIO VOLTAGE
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/voltage
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // note that no gpio NUMBER is included because this applies to all 4 gpios
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
		   { 'status': 'NG', 'message': string }
		   // voltage is an index of the value in the list of voltages

		F. SET GPIO VOLTAGE
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/voltage
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'voltage': int }
		   // note that no gpio NUMBER is included because this applies to all 4 gpios
		   // voltage is an index of the value in the list of voltages
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		G. GET GPIO PROPERTIES
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/NUMBER/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int } }
		   { 'status': 'NG', 'message': string }
		   // direction is an index of the value in the list of directions
		   // mode is an index of the value in the list of modes
		   // alert is an index of the value in the list of alerts
		   // alertperiod is the number of seconds to alert when alert is set to continuously
		   // sending only the index saves memory on the device and computation on frontend

		H. SET GPIO PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/NUMBER/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int }
		   // direction is an index of the value in the list of directions
		   // mode is an index of the value in the list of modes
		   // alert is an index of the value in the list of alerts
		   // alertperiod is the number of seconds to alert when alert is set to continuously
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


		Old requirements:

		A. GET STATUS
		-  Request:
		   GET /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		B. SET STATUS
		-  Request:
		   POST /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'value': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string}
		   { 'status': 'NG', 'message': string}

		C. GET IP
		-  Request:
		   GET /devices/device/DEVICENAME/ip
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		D. GET SUBNET
		-  Request:
		   GET /devices/device/DEVICENAME/subnet
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		E. GET GATEWAY
		-  Request:
		   GET /devices/device/DEVICENAME/gateway
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		F. GET MAC
		-  Request:
		   GET /devices/device/DEVICENAME/mac
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		G. GET GPIO
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/NUMBER
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		H. SET GPIO
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/NUMBER
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'value': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		I. GET RTC
		-  Request:
		   GET /devices/device/DEVICENAME/rtc
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		J. SET UART
		-  Request:
		   POST /devices/device/DEVICENAME/uart
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'value': string }
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': string }
		   { 'status': 'NG', 'message': string}

		K. SET NOTIFICATION
		-  Request:
		   POST /devices/device/DEVICENAME/notification
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'recipient': string, 'message': string }
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}


	4. Device transaction recording APIs

		A. GET HISTORIES
		-  Request:
		   GET /devices/histories
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'histories': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
		   { 'status': 'NG', 'message': string}

		B. GET HISTORIES FILTERED
		-  Request:
		   POST /devices/histories
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string, 'direction': string, 'topic': string, 'datebegin': int, 'dateend': int }
		   // all data items are optional (when data is empty, that is no filters are set, it is actually equivalent to as GET HISTORIES)
		   // to filter by device name, include devicename
		   // to filter by direction, include direction
		   // to filter by topic, include topic
		   // to filter by date, include datebegin or both datebegin, dateend
		   // datebegin and dateend are both epoch computed values
		   // List of topics: "get_status", "set_status", "get_ip", "get_subnet", "get_gateway", "get_mac", "get_gpio", "set_gpio", "get_rtc", "write_uart", "trigger_notifications"
		   // List of directions: "To", "From"
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'histories': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
		   { 'status': 'NG', 'message': string}


	5. Account subscription and payment APIs

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
		   data: { 'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string }
		-  Response:
		   {'status': 'OK', 'message': string, , 'approval_url': string, 'paymentId': string, 'token': string}
		   {'status': 'NG', 'message': string}

		D. PAYPAL EXECUTE
		-  Request:
		   POST /account/payment/paypalexecute
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'paymentId': string, 'payerId': string, 'token': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		E. PAYPAL VERIFY
		-  Request:
		   POST /account/payment/paypalverify
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'paymentId': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}



## Device Firmware Messaging API Documentation

This is for the firmware developers.

A device can connect to the portal using MQTT protocol over TLS connection.
It establishes connection with the message broker using its UUID and SerialNumber as MQTT username and password respectively.
This is a security measure added in addition to the mutual authentication using SSL X.509 certificates with ECC security.
The ECC certificates are stored in a 3rd-party hardware ATECC chip for hardware-grade secure storage.

	Security measures for device connectivity:

	1. MQTT connectivity over secured TLS connection
	2. ECC-based (Elliptic Curve Cryptography ECC) PKI and X.509 certificates
	3. Enforcement of mutual authentication on both MQTT broker and MQTT client configurations
	4. Unique MQTT credentials (username and password) per device
	5. Strict restrictions for MQTT topic permission (subscribe and publish) per device
	6. [TODO] ECC certificates stored in 3rd-party ATECC hardware chip 

Upon connection, each device subscribes to its own dedicated MQTT topic using its device identification (DEVICEID/#).
As a result, it will only be receiving subtopics under DEVICEID topic solely for the device.
Each device publishes to its own assigned MQTT topic using its device identification and server (server/DEVICEID/#)
Subscribing or publishing to other MQTT topics will fail as the message broker restricts the permissions of topic for each device.

Below is a summary and a detailed list of the topics the device will receive and publish.


SUMMARY:

	1. STATUS
		A. GET STATUS           receive: DEVICEID/get_status,          publish: server/DEVICEID/get_status
		B. SET STATUS           receive: DEVICEID/set_status,          publish: server/DEVICEID/set_status

	2. UART
		A. GET UART PROPERTIES  receive: DEVICEID/get_uart_properties, publish: server/DEVICEID/get_uart_properties
		B. SET UART PROPERTIES  receive: DEVICEID/set_uart_properties, publish: server/DEVICEID/set_uart_properties

	3. GPIO
		A. GET GPIO VOLTAGE     receive: DEVICEID/get_gpio_voltage,    publish: server/DEVICEID/get_gpio_voltage
		B. SET GPIO VOLTAGE     receive: DEVICEID/set_gpio_voltage,    publish: server/DEVICEID/set_gpio_voltage
		C. GET GPIO PROPERTIES  receive: DEVICEID/get_gpio_properties, publish: server/DEVICEID/get_gpio_properties
		D. SET GPIO PROPERTIES  receive: DEVICEID/set_gpio_properties, publish: server/DEVICEID/set_gpio_properties

	4. I2C
		A. get_i2c_properties   receive: DEVICEID/get_i2c_properties,  publish: server/DEVICEID/get_i2c_properties
		B. set_i2c_properties   receive: DEVICEID/set_i2c_properties,  publish: server/DEVICEID/set_i2c_properties


DETAILED:

	1. STATUS

		A. GET STATUS
		-  Receive:
		   topic: DEVICEID/get_status
		-  Publish:
		   topic: server/DEVICEID/get_status
		   payload: { 'value': string }

		B. SET STATUS
		-  Receive:
		   topic: DEVICEID/set_status
		   payload: { 'value': string }
		-  Publish:
		   topic: server/DEVICEID/set_status
		   payload: { 'value': string }

	2. UART

		A. GET UART PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_uart_properties
		   payload: { 'number': int }
		-  Publish:
		   topic: server/DEVICEID/get_uart_properties
		   payload: { 'value': { 'baudrate': int, 'parity': int } }

		B. SET UART PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_uart_properties
		   payload: { 'number': int, 'baudrate': int, 'parity': int }
		-  Publish:
		   topic: server/DEVICEID/set_uart_properties
		   payload: { 'value': { 'baudrate': int, 'parity': int } }

	3. GPIO

		A. GET GPIO VOLTAGE
		-  Receive:
		   topic: DEVICEID/get_gpio_voltage
		-  Publish:
		   topic: server/DEVICEID/get_gpio_voltage
		   payload: { 'value': int }

		B. SET GPIO VOLTAGE
		-  Receive:
		   topic: DEVICEID/set_gpio_voltage
		   payload: { 'voltage': int }
		-  Publish:
		   topic: server/DEVICEID/set_gpio_voltage
		   payload: { 'value': int }

		C. GET GPIO PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_gpio_properties
		   payload: { 'number': int }
		-  Publish:
		   topic: server/DEVICEID/get_gpio_properties
		   payload: { 'value': { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int } }

		D. SET GPIO PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_gpio_properties
		   payload: { 'number': int, 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int }
		-  Publish:
		   topic: server/DEVICEID/set_gpio_properties
		   payload: { 'value': { 'direction': int, 'mode': int, 'alert': int, 'alertperiod': int } }

	4. I2C

		A. get_i2c_properties
		-  Subscribe:
		   topic:
		   payload:
		-  Publish:
		   topic:
		   payload:

		B. set_i2c_properties
		-  Subscribe:
		   topic:
		   payload:
		-  Publish:
		   topic:
		   payload:


## Database Documentation

1. TODO



