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


Below is the sequence diagram for live status values for SENSOR aka INPUT devices (I2C INPUT devices, ADC/ONEWIRE/TPROBE devices).

  <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/architecture_livestatus.png" width="1000"/>


There are 3 ways to access the REST APIs.

1. Access directly from the live backend https://richmondu.com
2. Setup the docker containers of the backend on local machine and access via https://192.168.99.100 or https://ipofdocker
3. Setup the non-Docker version of the backend on local machine and access via https://localhost

Below contains a summary and a detailed description of all the current REST APIs.
More APIs will be added to support the new requirements.


SUMMARY:

	1. User sign-up/sign-in APIs

		A. SIGN-UP                        - POST   /user/signup
		B. CONFIRM SIGN-UP                - POST   /user/confirm_signup
		C. RESEND CONFIRMATION CODE       - POST   /user/resend_confirmation_code
		D. FORGOT PASSWORD                - POST   /user/forgot_password
		E. CONFIRM FORGOT PASSWORD        - POST   /user/confirm_forgot_password
		F. LOGIN                          - POST   /user/login
		G. LOGOUT                         - POST   /user/logout
		H. GET USER INFO                  - GET    /user
		I. UPDATE USER INFO               - POST   /user
		J. DELETE USER                    - DELETE /user
		K. REFRESH USER TOKEN             - POST   /user/token
		L. VERIFY PHONE NUMBER            - POST   /user/verify_phone_number
		M. CONFIRM VERIFY PHONE NUMBER    - POST   /user/confirm_verify_phone_number
		N. CHANGE PASSWORD                - POST   /user/change_password


	2. Device registration and management APIs

		A. GET DEVICES                    - GET    /devices
		B. GET DEVICES FILTERED           - GET    /devices/filter/FILTERSTRING
		C. ADD DEVICE                     - POST   /devices/device/DEVICENAME
		D. DELETE DEVICE                  - DELETE /devices/device/DEVICENAME
		E. GET DEVICE                     - GET    /devices/device/DEVICENAME
		F. UPDATE DEVICE NAME             - POST   /devices/device/DEVICENAME/name


	3. Device access and control APIs (STATUS, UART, GPIO)

		//
		// status
		A. GET STATUS                     - GET    /devices/device/DEVICENAME/status
		B. SET STATUS                     - POST   /devices/device/DEVICENAME/status

		// settings
		C. GET SETTINGS                   - GET    /devices/device/DEVICENAME/settings
		D. SET SETTINGS                   - POST   /devices/device/DEVICENAME/settings

		//
		// uart
		E. GET UARTS                      - GET    /devices/device/DEVICENAME/uarts
		F. GET UART PROPERTIES            - GET    /devices/device/DEVICENAME/uart/properties
		G. SET UART PROPERTIES            - POST   /devices/device/DEVICENAME/uart/properties
		H. ENABLE/DISABLE UART            - POST   /devices/device/DEVICENAME/uart/enable

		//
		// gpio
		I. GET GPIOS                      - GET    /devices/device/DEVICENAME/gpios
		J. GET GPIO PROPERTIES            - GET    /devices/device/DEVICENAME/gpio/NUMBER/properties
		K. SET GPIO PROPERTIES            - POST   /devices/device/DEVICENAME/gpio/NUMBER/properties
		L. ENABLE/DISABLE GPIO            - POST   /devices/device/DEVICENAME/gpio/NUMBER/enable
		M. GET GPIO VOLTAGE               - GET    /devices/device/DEVICENAME/gpio/voltage
		N. SET GPIO VOLTAGE               - POST   /devices/device/DEVICENAME/gpio/voltage
		   (NUMBER can be 1-4 only and corresponds to GPIO1,GPIO2,GPIO3,GPIO4)

		//
		// sensor readings (for dashboard)
		O. GET PERIPHERAL SENSOR READINGS         - GET    /devices/device/DEVICENAME/sensors/readings
		P. GET PERIPHERAL SENSOR READINGS DATASET - GET    /devices/device/DEVICENAME/sensors/readings/dataset
		Q. DELETE PERIPHERAL SENSOR READINGS      - DELETE /devices/device/DEVICENAME/sensors/readings

		//
		// sensor properties
		R. DELETE PERIPHERAL SENSOR PROPERTIES    - DELETE /devices/device/DEVICENAME/sensors/properties


	4. Device access and control APIs (I2C)

		A. ADD I2C DEVICE                 - POST   /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME
		B. DELETE I2C DEVICE              - DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME
		C. GET I2C DEVICE                 - GET    /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME
		D. GET I2C DEVICES                - GET    /devices/device/DEVICENAME/i2c/NUMBER/sensors
		E. GET ALL I2C DEVICES            - GET    /devices/device/DEVICENAME/i2c/sensors
		F. GET ALL I2C INPUT DEVICES      - GET    /devices/device/DEVICENAME/i2c/sensors/input
		G. GET ALL I2C OUTPUT DEVICES     - GET    /devices/device/DEVICENAME/i2c/sensors/output
		H. SET I2C DEVICE PROPERTIES      - POST   /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/properties
		I. GET I2C DEVICE PROPERTIES      - GET    /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/properties
		J. ENABLE/DISABLE I2C DEVICE      - POST   /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/enable
		K. GET I2C DEVICE READINGS        - GET    /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/readings
		L. DELETE I2C DEVICE READINGS     - DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/readings
		M. GET I2C DEVICES READINGS       - GET    /devices/device/DEVICENAME/i2c/NUMBER/sensors/readings
		N. GET I2C DEVICE READINGS DATASET- GET    /devices/device/DEVICENAME/i2c/NUMBER/sensors/readings/dataset
		O. DELETE I2C DEVICES READINGS    - DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/readings
		   (NUMBER can be 1-4 only and corresponds to I2C1,I2C2,I2C3,I2C4)


	5. Device access and control APIs (ADC)

		A. ADD ADC DEVICE                 - POST   /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME
		B. DELETE ADC DEVICE              - DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME
		C. GET ADC DEVICE                 - GET    /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME
		D. GET ADC DEVICES                - GET    /devices/device/DEVICENAME/adc/NUMBER/sensors
		E. GET ALL ADC DEVICES            - GET    /devices/device/DEVICENAME/adc/sensors
		F. SET ADC DEVICE PROPERTIES      - POST   /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/properties
		G. GET ADC DEVICE PROPERTIES      - GET    /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/properties
		H. ENABLE/DISABLE ADC DEVICE      - POST   /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/enable
		I. GET ADC DEVICE READINGS        - GET    /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/readings
		J. DELETE ADC DEVICE READINGS     - DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/readings
		K. GET ADC DEVICES READINGS       - GET    /devices/device/DEVICENAME/adc/NUMBER/sensors/readings
		L. GET ADC DEVICE READINGS DATASET- GET    /devices/device/DEVICENAME/adc/NUMBER/sensors/readings/dataset
		M. DELETE ADC DEVICES READINGS    - DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/readings
		   (NUMBER can be 1-2 only and corresponds to ADC1,ADC2)
		N. GET ADC VOLTAGE                - GET    /devices/device/DEVICENAME/adc/voltage
		O. SET ADC VOLTAGE                - POST   /devices/device/DEVICENAME/adc/voltage


	6. Device access and control APIs (1WIRE)

		A. ADD 1WIRE DEVICE               - POST   /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME
		B. DELETE 1WIRE DEVICE            - DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME
		C. GET 1WIRE DEVICE               - GET    /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME
		D. GET 1WIRE DEVICES              - GET    /devices/device/DEVICENAME/1wire/NUMBER/sensors
		E. GET ALL 1WIRE DEVICES          - GET    /devices/device/DEVICENAME/1wire/sensors
		F. SET 1WIRE DEVICE PROPERTIES    - POST   /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/properties
		G. GET 1WIRE DEVICE PROPERTIES    - GET    /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/properties
		H. ENABLE/DISABLE 1WIRE DEVICE    - POST   /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/enable
		I. GET 1WIRE DEVICE READINGS      - GET    /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/readings
		J. DELETE 1WIRE DEVICE READINGS   - DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/readings
		K. GET 1WIRE DEVICES READINGS     - GET    /devices/device/DEVICENAME/1wire/NUMBER/sensors/readings
		L. GET 1WIRE DEVICE READINGS DATASET- GET  /devices/device/DEVICENAME/1wire/NUMBER/sensors/readings/dataset
		M. DELETE 1WIRE DEVICES READINGS  - DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/readings
		   (NUMBER will always be 1 since there is only 1 1wire)


	7. Device access and control APIs (TPROBE)

		A. ADD TPROBE DEVICE              - POST   /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME
		B. DELETE TPROBE DEVICE           - DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME
		C. GET TPROBE DEVICE              - GET    /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME
		D. GET TPROBE DEVICES             - GET    /devices/device/DEVICENAME/tprobe/NUMBER/sensors
		E. GET ALL TPROBE DEVICES         - GET    /devices/device/DEVICENAME/tprobe/sensors
		F. SET TPROBE DEVICE PROPERTIES   - POST   /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/properties
		G. GET TPROBE DEVICE PROPERTIES   - GET    /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/properties
		H. ENABLE/DISABLE TPROBE DEVICE   - POST   /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/enable
		I. GET TPROBE DEVICE READINGS     - GET    /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings
		J. DELETE TPROBE DEVICE READINGS  - DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings
		K. GET TPROBE DEVICES READINGS    - GET    /devices/device/DEVICENAME/tprobe/NUMBER/sensors/readings
		L. GET TPROBE DEVICE READINGS DATASET- GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors/readings/dataset
		M. DELETE TPROBE DEVICES READINGS - DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/readings
		   (NUMBER will always be 1 since there is only 1 tprobe)


	8. Device transaction recording APIs

		A. GET HISTORIES                  - GET    /devices/histories
		B. GET HISTORIES FILTERED         - POST   /devices/histories
		   (filter by device name, direction, topic, date start, date end)

		C. GET MENOS HISTORIES            - GET    /devices/menos
		D. GET MENOS HISTORIES FILTERED   - POST   /devices/menos


	9. Account subscription and payment APIs

		A. GET SUBSCRIPTION               - GET    /account/subscription
		B. SET SUBSCRIPTION               - POST   /account/subscription
		C. PAYPAL SETUP                   - POST   /account/payment/paypalsetup
		D. PAYPAL EXECUTE                 - POST   /account/payment/paypalexecute
		E. PAYPAL VERIFY                  - POST   /account/payment/paypalverify


	10. Mobile services

		A. REGISTER DEVICE TOKEN          - POST   /mobile/devicetoken


	11. Supported devices

		A. GET SUPPORTED I2C DEVICES      - GET    /others/i2cdevices [OBSOLETED, use GET SUPPORTED SENSOR DEVICES instead]
		B. GET SUPPORTED SENSOR DEVICES   - GET    /others/sensordevices


	12. Others

		A. SEND FEEDBACK                  - POST   /others/feedback
		B. GET FAQS                       - GET    /others/faqs
		C. GET ABOUT                      - GET    /others/about


	13. HTTP error codes

		A. HTTP_400_BAD_REQUEST           - Invalid input
		B. HTTP_401_UNAUTHORIZED          - Invalid password or invalid/expired token
		C. HTTP_404_NOT_FOUND             - User or device not found
		D. HTTP_409_CONFLICT              - User or device already exist
		E. HTTP_500_INTERNAL_SERVER_ERROR - Internal processing error or 3rd-party API failure
		F. HTTP_503_SERVICE_UNAVAILABLE   - Device is offline/unreachable


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
		   {'status': 'OK', 'message': string, 
		    'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
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

		DEVICENAME (and other parameters) are included in the URL field because of the following reasons:
		- LIMITATION. HTTP GET requests do not permit including payload/data parameters.
		- CONSISTENCY. To make APIs consistent, HTTP POST/DELETE requests are also made similar to their corresponding HTTP GET requests.
		- PRACTICE. 3rd-party APIs such as RabbitMQ HTTP APIs also employ the same technique.
		- FRAMEWORK. Flask provides a framework to parse parameters in the URL path, applicable to both GET and POST, in the backend.
		- CONVENIENT. The consistency-ness makes it easy and convenient to implement and debug in the frontend.
		- EASY. Supporting this only requires simple string concatenation to generate the URL field.


		A. GET DEVICES
		-  Request:
		   GET /devices
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // deviceid refers to UUID
		   // timestamp refers to the epoch time (in seconds) the device was registered/added
		   // heartbeat refers to the epoch time (in seconds) of the last publish packet sent by the device
		   // heartbeat will only appear if device has published an MQTT packet
		   // In Javascript, heartbeat can be converted to a readable date using "new Date(heartbeat* 1000)"
		   // version will only appear if device has previously been queried already
		   // heartbeat and version are cached values

		B. GET DEVICES FILTERED
		-  Request:
		   GET /devices/filter/FILTERSTRING
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // filter will be applied to devicename and deviceid
		   // if devicename or deviceid contains the filter string, the device will be returned

		C. ADD DEVICE
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
		   // registering a device using an already used devicename returns HTTP_409_CONFLICT with 'Device name is already taken'
		   // registering a device using an already used deviceid returns HTTP_409_CONFLICT with 'Device UUID is already registered'
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		D. DELETE DEVICE
		-  Request:
		   DELETE /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		E. GET DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': string, 'heartbeat': string, 'version': string}}
		   { 'status': 'NG', 'message': string}
		   // deviceid refers to UUID
		   // timestamp refers to the epoch time (in seconds) the device was registered/added
		   // heartbeat refers to the epoch time (in seconds) of the last publish packet sent by the device
		   // heartbeat will only appear if device has published an MQTT packet
		   // In Javascript, heartbeat can be converted to a readable date using "new Date(heartbeat* 1000)"
		   // version will only appear if device has previously been queried already
		   // heartbeat and version are cached values

		F. UPDATE DEVICE NAME
		-  Request:
		   POST /devices/device/DEVICENAME/name
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'new_devicename': string}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // new_devicename refers to the new name of the device


	3. Device access and control APIs (STATUS, UART, GPIO)

		For device APIs, note that DEVICENAME is used instead of DEVICEID.
		This strategy is more secure as the unique DEVICEID is not easily exposed in the HTTP packets.
		The APIs perform the DEVICENAME and DEVICEID mapping appropriately.

		DEVICEID is unique for all devices.
		DEVICENAME is unique for all devices of a user.
		Two users can have the same DEVICENAME. 
		But this will not cause conflict because each API call provides a token which contains user's USERNAME.

		The NOTIFICATION object in GET/SET UART/GPIO/I2C PROPERTIES is made generic to be simple, extensible and performant.
		

		A. GET STATUS
		-  Request:
		   GET /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { "status": int, "version": string } }
		   { 'status': 'NG', 'message': string, 'value': { "heartbeat": string, "version": string} }
		   // status is an index of the value in the list of statuses
		   //   ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]
		   //      restart->restarting->running
		   //      stop->stopping->stopped
		   //      start->starting->running
		   // version is the firmware version in the string format of "major_version.minor_version"
		   // if HTTP ERROR CODE is HTTP_503_SERVICE_UNAVAILABLE, cached value containing heartbeat and version will be included in the error message
		   // heartbeat refers to the epoch time (in seconds) of the last publish packet sent by the device
		   // heartbeat will only appear if device has published an MQTT packet
		   // In Javascript, heartbeat can be converted to a readable date using "new Date(heartbeat* 1000)"

		B. SET STATUS
		-  Request:
		   POST /devices/device/DEVICENAME/status
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'status': int }
		   // status is an index of the value in the list of statuses
		   //   ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]
		   // for SET STATUS, only valid are "restart", "stop", "start"
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': {'status': int}}
		   { 'status': 'NG', 'message': string }


		C. GET SETTINGS
		-  Request:
		   GET /devices/device/DEVICENAME/settings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { "sensorrate": int } }
		   { 'status': 'NG', 'message': string }
		   // sensorrate is the time in seconds the device publishes sensor data for ENABLED devices

		D. SET SETTINGS
		-  Request:
		   POST /devices/device/DEVICENAME/settings
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'sensorrate': int }
		   // sensorrate is the time in seconds the device publishes sensor data for ENABLED devices
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


		E. GET UARTS
		-  Request:
		   GET /devices/device/DEVICENAME/uarts
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'value': { 
		        'uarts': [
		            {"enabled": int}, 
		        ]
		     }
		   }
		   // enabled is an int indicating if disabled (0) or enabled (1)

		F. GET UART PROPERTIES
		-  Request:
		   GET /devices/device/DEVICENAME/uart/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value':
		     { 
		        'baudrate': int,
		        'parity': int,
		        'flowcontrol': int,
		        'stopbits': int,
		        'databits': int,
		        'notification': { // this notification object is generic for UART/GPIO/I2C
		            'messages': [
		                { 'message': string, 'enable': boolean }, 
		            ],
		            'endpoints' : {
		                'mobile': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'email': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'notification': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'modem': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'storage': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		            }
		        }
		   } }
		   { 'status': 'NG', 'message': string }
		   // baudrate is an index of the value in the list of baudrates
		   //   ft900_uart_simple.h: UART_DIVIDER_XXX
		   //   ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
		   //      default = 7 (19200)
		   // parity is an index of the value in the list of parities
		   //   ft900_uart_simple.h: uart_parity_t enum
		   //   ["None", "Odd", "Even"]
		   //      default = 0 (None)
		   // flowcontrol is an index of the value in the list of flowcontrols
		   //   ["None", "Rts/Cts", "Xon/Xoff"]
		   //      default = 0 (None)
		   // stopbits is an index of the value in the list of stopbits
		   //   ft900_uart_simple.h: uart_stop_bits_t enum
		   //   ["1", "2"]
		   //      default = 0 (1)
		   // databits is an index of the value in the list of databits
		   //   ft900_uart_simple.h: uart_data_bits_t enum
		   //   ["7", "8"]
		   //      default = 1 (8)
		   // sending only the index saves memory on the device and computation on frontend

		G. SET UART PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/uart/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: 
		   { 
		        'baudrate': int,
		        'parity': int,
		        'flowcontrol': int,
		        'stopbits': int,
		        'databits': int,
		        'notification': { // this notification object is generic for UART/GPIO/I2C
		            'messages': [
		                { 'message': string, 'enable': boolean },
		            ],
		            'endpoints' : {
		                'mobile': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'email': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'notification': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'modem': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'storage': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		            }
		        }
		   }
		   // baudrate is an index of the value in the list of baudrates
		   //   ft900_uart_simple.h: UART_DIVIDER_XXX
		   //   ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
		   //      default = 7 (19200)
		   // parity is an index of the value in the list of parities
		   //   ft900_uart_simple.h: uart_parity_t enum
		   //   ["None", "Odd", "Even"]
		   //      default = 0 (None)
		   // flowcontrol is an index of the value in the list of flowcontrols
		   //   ["None", "Rts/Cts", "Xon/Xoff"]
		   //      default = 0 (None)
		   // stopbits is an index of the value in the list of stopbits
		   //   ft900_uart_simple.h: uart_stop_bits_t enum
		   //   ["1", "2"]
		   //      default = 0 (1)
		   // databits is an index of the value in the list of databits
		   //   ft900_uart_simple.h: uart_data_bits_t enum
		   //   ["7", "8"]
		   //      default = 1 (8)
		   // sending only the index saves memory on the device and computation on frontend
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		H. ENABLE/DISABLE UART
		-  Request:
		   POST /devices/device/DEVICENAME/uart/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }



		I. GET GPIOS
		-  Request:
		   GET /devices/device/DEVICENAME/gpios
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'value': { 
		        'voltage': int,
		        'gpios': [
		            {"enabled": int, "direction": int, "status": int},
		            {"enabled": int, "direction": int, "status": int},
		            {"enabled": int, "direction": int, "status": int},
		            {"enabled": int, "direction": int, "status": int},
		        ]
		     }
		   }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]
		   // enabled is an int indicating if disabled (0) or enabled (1)
		   // direction is an index of the value in the list of directions
		   //   ft900_gpio.h: pad_dir_t
		   //   ["Input", "Output"]
		   // status is an index of the value in the list of livestatuses
		   //   ["Low", "High"]

		J. GET GPIO PROPERTIES
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/NUMBER/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value':
		     { 
		        'direction': int,
		        'mode': int,
		        'alert': int,
		        'alertperiod': int,
		        'polarity': int,
		        'width': int,
		        'mark': int,
		        'space': int,
		        'count': int,
		        'notification': { // this notification object is generic for UART/GPIO/I2C
		            'messages': [
		                { 'message': string, 'enable': boolean }, // for GPIO, index 0 will always refer to message on activation
		                { 'message': string, 'enable': boolean }  // for GPIO, index 1 will always refer to message on deactivation
		            ],
		            'endpoints' : {
		                'mobile': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'email': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'notification': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'modem': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'storage': {
		                    'recipients': string,   // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': []   // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		            }
		        }
		   } }
		   { 'status': 'NG', 'message': string }
		   // direction is an index of the value in the list of directions
		   //     ft900_gpio.h: pad_dir_t
		   //     ["Input", "Output"]
		   // mode is an index of the value in the list of modes
		   //     ft900_gpio.h
		   //     direction == "Input"
		   //       ["High Level", "Low Level", "High Edge", "Low Edge"]
		   //     direction == "Output"
		   //       ["Level", "Pulse", "Clock"]
		   // alert is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   // alert is an optional and is valid only when direction points to Input
		   // alertperiod is optional and is valid only if alert points to Continuously
		   // alertperiod is in milliseconds and should be >= 100
		   // polarity is an index of the value in the list of polarities
		   //     ft900_gpio.h
		   //     direction == "Output"
		   //       ["Negative", "Positive"]
		   // polarity is optional and is valid only when direction points to Output
		   // width is optional and is valid only when direction points to Output and mode points to Pulse (width (ms) should be > 0)
		   // mark is optional and is valid only when direction points to Output and mode points to Clock (mark (ms) should be > 0)
		   // space is optional and is valid only when direction points to Output and mode points to Clock (space (ms) should be > 0)
		   // count is optional and is valid only when direction points to Output and mode points to Clock (count should be > 0)
		   // sending only the index saves memory on the device and computation on frontend

		K. SET GPIO PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/NUMBER/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: 
		   { 
		        'direction': int,
		        'mode': int,
		        'alert': int,
		        'alertperiod': int,
		        'polarity': int,
		        'width': int,
		        'mark': int,
		        'space': int,
		        'count': int,
		        'notification': { // this notification object is generic for UART/GPIO/I2C
		            'messages': [
		                { 'message': string, 'enable': boolean }, // for GPIO, index 0 will always refer to message on activation
		                { 'message': string, 'enable': boolean }  // for GPIO, index 1 will always refer to message on deactivation
		            ],
		            'endpoints' : {
		                'mobile': {
		                    'recipients': string, // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': [] // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'email': {
		                    'recipients': string, // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': [] // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'notification': {
		                    'recipients': string, // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': [] // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'modem': {
		                    'recipients': string, // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': [] // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		                'storage': {
		                    'recipients': string, // can be multiple items separated by comma
		                    'enable': boolean,
		                    'recipients_list': [] // array of JSON object. example: [{'to': string, 'group': boolean}, ],
		                },
		            }
		        }
		   }
		   // direction is an index of the value in the list of directions
		   //     ft900_gpio.h: pad_dir_t
		   //     ["Input", "Output"]
		   // mode is an index of the value in the list of modes
		   //     ft900_gpio.h
		   //     direction == "Input"
		   //       ["High Level", "Low Level", "High Edge", "Low Edge"]
		   //     direction == "Output"
		   //       ["Level", "Pulse", "Clock"]
		   // alert is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   // alert is an optional and is valid only when direction points to Input
		   // alertperiod is optional and is valid only if alert points to Continuously
		   // alertperiod is in milliseconds and should be >= 100
		   // polarity is an index of the value in the list of polarities
		   //     ft900_gpio.h
		   //     direction == "Output"
		   //       ["Negative", "Positive"]
		   // polarity is optional and is valid only when direction points to Output
		   // width is optional and is valid only when direction points to Output and mode points to Pulse (width (ms) should be > 0)
		   // mark is optional and is valid only when direction points to Output and mode points to Clock (mark (ms) should be > 0)
		   // space is optional and is valid only when direction points to Output and mode points to Clock (space (ms) should be > 0)
		   // count is optional and is valid only when direction points to Output and mode points to Clock (count should be > 0)
		   // sending only the index saves memory on the device and computation on frontend
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		L. ENABLE/DISABLE GPIO
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/NUMBER/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		M. GET GPIO VOLTAGE
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/voltage
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // note that no gpio NUMBER is included because this applies to all 4 gpios
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
		   { 'status': 'NG', 'message': string }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]

		N. SET GPIO VOLTAGE
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/voltage
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'voltage': int }
		   // note that no gpio NUMBER is included because this applies to all 4 gpios
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


		O. GET PERIPHERAL SENSOR READINGS
		-  Request:
		   GET /devices/device/DEVICENAME/sensors/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}} }
		   { 'status': 'NG', 'message': string}
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		P. GET PERIPHERAL SENSOR READINGS DATASET
		-  Request:
		   GET /devices/device/DEVICENAME/sensors/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': [], 'dataset': {'labels': [], 'data': []} }
		   { 'status': 'NG', 'message': string}
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass
		   // if sensor has a subclass: 'dataset':  {'labels': [], 'data': [[],[]]}
		      if sensor has no subclass: 'dataset': {'labels': [], 'data': []}
		      this make the dataset object directly useable by Chart.JS 

		Q. DELETE PERIPHERAL SENSOR READINGS
		-  Request:
		   DELETE /devices/device/DEVICENAME/sensors/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		R. DELETE PERIPHERAL SENSOR PROPERTIES
		-  Request:
		   DELETE /devices/device/DEVICENAME/sensors/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}


	4. Device access and control APIs (I2C)


		A. ADD I2C DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'units': [], 'formats': [], 'attributes': []}
		   // Note: multiclass sensor data requires adding of {'subclass': string, 'subattributes': []}
		   // call GET SUPPORTED SENSOR DEVICES to get the JSON data contained here: https://ft900-iot-portal.s3.amazonaws.com/supported_sensor_devices.json
		   // registering a sensor using an already used sensorname returns HTTP_409_CONFLICT with 'Sensor name is already taken'
		   // address should be greater than 0 and less than or equal to 255
		   // registering a sensor using an already used address for the slot returns HTTP_409_CONFLICT with 'Sensor address is already taken'
		   // Note: The device class defines if device type is INPUT or OUTPUT
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		B. DELETE I2C DEVICE
		-  Request:
		   DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		C. GET I2C DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be SPEAKER, DISPLAY, LIGHT, POTENTIOMETER, TEMPERATURE

		D. GET I2C DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		E. GET ALL I2C DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		F. GET ALL I2C INPUT DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/sensors/input
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		G. GET ALL I2C OUPUT DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/sensors/output
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		H. SET I2C DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   // LIGHT class
		   data: { 
		           "color": {
		               "usage": int,
		               "single": {
		                    "endpoint": int,
		                    "manual": int,
		                    "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		               },
		               "individual": {
		                   "red": {
		                       "endpoint": int,
		                       "manual": int,
		                       "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		                   },
		                   "green": {
		                       "endpoint": int,
		                       "manual": int,
		                       "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		                   },
		                   "blue": {
		                       "endpoint": int,
		                       "manual": int,
		                       "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		                   }
		               }
		           }, 
		           "fadeouttime": int 
		     }
		   //   color usage is an index to the list of color usages:
		   //     ["RGB as color", "RGB as component"]
		   //   single should be used if "RGB as color" is selected for color usage
		   //     manual is an int indicating the 0x00RRGGBB 
		   //   individual should be used if "RGB as component" is selected for color usage
		   //     manual is an int indicating the 0xRR or 0xGG or 0xBB
		   //   endpoint is an index to the list source endpoints:
		   //     ["Manual", "Hardware"]
		   //   if endpoint is Manual
		   //     manual is an integer value of the hex color 0xRRGGBB where each RR (red), GG (green), BB (blue) can be 0x00-0xFF (0-255)
		   //   if endpoint is Hardware
		   //     hardware contains the devicename (input IoT Modem device) and sensorname (input I2C device)
		   //       deviceid is the id of the IoT modem device
		   //       devicename is the name of the IoT modem device
		   //       peripheral is the name of the peripheral device (I2C, ADC, 1WIRE, TPROBE)
		   //       sensorname is the name of the input device
		   //       attribute is the attribute of the device to use
		   //       number is the peripheral number of the input device where sensor is connected to
		   //       address is the address of the input device where sensor is connected to. only applicable for I2C.
		   //   fadeouttime indicates the number of seconds for fadeout
		   //
		   // DISPLAY class
		   data: { 
		           "endpoint": int, 
		           "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		           "format": int, 
		           "text": string,
		           "brightness": int
		         }
		   //   endpoint is an index to the list source endpoints:
		   //     ["Manual", "Hardware"]
		   //   if endpoint is Manual
		   //     brightness is a value from 0x00 (completely dark) to 0xFF (full brightness)
		   //       default: 255 (0xFF)
		   //     format is an index to the list of formats
		   //       ["0x00 to 0xFF", "0 to 99", "0.0 to 9.9"]
		   //     text is the characters to display
		   //       default: "23"
		   //   if endpoint is Hardware
		   //     hardware contains the devicename (input IoT Modem device) and sensorname (input device)
		   //       deviceid is the id of the IoT modem device
		   //       devicename is the name of the IoT modem device
		   //       peripheral is the name of the peripheral device (I2C, ADC, 1WIRE, TPROBE)
		   //       sensorname is the name of the input device
		   //       attribute is the attribute of the device to use
		   //       number is the peripheral number of the input device where sensor is connected to
		   //       address is the address of the input device where sensor is connected to. only applicable for I2C.
		   //
		   // SPEAKER class
		   data: { 
		            "endpoint": int, 
		            "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		            "type": int,
		            "values": { "duration": int, "pitch": int, "delay": int }
		         }
		   // TODO: how to send the file
		   //   endpoint is an index to the list source endpoints:
		   //     ["Manual", "Hardware"]
		   //   type is an index to the list of sound types:
		   //     ["midi"]
		   //   values is the parameters for the specified type
		   //     for midi type, values should include duration, pitch, delay
		   //   if endpoint is Manual
		   //     type is the type of sound to play
		   //     midi is the sound/music configuration of the MIDI sound
		   //       duration is the note duration in milliseconds [default: 100]
		   //       pitch is the MIDI note number to use. possible values is from 55-126 [default: 55]
		   //       delay is the time in milliseconds before sound is repeated [default: 100]
		   //       file is the sound/music file to send and play
		   //         name is the name of the sound/music file to send and play
		   //         size is the size of the sound/music file to send and play
		   //   if endpoint is Hardware
		   //     hardware contains the devicename (input IoT Modem device) and sensorname (input I2C device)
		   //       deviceid is the id of the IoT modem device
		   //       devicename is the name of the IoT modem device
		   //       peripheral is the name of the peripheral device (I2C, ADC, 1WIRE, TPROBE)
		   //       sensorname is the name of the input device
		   //       attribute is the attribute of the device to use
		   //       number is the peripheral number of the input device where sensor is connected to
		   //       address is the address of the input device where sensor is connected to. only applicable for I2C.
		   //     type is the type of sound to play
		   //     midi is the sound/music configuration of the MIDI sound
		   //       duration is the note duration in milliseconds [default: 100]
		   //       pitch is the MIDI note number to use. possible values is from 55-126 [default: 55]
		   //       delay is the time in milliseconds before sound is repeated [default: 100]
		   //       file is the sound/music file to send and play
		   //         name is the name of the sound/music file to send and play
		   //         size is the size of the sound/music file to send and play
		   //
		   // TEMPERATURE class
		   data: {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   // POTENTIOMETER class
		   data: {
		           "range": int, 
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj 
		      }
		   //   range is an index to the list of ranges
		   //     ["0-255", "0-99", "0-15", "0-9"]
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   notification appears when mode is NOT continuous
		   //   hardware
		   //     appears when mode is continuous
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string}

		I. GET I2C DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value':
		   // LIGHT class
		     { 
		           "color": {
		               "usage": int,
		               "single": {
		                    "endpoint": int,
		                    "manual": int,
		                    "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		               },
		               "individual": {
		                   "red": {
		                       "endpoint": int,
		                       "manual": int,
		                       "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		                   },
		                   "green": {
		                       "endpoint": int,
		                       "manual": int,
		                       "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		                   },
		                   "blue": {
		                       "endpoint": int,
		                       "manual": int,
		                       "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		                   }
		               }
		           }, 
		           "fadeouttime": int 
		     }
		   //   color usage is an index to the list of color usages:
		   //     ["RGB as color", "RGB as component"]
		   //   single should be used if "RGB as color" is selected for color usage
		   //     manual is an int indicating the 0x00RRGGBB 
		   //   individual should be used if "RGB as component" is selected for color usage
		   //     manual is an int indicating the 0xRR or 0xGG or 0xBB
		   //   endpoint is an index to the list source endpoints:
		   //     ["Manual", "Hardware"]
		   //   if endpoint is Manual
		   //     manual is an integer value of the hex color 0xRRGGBB where each RR (red), GG (green), BB (blue) can be 0x00-0xFF (0-255)
		   //   if endpoint is Hardware
		   //     hardware contains the devicename (input IoT Modem device) and sensorname (input I2C device)
		   //       deviceid is the id of the IoT modem device
		   //       devicename is the name of the IoT modem device
		   //       peripheral is the name of the peripheral device (I2C, ADC, 1WIRE, TPROBE)
		   //       sensorname is the name of the input device
		   //       attribute is the attribute of the device to use
		   //       number is the peripheral number of the input device where sensor is connected to
		   //       address is the address of the input device where sensor is connected to. only applicable for I2C.
		   //   fadeouttime indicates the number of seconds for fadeout
		   //
		   // DISPLAY class
		      { 
		           "endpoint": int, 
		           "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		           "format": int, 
		           "text": string,
		           "brightness": int
		      }
		   //   endpoint is an index to the list source endpoints:
		   //     ["Manual", "Hardware"]
		   //   if endpoint is Manual
		   //     brightness is a value from 0x00 (completely dark) to 0xFF (full brightness)
		   //       default: 255 (0xFF)
		   //     format is an index to the list of formats
		   //       ["0x00 to 0xFF", "0 to 99", "0.0 to 9.9"]
		   //     text is the characters to display
		   //       default: "23"
		   //   if endpoint is Hardware
		   //     hardware contains the devicename (input IoT Modem device) and sensorname (input device)
		   //       deviceid is the id of the IoT modem device
		   //       devicename is the name of the IoT modem device
		   //       peripheral is the name of the peripheral device (I2C, ADC, 1WIRE, TPROBE)
		   //       sensorname is the name of the input device
		   //       attribute is the attribute of the device to use
		   //       number is the peripheral number of the input device where sensor is connected to
		   //       address is the address of the input device where sensor is connected to. only applicable for I2C.
		   //
		   // SPEAKER class
		      { 
		            "endpoint": int, 
		            "hardware": {"devicename": string, "peripheral": string, "sensorname": string, "attribute": string}, 
		            "type": int,
		            "values": { "duration": int, "pitch": int, "delay": int }
		      }
		   // TODO: how to send the file
		   //   endpoint is an index to the list source endpoints:
		   //     ["Manual", "Hardware"]
		   //   type is an index to the list of sound types:
		   //     ["midi"]
		   //   values is the parameters for the specified type
		   //     for midi type, values should include duration, pitch, delay
		   //   if endpoint is Manual
		   //     type is the type of sound to play
		   //     midi is the sound/music configuration of the MIDI sound
		   //       duration is the note duration in milliseconds [default: 100]
		   //       pitch is the MIDI note number to use. possible values is from 55-126 [default: 55]
		   //       delay is the time in milliseconds before sound is repeated [default: 100]
		   //       file is the sound/music file to send and play
		   //         name is the name of the sound/music file to send and play
		   //         size is the size of the sound/music file to send and play
		   //   if endpoint is Hardware
		   //     hardware contains the devicename (input IoT Modem device) and sensorname (input I2C device)
		   //       deviceid is the id of the IoT modem device
		   //       devicename is the name of the IoT modem device
		   //       peripheral is the name of the peripheral device (I2C, ADC, 1WIRE, TPROBE)
		   //       sensorname is the name of the input device
		   //       attribute is the attribute of the device to use
		   //       number is the peripheral number of the input device where sensor is connected to
		   //       address is the address of the input device where sensor is connected to. only applicable for I2C.
		   //     type is the type of sound to play
		   //     midi is the sound/music configuration of the MIDI sound
		   //       duration is the note duration in milliseconds [default: 100]
		   //       pitch is the MIDI note number to use. possible values is from 55-126 [default: 55]
		   //       delay is the time in milliseconds before sound is repeated [default: 100]
		   //       file is the sound/music file to send and play
		   //         name is the name of the sound/music file to send and play
		   //         size is the size of the sound/music file to send and play
		   //
		   // TEMPERATURE class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   // POTENTIOMETER class
		      {
		           "range": int,
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj 
		      }
		   //   range is an index to the list of ranges
		   //     ["0-255", "0-99", "0-15", "0-9"]
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   notification appears when mode is NOT continuous
		   //   hardware
		   //     appears when mode is continuous

		   { 'status': 'NG', 'message': string}

		J. ENABLE/DISABLE I2C DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		K. GET I2C DEVICE READINGS
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float} } }
		   { 'status': 'NG', 'message': string }

		L. GET I2C DEVICE READINGS DATASET
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'sensor_readings': {'value': float, 'subclass': {'value': float} }} ] }
		   { 'status': 'NG', 'message': string }

		M. DELETE I2C DEVICE READINGS
		-  Request:
		   DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


	5. Device access and control APIs (ADC)


		A. ADD ADC DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'manufacturer': string, 'model': string, 'class': string, 'type': string, 'units': [], 'formats': [], 'attributes': []}
		   // Note: multiclass sensor data requires adding of {'subclass': string, 'subattributes': []}
		   // call GET SUPPORTED SENSOR DEVICES to get the JSON data contained here: https://ft900-iot-portal.s3.amazonaws.com/supported_sensor_devices.json
		   // registering a sensor using an already used sensorname returns HTTP_409_CONFLICT with 'Sensor name is already taken'
		   // Note: The device class defines if device type is INPUT or OUTPUT
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		B. DELETE ADC DEVICE
		-  Request:
		   DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}

		C. GET ADC DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be ANEMOMETER

		D. GET ADC DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/adc/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		E. GET ALL ADC DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/adc/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		F. SET ADC DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data:
		   // ANENOMOMETER class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj 
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   notification appears when mode is NOT continuous
		   //   hardware
		   //     appears when mode is continuous
		   //
		   // BATTERY class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   // FLUID class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   -  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		G. GET ADC DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value':
		   // ANENOMOMETER class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj 
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   notification appears when mode is NOT continuous
		   //   hardware
		   //     appears when mode is continuous
		   //
		   // BATTERY class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   // FLUID class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   { 'status': 'NG', 'message': string}

		H. ENABLE/DISABLE ADC DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		I. GET ADC DEVICE READINGS
		-  Request:
		   GET /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float} } }
		   { 'status': 'NG', 'message': string }

		J. GET ADC DEVICE READINGS DATASET
		-  Request:
		   GET /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'sensor_readings': {'value': float, 'subclass': {'value': float} }} ] }
		   { 'status': 'NG', 'message': string }

		K. DELETE ADC DEVICE READINGS
		-  Request:
		   DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		L. GET ADC VOLTAGE
		-  Request:
		   GET /devices/device/DEVICENAME/adc/voltage
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // note that no adc NUMBER is included because this applies to all 2 adcs
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
		   { 'status': 'NG', 'message': string }
		   // voltage is an index of the value in the list of voltages
		   //   ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]

		M. SET ADC VOLTAGE
		-  Request:
		   POST /devices/device/DEVICENAME/adc/voltage
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'voltage': int }
		   // note that no adc NUMBER is included because this applies to all 2 adcs
		   // voltage is an index of the value in the list of voltages
		   //   ["-5/+5V Range", "-10/+10V Range", "0/10V Range"]
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


	6. Device access and control APIs (1WIRE)


		A. ADD 1WIRE DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'manufacturer': string, 'model': string, 'class': string, 'type': string, 'units': [], 'formats': [], 'attributes': []}
		   // Note: multiclass sensor data requires adding of {'subclass': string, 'subattributes': []}
		   // call GET SUPPORTED SENSOR DEVICES to get the JSON data contained here: https://ft900-iot-portal.s3.amazonaws.com/supported_sensor_devices.json
		   // registering a sensor using an already used sensorname returns HTTP_409_CONFLICT with 'Sensor name is already taken'
		   // Note: The device class defines if device type is INPUT or OUTPUT
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		B. DELETE 1WIRE DEVICE
		-  Request:
		   DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		C. GET 1WIRE DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be TEMPERATURE

		D. GET 1WIRE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		E. GET ALL 1WIRE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		F. SET 1WIRE DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   //
		   // TEMPERATURE class
		   data: {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		G. GET 1WIRE DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value':
		   //
		   // TEMPERATURE class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //
		   { 'status': 'NG', 'message': string}

		H. ENABLE/DISABLE 1WIRE DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		I. GET 1WIRE DEVICE READINGS
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float} } }
		   { 'status': 'NG', 'message': string }

		J. GET 1WIRE DEVICE READINGS DATASET
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'sensor_readings': {'value': float, 'subclass': {'value': float} }} ] }
		   { 'status': 'NG', 'message': string }

		K. DELETE 1WIRE DEVICE READINGS
		-  Request:
		   DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


	7. Device access and control APIs (TPROBE)


		A. ADD TPROBE DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'manufacturer': string, 'model': string, 'class': string, 'type': string, 'units': [], 'formats': [], 'attributes': []}
		   // Note: multiclass sensor data requires adding of {'subclass': string, 'subattributes': []}
		   // call GET SUPPORTED SENSOR DEVICES to get the JSON data contained here: https://ft900-iot-portal.s3.amazonaws.com/supported_sensor_devices.json
		   // registering a sensor using an already used sensorname returns HTTP_409_CONFLICT with 'Sensor name is already taken'
		   // Note: The device class defines if device type is INPUT or OUTPUT
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		B. DELETE TPROBE DEVICE
		-  Request:
		   DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		C. GET TPROBE DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be TEMPERATURE with subclass of HUMIDITY

		D. GET TPROBE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		E. GET ALL TPROBE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': string, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		F. SET TPROBE DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data:
		   //
		   // TEMPERATURE class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		           
		           // HUMIDITY class
		           "subattributes": {
		               "mode": int, 
		               "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		               "alert": {"type": int, 'period': int}, 
		               "hardware": {"devicename": string}, 
		               "notification": json_obj,
		           }
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //   subattributes is optional only appears if the device class has a subclass
		   //
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		G. GET TPROBE DEVICE PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': 
		   //
		   // TEMPERATURE class
		      {
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string}, 
		           "notification": json_obj,
		           
		           // HUMIDITY class
		           "subattributes": {
		               "mode": int, 
		               "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		               "alert": {"type": int, 'period': int}, 
		               "hardware": {"devicename": string}, 
		               "notification": json_obj,
		           }
		      }
		   //   mode is an index to the list of modes
		   //     ["Single Threshold", "Dual Threshold", "Continuous"]
		   //   threshold
		   //     if Single Threshold:
		   //       value is used
		   //     if Dual Threshold:
		   //       min and max are used
		   //   activate is an index to the list of activates
		   //     ["Out of range", "Within range"]
		   //   alert type is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   //   alert period is the time in milliseconds for the alert when alert type points to Continuously
		   //   notification refers to the the same notification settings in GPIO
		   //   hardware
		   //     appears when mode is continuous
		   //   subattributes is optional only appears if the device class has a subclass
		   //
		   { 'status': 'NG', 'message': string}

		H. ENABLE/DISABLE TPROBE DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		I. GET TPROBE DEVICE READINGS
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float} } }
		   { 'status': 'NG', 'message': string }

		J. GET TPROBE DEVICE READINGS DATASET
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensor_readings': [{'timestamp': int, 'sensor_readings': {'value': float, 'subclass': {'value': float} }} ] }
		   { 'status': 'NG', 'message': string }

		K. DELETE TPROBE DEVICE READINGS
		-  Request:
		   DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


	8. Device transaction recording APIs

		A. GET HISTORIES
		-  Request:
		   GET /devices/histories
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
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
		   // List of topics: 
		      "get_status", 
		      "set_status", 
		      "get_settings", 
		      "set_settings",
		      "get_uarts", 
		      "get_uart_prop", 
		      "set_uart_prop", 
		      "enable_uart",
		      "get_gpios", 
		      "get_gpio_prop", 
		      "set_gpio_prop", 
		      "enable_gpio",
		      "get_gpio_voltage", 
		      "set_gpio_voltage", 
		      "get_i2c_devs", 
		      "enable_i2c_dev",
		      "get_i2c_dev_prop", 
		      "set_i2c_dev_prop", 
		      "get_adc_devs", 
		      "enable_adc_dev",
		      "get_adc_dev_prop", 
		      "set_adc_dev_prop", 
		      "get_adc_voltage", 
		      "set_adc_voltage",
		      "get_1wire_devs", 
		      "enable_1wire_dev",
		      "get_1wire_dev_prop", 
		      "set_1wire_dev_prop", 
		      "get_tprobe_devs", 
		      "enable_tprobe_dev",
		      "get_tprobe_dev_prop", 
		      "get_tprobe_dev_prop", 
		      "get_devs", 
		      "recv_notification", 
		      "trigger_notification",
		      "status_notification", 
		      "rcv_sensor_reading", 
		      "req_sensor_reading",
		      "sensor_reading", 
		      "rcv_configuration", 
		      "req_configuration",
		      "del_configuration", 
		      "set_configuration", 
			  
		   // List of directions: "To", "From"
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
		   { 'status': 'NG', 'message': string}

		C. GET MENOS HISTORIES
		-  Request:
		   GET /devices/menos
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'timestamp': string, 'recipient': string, 'messagelen': int, 'type': string, 'source': string, 'sensorname': string, 'condition': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // sensorname and condition are optional (ex. when source is UART/GPIO, then both sensorname and condition are not present

		D. GET MENOS HISTORIES FILTERED
		-  Request:
		   POST /devices/menos
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string }
		   // all data items are optional (when data is empty, that is no filters are set, it is actually equivalent to as GET MENOS HISTORIES)
		   // to filter by device name, include devicename
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'timestamp': string, 'recipient': string, 'messagelen': int, 'type': string, 'source': string, 'sensorname': string, 'condition': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // sensorname and condition are optional (ex. when source is UART/GPIO, then both sensorname and condition are not present


	9. Account subscription and payment APIs

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


	10. Mobile services

		A. REGISTER DEVICE TOKEN
		-  Request:
		   POST /mobile/devicetoken
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'token': jwtEncode(devicetoken, service)}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		-  Details:
		   // devicetoken is the unique device token generated during app installation/reinstallation
		   // service is APNS (IOS) or GCM (ANDROID)
		   How to compute the JWT token using Javascript
		   base64UrlEncodedHeader = urlEncode(base64Encode(JSON.stringify({
		     "alg": "HS256",
		     "typ": "JWT"
		   })));
		   base64UrlEncodedPayload = urlEncode(base64Encode(JSON.stringify({
		     "username": devicetoken,
		     "password": service,
		     "iat": Math.floor(Date.now() / 1000), // epoch time in seconds
		     "exp": iat + 10,                      // expiry in seconds
		   })));
		   base64UrlEncodedSignature = urlEncode(CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(
		     base64UrlEncode(header) + "." + base64UrlEncode(payload),
		     SECRET_KEY                            // message me for the value of the secret key
		     )));
		   JWT = base64UrlEncodedHeader + "." base64UrlEncodedPayload + "." + base64UrlEncodedSignature
		   Double check your results here: https://jwt.io/


	11. Supported devices

		A. GET SUPPORTED I2C DEVICES (obsoloted: use GET SUPPORTED SENSOR DEVICES instead)
		-  Request:
		   GET /others/i2cdevices
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'document': json_object }
		   {'status': 'NG', 'message': string }
		   // document refers to the JSON document file uploaded in AWS S3
		   // the file has been temporarily made public at https://ft900-iot-portal.s3.amazonaws.com/supported_i2c_devices.json
		   // this API provides access to the contents of the JSON file
		   // WARNING: This API is obsoleted. Please use GET SUPPORTED SENSOR DEVICES instead.

		B. GET SUPPORTED SENSOR DEVICES
		-  Request:
		   GET /others/sensordevices
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'document': json_object }
		   {'status': 'NG', 'message': string }
		   // document refers to the JSON document file uploaded in AWS S3
		   // the file has been temporarily made public at https://ft900-iot-portal.s3.amazonaws.com/supported_sensor_devices.json
		   // this API provides access to the contents of the JSON file


	12. Others

		A. SEND FEEDBACK
		-  Request:
		   POST /others/feedback
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'feedback': string, 'rating': int, 'contactme': boolean, 'recipient': string }
		   // recipient is temporary for testing purposes only
		-  Response:
		   {'status': 'OK', 'message': string }
		   {'status': 'NG', 'message': string }

		B. GET FAQS
		-  Request:
		   GET /others/faqs
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'url': {'faqs': string} }
		   {'status': 'NG', 'message': string }

		C. GET ABOUT
		-  Request:
		   GET /others/about
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'url': {'terms': string, 'privacy': string, 'license': string} }
		   {'status': 'NG', 'message': string }


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
		6. [TODO] ECC certificates and UUID stored in 3rd-party ATECC hardware chip 

Upon connection, each device subscribes to its own dedicated MQTT topic using its device identification (DEVICEID/#).
As a result, it will only be receiving subtopics under DEVICEID topic solely for the device.
Each device publishes to its own assigned MQTT topic using its device identification and server (server/DEVICEID/#)
Subscribing or publishing to other MQTT topics will fail as the message broker restricts the permissions of topic for each device.

	MQTT device connection details:

		1.  MQTT host: richmondu.com
		2.  MQTT port: 8883
		3.  MQTT clientid: DEVICEID
		4.  MQTT username: UUID
		5.  MQTT password: SERIALNUMBER
		6.  TLS CA certificate
		7.  TLS client certificates
		8.  TLS client private key
		9.  MQTT subscribe topic: DEVICEID/#
		10. MQTT publish topic: server/DEVICEID/#

Below is a summary and a detailed list of the subtopics the device will receive and publish.


SUMMARY:

	1. STATUS
		A. GET STATUS                get_status
		   - starting, running, restart, restarting, stop, stopping, stopped, start

		B. SET STATUS                set_status
		   - restart, stop, start

	2. SETTINGS
		A. GET SETTINGS              get_settings
		   - sensorrate (can add more settings in the future)

		B. SET SETTINGS              set_settings
		   - sensorrate (can add more settings in the future)

	2. UART
		A. GET UARTS                 get_uarts
		   - gets enabled status of the UART

		B. GET UART PROPERTIES       get_uart_prop
		   - gets structure data with correct value mapping (due to unexposed values)

		C. SET UART PROPERTIES       set_uart_prop
		   - sets structure data with correct value mapping
		   - calls uart_close(), uart_soft_reset(), uart_open()
		     * uart_soft_reset is needed to prevent distorted text when changing databits or parity
		     * interrupt_attach, uart_enable_interrupt and uart_enable_interrupts_globally needs to be called because uart_soft_reset clears the interrupt

		D. ENABLE/DISABLE UART       enable_uart
		   - ENABLE: calls uart_open()
		     * interrupt_attach, uart_enable_interrupt and uart_enable_interrupts_globally needs to be called because uart_soft_reset clears the interrupt
		   - DISABLE: calls uart_close() and uart_soft_reset()
		     * uart_soft_reset is needed to prevent distorted text when changing databits or parity

		E. UART AT Commands
		   - AT+M (Mobile)
		           AT+M
		           AT+M+6512345678
		           AT+M++Hello World
		           AT+M+6512345678+Hello World
		   - AT+E (Email)
		           AT+E
		           AT+E+email@xyz.com
		           AT+E++Hello World
		           AT+E+email@xyz.com+Hello World
		   - AT+N (Notification)
		   - AT+O (mOdem)
		           AT+O
		           AT+O+DEVICEID
		           AT+O++Hello World
		           AT+O+DEVICEID+Hello World
		   - AT+S (Storage)
		   - AT+D (Default)
		           AT+D
		   - Others

	3. GPIO
		A. GET GPIOS                    get_gpios
		   - gets enabled, direction and status of all 4 GPIO pins

		B. GET GPIO PROPERTIES       get_gpio_prop
		C. SET GPIO PROPERTIES       set_gpio_prop
		   - if input pin, disable OUTPUT ENABLE pin
		   - else if output pin, enable OUTPUT ENABLE pin
		     and set output pin to inactive state (opposite of specified polarity)

		D. ENABLE/DISABLE GPIO          enable_gpio
		   - ENABLE:
		     If INPUT
		     - calls gpio_read() the creates a timer or interrupt
		       timer if already in activation mode
		       interrupt to wait to get to activation mode before create timer
		     Else OUTPUT
		     - if Level or Pulse mode, call gpio_write() and delayms()
		       else if Clock, create a task that calls gpio_write() and delayms()
		   - DISABLE:
		     If INPUT
		     - deletes timer and or interrupt
		     Else OUTPUT
		     - if Clock mode, delete the task

		E. GET GPIO VOLTAGE             get_gpio_voltage
		F. SET GPIO VOLTAGE             set_gpio_voltage
		   - 3.3v: gpio_write(16, 0), gpio_write(17, 1)
		   - 5v:   gpio_write(16, 1), gpio_write(17, 0)

	4. I2C
		A. GET I2C DEVICES              get_i2c_devs
		B. GET I2C DEVICE PROPERTIES    get_i2c_dev_prop
		C. SET I2C DEVICE PROPERTIES    set_i2c_dev_prop
		D. ENABLE/DISABLE I2C DEVICE    enable_i2c_dev

	5. ADC
		A. GET ADC DEVICES              get_adc_devs
		B. GET ADC DEVICE PROPERTIES    get_adc_dev_prop
		C. SET ADC DEVICE PROPERTIES    set_adc_dev_prop
		D. ENABLE/DISABLE ADC DEVICE    enable_adc_dev
		E. GET ADC VOLTAGE              get_adc_voltage
		F. SET ADC VOLTAGE              set_adc_voltage

	6. 1WIRE
		A. GET 1WIRE DEVICES            get_1wire_devs
		B. GET 1WIRE DEVICE PROPERTIES  get_1wire_dev_prop
		C. SET 1WIRE DEVICE PROPERTIES  set_1wire_dev_prop
		D. ENABLE/DISABLE 1WIRE DEVICE  enable_1wire_dev

	7. TPROBE
		A. GET TPROBE DEVICES           get_tprobe_devs
		B. GET TPROBE DEVICE PROPERTIES get_tprobe_dev_prop
		C. SET TPROBE DEVICE PROPERTIES set_tprobe_dev_prop
		D. ENABLE/DISABLE TPROBE DEVICE enable_tprobe_dev

	8. PERIPHERALS
		A. GET PERIPHERAL DEVICES       get_devs

	9. Notifications
		A. SEND NOTIFICATION            trigger_notification
		B. STATUS NOTIFICATION          status_notification
		C. RECV NOTIFICATION            recv_notification

	10. Sensor Reading
		A. RECEIVE SENSOR READING       rcv_sensor_reading
		B. REQUEST SENSOR READING       req_sensor_reading
		C. PUBLISH SENSOR READING       sensor_reading

	11. Configurations
		A. RECEIVE CONFIGURATION        rcv_configuration
		B. REQUEST CONFIGURATION        req_configuration
		C. DELETE CONFIGURATION         del_configuration


DETAILED:

	1. STATUS

		A. GET STATUS
		-  Receive:
		   topic: DEVICEID/get_status
		-  Publish:
		   topic: server/DEVICEID/get_status
		   payload: { 'value': {'status': int, 'version': string} }
		   // version is the firmware version in the string format of "major_version.minor_version"
		   // status is an index of the value in the list of statuses
		   //   ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]
		   
		B. SET STATUS
		-  Receive:
		   topic: DEVICEID/set_status
		   payload: { 'status': int }
		   // status is an index of the value in the list of statuses
		   //   ["starting", "running", "restart", "restarting", "stop", "stopping", "stopped", "start"]
		-  Publish:
		   topic: server/DEVICEID/set_status
		   payload: { 'value': {'status': int} }


	2. UART

		A. GET UARTS
		-  Receive:
		   topic: DEVICEID/get_uarts
		-  Publish:
		   topic: server/DEVICEID/get_uarts
		   payload: { 
		     'value': { 
		       'uarts': [ 
		           {'enabled': int}, 
		       ]
		     }
		   }
		   // enable is an int indicating if disabled (0) or enabled (1)

		B. GET UART PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_uart_prop
		-  Publish:
		   topic: server/DEVICEID/get_uart_prop
		   payload: { 
		     'value': { 
		       'baudrate': int, 
		       'parity': int, 
		       'flowcontrol': int 
		       'stopbits': int, 
		       'databits': int, 
		     } 
		   }
		   // baudrate is an index of the value in the list of baudrates
		   //   ft900_uart_simple.h: UART_DIVIDER_XXX
		   //   ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
		   //      default = 7 (19200)
		   // parity is an index of the value in the list of parities
		   //   ft900_uart_simple.h: uart_parity_t enum
		   //   ["None", "Odd", "Even"]
		   //      default = 0 (None)
		   // flowcontrol is an index of the value in the list of flowcontrols
		   //   ["None", "Rts/Cts", "Xon/Xoff"]
		   //      default = 0 (None)
		   // stopbits is an index of the value in the list of stopbits
		   //   ft900_uart_simple.h: uart_stop_bits_t enum
		   //   ["1", "2"]
		   //      default = 0 (1)
		   // databits is an index of the value in the list of databits
		   //   ft900_uart_simple.h: uart_data_bits_t enum
		   //   ["7", "8"]
		   //      default = 1 (8)

		C. SET UART PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_uart_prop
		   payload: { 
		       'baudrate': int, 
		       'parity': int, 
		       'flowcontrol': int 
		       'stopbits': int, 
		       'databits': int, 
		   }
		   // baudrate is an index of the value in the list of baudrates
		   //   ft900_uart_simple.h: UART_DIVIDER_XXX
		   //   ["110", "150", "300", "1200", "2400", "4800", "9600", "19200", "31250", "38400", "57600", "115200", "230400", "460800", "921600", "1000000"]
		   //      default = 7 (19200)
		   // parity is an index of the value in the list of parities
		   //   ft900_uart_simple.h: uart_parity_t enum
		   //   ["None", "Odd", "Even"]
		   //      default = 0 (None)
		   // flowcontrol is an index of the value in the list of flowcontrols
		   //   ["None", "Rts/Cts", "Xon/Xoff"]
		   //      default = 0 (None)
		   // stopbits is an index of the value in the list of stopbits
		   //   ft900_uart_simple.h: uart_stop_bits_t enum
		   //   ["1", "2"]
		   //      default = 0 (1)
		   // databits is an index of the value in the list of databits
		   //   ft900_uart_simple.h: uart_data_bits_t enum
		   //   ["7", "8"]
		   //      default = 1 (8)
		-  Publish:
		   topic: server/DEVICEID/set_uart_prop
		   payload: {}

		D. ENABLE/DISABLE UART
		-  Receive:
		   topic: DEVICEID/enable_uart
		   payload: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_uart
		   payload: {}


	3. GPIO

		A. GET GPIOS
		-  Receive:
		   topic: DEVICEID/get_gpios
		-  Publish:
		   topic: server/DEVICEID/get_gpios
		   payload: { 
		     'value': { 
		       'voltage': int, 
		       'gpios': [ 
		           {'enabled': int, 'direction': int, 'status': int}, 
		           {'enabled': int, 'direction': int, 'status': int}, 
		           {'enabled': int, 'direction': int, 'status': int}, 
		           {'enabled': int, 'direction': int, 'status': int} 
		       ]
		     }
		   }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]
		   // enable is an int indicating if disabled (0) or enabled (1)
		   // direction is an index of the value in the list of directions
		   //   ["Input", "Output"]
		   // status is an index of the value in the list of directions
		   //   ["Low", "High"]

		B. GET GPIO PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_gpio_prop
		   payload: { 'number': int }
		-  Publish:
		   topic: server/DEVICEID/get_gpio_prop
		   payload: { 
		     'value': {
		       'direction': int, 
		       'mode': int, 
		       'alert': int, 
		       'alertperiod': int, 
		       'polarity': int, 
		       'width': int, 
		       'mark': int, 
		       'space': int
		       'count': int
		     } 
		   }
		   // direction is an index of the value in the list of directions
		   //     ft900_gpio.h: pad_dir_t
		   //     ["Input", "Output"]
		   // mode is an index of the value in the list of modes
		   //     ft900_gpio.h
		   //     direction == "Input"
		   //       ["High Level", "Low Level", "High Edge", "Low Edge"]
		   //     direction == "Output"
		   //       ["Level", "Clock", "Pulse"]
		   // alert is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   // alert is an optional and is valid only when direction points to Input
		   // alertperiod is optional and is valid only if alert points to Continuously
		   // polarity is an index of the value in the list of polarities
		   //     ft900_gpio.h
		   //     direction == "Output"
		   //       ["Negative", "Positive"]
		   // polarity is optional and is valid only when direction points to Output
		   // width is optional and is valid only when direction points to Output and mode points to Pulse (width (ms) should be > 0)
		   // mark is optional and is valid only when direction points to Output and mode points to Clock (mark (ms) should be > 0)
		   // space is optional and is valid only when direction points to Output and mode points to Clock (space (ms) should be > 0)
		   // count is optional and is valid only when direction points to Output and mode points to Clock (count should be > 0)

		C. SET GPIO PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_gpio_prop
		   payload: {
		       'direction': int, 
		       'mode': int, 
		       'alert': int, 
		       'alertperiod': int, 
		       'polarity': int, 
		       'width': int, 
		       'mark': int, 
		       'space': int,
		       'count': int,
		       'number': int
		   }
		   // direction is an index of the value in the list of directions
		   //     ft900_gpio.h: pad_dir_t
		   //     ["Input", "Output"]
		   // mode is an index of the value in the list of modes
		   //     ft900_gpio.h
		   //     direction == "Input"
		   //       ["High Level", "Low Level", "High Edge", "Low Edge"]
		   //     direction == "Output"
		   //       ["Level", "Clock", "Pulse"]
		   // alert is an index of the value in the list of alerts
		   //     ["Once", "Continuously"]
		   // alert is an optional and is valid only when direction points to Input
		   // alertperiod is optional and is valid only if alert points to Continuously
		   // polarity is an index of the value in the list of polarities
		   //     ft900_gpio.h
		   //     direction == "Output"
		   //       ["Negative", "Positive"]
		   // polarity is optional and is valid only when direction points to Output
		   // width is optional and is valid only when direction points to Output and mode points to Pulse (width (ms) should be > 0)
		   // mark is optional and is valid only when direction points to Output and mode points to Clock (mark (ms) should be > 0)
		   // space is optional and is valid only when direction points to Output and mode points to Clock (space (ms) should be > 0)
		   // count is optional and is valid only when direction points to Output and mode points to Clock (count should be > 0)
		-  Publish:
		   topic: server/DEVICEID/set_gpio_prop
		   payload: {}

		D. ENABLE/DISABLE GPIO
		-  Receive:
		   topic: DEVICEID/enable_gpio
		   payload: { 'enable': int, 'number': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_gpio
		   payload: {}

		E. GET GPIO VOLTAGE
		-  Receive:
		   topic: DEVICEID/get_gpio_voltage
		-  Publish:
		   topic: server/DEVICEID/get_gpio_voltage
		   payload: { 'value': { 'voltage': int } }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]

		F. SET GPIO VOLTAGE
		-  Receive:
		   topic: DEVICEID/set_gpio_voltage
		   payload: { 'voltage': int }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]
		-  Publish:
		   topic: server/DEVICEID/set_gpio_voltage
		   payload: {}


	4. I2C

		A. GET I2CS
		-  Receive:
		   topic: DEVICEID/get_i2cs
		-  Publish:
		   topic: server/DEVICEID/get_i2cs
		   payload: { 
		     'value': { 
		       'i2cs': [ 
		           {'enabled': int}, 
		           {'enabled': int}, 
		           {'enabled': int}, 
		           {'enabled': int} 
		       ]
		     }
		   }
		   // enable is an int indicating if disabled (0) or enabled (1)

		B. GET I2C DEVICES
		-  Receive:
		   topic: DEVICEID/get_i2c_devs
		-  Publish:
		   topic: server/DEVICEID/get_i2c_devs
		   payload: { 
		     'value': { 
		       'i2cs': [ 
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		           {
		              address: { 'enabled': 0, 'class': 0, 'attributes': {} },
		           },
		       ]
		     }
		   }
		   // enable is an int indicating if disabled (0) or enabled (1)

		C. GET I2C DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_i2c_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_i2c_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET I2C DEVICE PROPERTIES API } 
		   }

		D. SET I2C DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_i2c_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET I2C DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_i2c_dev_prop
		   payload: {}

		E. ENABLE/DISABLE I2C DEVICE
		-  Receive:
		   topic: DEVICEID/enable_i2c_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_i2c
		   payload: {}

		F. ENABLE/DISABLE I2C
		-  Receive:
		   topic: DEVICEID/enable_i2c
		   payload: { 'enable': int, 'number': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_i2c
		   payload: {}


	5. ADC

		A. GET ADC DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_adc_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_adc_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET ADC DEVICE PROPERTIES API } 
		   }

		B. SET ADC DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_adc_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET ADC DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_adc_dev_prop
		   payload: {}

		C. ENABLE/DISABLE ADC DEVICE
		-  Receive:
		   topic: DEVICEID/enable_adc_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_adc_dev
		   payload: {}


	6. 1WIRE

		A. GET 1WIRE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_1wire_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_1wire_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET 1WIRE DEVICE PROPERTIES API } 
		   }

		B. SET 1WIRE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_1wire_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET 1WIRE DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_1wire_dev_prop
		   payload: {}

		C. ENABLE/DISABLE 1WIRE DEVICE
		-  Receive:
		   topic: DEVICEID/enable_1wire_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_1wire_dev
		   payload: {}


	7. TPROBE

		A. GET TPROBE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/get_tprobe_dev_prop
		   payload: { 'number': int, 'address': int }
		-  Publish:
		   topic: server/DEVICEID/get_tprobe_dev_prop
		   payload: { 
		     'value': { TODO:Refer to GET TPROBE DEVICE PROPERTIES API } 
		   }

		B. SET TPROBE DEVICE PROPERTIES
		-  Receive:
		   topic: DEVICEID/set_tprobe_dev_prop
		   payload: { 
		       'number': int, 
		       'address': int, 
		       'class': string, 
		       ...  TODO:Refer to SET TPROBE DEVICE PROPERTIES API ...
		   }
		-  Publish:
		   topic: server/DEVICEID/set_tprobe_dev_prop
		   payload: {}

		C. ENABLE/DISABLE TPROBE DEVICE
		-  Receive:
		   topic: DEVICEID/enable_tprobe_dev
		   payload: { 'enable': int, 'number': int, 'address': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Publish:
		   topic: server/DEVICEID/enable_tprobe_dev
		   payload: {}


	8. Peripherals

		A. GET PERIPHERAL DEVICES    get_devs


	9. Notifications

		A. SEND NOTIFICATION         trigger_notification
		-  Receive:
		   topic: DEVICEID/trigger_notification
		   payload: { "recipient": string, "message": string }
		-  Publish:
		   topic: server/DEVICEID/trigger_notification
		   topic: server/DEVICEID/trigger_notification/uart/MENOS
		   topic: server/DEVICEID/trigger_notification/gpioX/MENOS
		   topic: server/DEVICEID/trigger_notification/i2cX/MENOS
		   // MENOS: mobile, email, notification, modem, storage
		   payload: { "recipient": string, "message": string }

		B. STATUS NOTIFICATION       status_notification
		-  Receive:
		   topic: DEVICEID/status_notification
		   payload: { "status": string }
		   // status is result of the trigger_notification

		C. RECV NOTIFICATION         recv_notification
		-  Receive:
		   topic: DEVICEID/recv_notification
		   payload: { "sender": string, "message": string }
		   // sender is the DEVICEID of the sender device/mOdem


	10. Sensor Reading

		A. RECEIVE SENSOR READING    rcv_sensor_reading
		B. REQUEST SENSOR READING    req_sensor_reading
		C. PUBLISH SENSOR READING    sensor_reading


	11. Configurations

		A. RECEIVE CONFIGURATION     rcv_configuration
		B. REQUEST CONFIGURATION     req_configuration
		C. DELETE CONFIGURATION      del_configuration



UART Notification sequence

  <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/notification_sequence_UART.png" width="1000"/>


GPIO Notification sequence

  <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/notification_sequence_GPIO.png" width="1000"/>


## Demo Setup Documentation

Below contains the 4 demo setups for Embedded World 2020 in Germany. 

All 4 setups can be simulated by the device simulator. 
The device simulator was used to stress test the backend using the web app and was successfully running for 2.5 days over a weekend (Friday night to Monday morning).

  <img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/demo_stress_test.png" width="1000"/>

The 5 device simulators publishes sensor data at rate of 5 seconds interval while the 5 webapps polls the sensor dataset for graphing at 5 seconds interval too.
On the AWS EC2 side, the CPU usage is as follows:

    - X=5 -> ec2 cpu usage 5%  -> tested stable for ~2.5days (weekend test)
    - X=3 -> ec2 cpu usage 7%  -> tested stable for ~12 hours (Monday night test)
    - X=1 -> ec2 cpu usage 15% -> to test stability

  <a href="https://www.youtube.com/watch?v=xkrd0WblCaI"
    target="_blank"><img src="https://github.com/richmondu/libpyiotcloud/blob/master/_images/demo_stress_test.png" 
    alt="Face Pay demo prototype" width="480" border="10" /></a>


Demo setups:

1.  Demo1 - demonstrates <b>sensor graphing</b> and <b>sensor thresholding (w/MENOS triggering)</b> of ADC/Onewire/TProbe sensors

        Dev1
            ADC - QS-FS Wind sensor 1 (Anemometer)
                Dual Threshold
                Threshold: min 0.1, max 99.9, out of range
                Alert: once
                Notification: 
                    Messages: message on activation, message on deactivation
                    Recipients: send email

            Onewire - DS18B20 1 (Temperature)
                Dual Threshold
                Threshold: min 0.1, max 39.9, out of range
                Alert: once
                Notification: 
                    Messages: message on activation, message on deactivation
                    Recipients: send email

            TProbe - Sonoff TH16 (Temperature and Humidity)
                Temperature
                    Single Threshold
                    Threshold: value 39.9
                    Alert: once
                    Notification: 
                        Messages: message on activation, message on deactivation
                        Recipients: send email
                Humidity
                    Single Threshold
                    Threshold: value 99.9
                    Alert: once
                    Notification: 
                        Messages: message on activation, message on deactivation
                        Recipients: send email

2.  Demo2 - demonstrates <b>sensor forwarding</b> from 3 I2C INPUT sensors of 1 device to 1 I2C OUTPUT sensor of another device

        Dev1
            I2C POT 1
                Mode: Continuous
                Hardware: Demo2Dev2
            I2C POT 2
                Mode: Continuous
                Hardware: Demo2Dev2
            I2C POT 3
                Mode: Continuous
                Hardware: Demo2Dev2
            I2C LED 1
                Usage: RGB as component
                R: Demo2Dev2 > I2C > POT 1 > Range
                G: Demo2Dev2 > I2C > POT 2 > Range
                B: Demo2Dev2 > I2C > POT 3 > Range

        Dev 2
            I2C POT 1
                Mode: Continuous
                Hardware: Demo2Dev1
            I2C POT 2
                Mode: Continuous
                Hardware: Demo2Dev1
            I2C POT 3
                Mode: Continuous
                Hardware: Demo2Dev1
            I2C LED 1
                Usage: RGB as component
                R: Demo2Dev1 > I2C > POT 1 > Range
                G: Demo2Dev1 > I2C > POT 2 > Range
                B: Demo2Dev1 > I2C > POT 3 > Range

3.  Demo 3 - demonstrates <b>sensor forwarding</b> from 2 ADC INPUT sensors of 1 device to 2 I2C OUTPUT sensors of another device

        Dev1
            ADC Battery sensor 1
                Mode: Continuous
                Hardware: Demo3Dev2
            ADC Fluid sensor 1
                Mode: Continuous
                Hardware: Demo3Dev2
            I2C DIG2 1
                Endpoint: Hardware
                Hardware: Demo3Dev2 > ADC > Battery sensor 1 > Battery Level
            I2C DIG2 2
                Endpoint: Hardware
                Hardware: Demo3Dev2 > ADC > eTape Fluid sensor 1 > Fluid Level

        Dev2
            ADC Battery sensor 1
                Mode: Continuous
                Hardware: Demo3Dev1
            ADC Fluid sensor 1
                Mode: Continuous
                Hardware: Demo3Dev1
            I2C DIG2 1
                Endpoint: Hardware
                Hardware: Demo3Dev1 > ADC > Battery sensor 1 > Battery Level
            I2C DIG2 2
                Endpoint: Hardware
                Hardware: Demo3Dev1 > ADC > eTape Fluid sensor 1 > Fluid Level

4.  Demo 4 - demonstrates <b>MENOS notification triggering via UART</b>

        Dev1
            UART
                Notification Recipient: Mobile (SMS), Email, Notification (Push Notification)
            Type AT+M
            Type AT+E
            Type AT+N (Requires logging in on Android or IOS mobile app)

