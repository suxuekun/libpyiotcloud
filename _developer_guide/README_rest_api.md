# HTTPS REST API Documentation

This is for the front-end (mobile/web) developers.

The REST APIs are the gateway of the frontend (mobile apps, web app) to the backend (3rd party APIs and services). 
<b>The frontend does NOT directly access any 3rd party APIs and services, it only communicates with the backend REST APIs.</b> 
The frontend does NOT directly access any AWS service, Paypal service or MongoDB database.
The backend communicates with AWS Cognito, Pinpoint, Paypal, MongoDB and all other 3rd party services, that means most of the logic is handled by the backend. 
This makes the frontend abstracted of the complexities and focus on consistent user experience across Android, IOS and the web.

Below contains a summary and a detailed description of all the current REST APIs.
More APIs will be added to support the new requirements.


SUMMARY:

	1. User sign-up/sign-in APIs

		A. SIGN-UP                         - POST   /user/signup
		B. CONFIRM SIGN-UP                 - POST   /user/confirm_signup
		C. RESEND CONFIRMATION CODE        - POST   /user/resend_confirmation_code
		D. FORGOT PASSWORD                 - POST   /user/forgot_password
		E. CONFIRM FORGOT PASSWORD         - POST   /user/confirm_forgot_password
		F. LOGIN                           - POST   /user/login
		G. LOGOUT                          - POST   /user/logout
		H. GET USER INFO                   - GET    /user
		I. UPDATE USER INFO                - POST   /user
		J. DELETE USER                     - DELETE /user
		K. REFRESH USER TOKEN              - POST   /user/token
		L. VERIFY PHONE NUMBER             - POST   /user/verify_phone_number
		M. CONFIRM VERIFY PHONE NUMBER     - POST   /user/confirm_verify_phone_number
		N. CHANGE PASSWORD                 - POST   /user/change_password

		//
		// login via social idp (facebook, google, amazon)
		O. LOGIN IDP STORE CODE            - POST   /user/login/idp/code/ID
		P. LOGIN IDP QUERY CODE            - GET    /user/login/idp/code/ID

		//
		// mfa (multi-factor authentication)
		Q. ENABLE MFA                      - POST   /user/mfa
		R. LOGIN MFA                       - POST   /user/login/mfa

		//
		// organization (members)
		S. GET ORGANIZATIONS               - GET    /user/organizations
		T. SET ACTIVE ORGANIZATION         - POST   /user/organizations
		   all ORG-related APIs below will use the organization that is active

		U. GET ORGANIZATION                - GET    /user/organization
		V. LEAVE ORGANIZATION              - DELETE /user/organization
		W. ACCEPT ORGANIZATION INVITATION  - POST   /user/organization/invitation
		X. DECLINE ORGANIZATION INVITATION - DELETE /user/organization/invitation


	2. Organization management APIs

		all APIs below will use the organization that is active (EXCEPT FOR CREATE ORGANIZATION)

		//
		// organization (owner, users)
		A. CREATE ORGANIZATION             - POST   organization
		B. DELETE ORGANIZATION             - DELETE organization
		C. CREATE/CANCEL INVITATIONS       - POST   organization/invitation
		D. UPDATE/REMOVE MEMBERSHIPS       - POST   organization/membership

		//
		// organization (owner, groups)
		E. GET USER GROUPS                 - GET    organization/groups
		F. CREATE USER GROUP               - POST   organization/groups/group/GROUPNAME
		G. DELETE USER GROUP               - DELETE organization/groups/group/GROUPNAME
		H. GET MEMBERS IN USER GROUP       - GET    organization/groups/group/GROUPNAME/members
		I. UPDATE MEMBERS IN USER GROUP    - POST   organization/groups/group/GROUPNAME/members
		J. ADD MEMBER TO USER GROUP        - POST   organization/groups/group/GROUPNAME/members/member/MEMBERNAME
		K. REMOVE MEMBER FROM USER GROUP   - DELETE organization/groups/group/GROUPNAME/members/member/MEMBERNAME

		//
		// organization (owner, policies)
		L. GET POLICIES                    - GET    organization/policies
		M. GET POLICY                      - GET    organization/policies/policy/POLICYNAME
		N. CREATE/UPDATE POLICY            - POST   organization/policies/policy/POLICYNAME
		O. DELETE POLICY                   - DELETE organization/policies/policy/POLICYNAME
		P. GET POLICIES SETTINGS           - GET    organization/policies/settings
		Q. GET POLICIES IN USER GROUP      - GET    organization/groups/group/GROUPNAME/policies
		R. UPDATE POLICIES IN USER GROUP   - POST   organization/groups/group/GROUPNAME/policies
		S. ADD POLICY TO USER GROUP        - POST   organization/groups/group/GROUPNAME/policies/policy/POLICYNAME
		T. REMOVE POLICY FROM USER GROUP   - DELETE organization/groups/group/GROUPNAME/policies/policy/POLICYNAME


	3. Device registration and management APIs

		A. GET DEVICES                    - GET    /devices
		B. GET DEVICES FILTERED           - GET    /devices/filter/FILTERSTRING
		C. ADD DEVICE                     - POST   /devices/device/DEVICENAME
		D. DELETE DEVICE                  - DELETE /devices/device/DEVICENAME
		E. UPDATE DEVICE NAME             - POST   /devices/device/DEVICENAME/name
		F. GET DEVICE                     - GET    /devices/device/DEVICENAME
		G. GET DEVICE DESCRIPTOR          - GET    /devices/device/DEVICENAME/descriptor

		//
		// location
		H. GET DEVICES LOCATION           - GET    /devices/location
		I. SET DEVICES LOCATION           - POST   /devices/location
		J. DELETE DEVICES LOCATION        - DELETE /devices/location
		K. GET DEVICE LOCATION            - GET    /devices/device/DEVICENAME/location
		L. SET DEVICE LOCATION            - POST   /devices/device/DEVICENAME/location
		M. DELETE DEVICE LOCATION         - DELETE /devices/device/DEVICENAME/location

		//
		// ota firmware update
		https://github.com/richmondu/libpyiotcloud/blob/dev/_images/ota_firmware_update_sequence_diagram.png
		N. UPDATE FIRMWARE                - POST   /devices/device/DEVICENAME/firmware
		O. UPDATE FIRMWARES               - POST   /devices/firmware
		P. GET OTA STATUS                 - GET    /devices/device/DEVICENAME/ota
		Q. GET OTA STATUSES               - GET    /devices/ota

		//
		// device-sensor hierarchy tree
		R. GET DEVICE HIERARCHY TREE               - GET    /devices/device/DEVICENAME/hierarchy
		S. GET DEVICE HIERARCHY TREE (WITH STATUS) - POST   /devices/device/DEVICENAME/hierarchy

		//
		// device-sensor data
		T. DOWNLOAD DEVICE SENSOR DATA    - POST   /devices/device/DEVICENAME/sensordata
		U. CLEAR DEVICE SENSOR DATA       - DELETE /devices/device/DEVICENAME/sensordata


	4. Device group registration and management APIs

		A. GET DEVICE GROUPS              - GET    /devicegroups
		B. ADD DEVICE GROUP               - POST   /devicegroups/group/DEVICEGROUPNAME
		C. REMOVE DEVICE GROUP            - DELETE /devicegroups/group/DEVICEGROUPNAME
		D. GET DEVICE GROUP               - GET    /devicegroups/group/DEVICEGROUPNAME
		E. GET DEVICE GROUP DETAILED      - GET    /devicegroups/group/DEVICEGROUPNAME/devices
		F. UPDATE DEVICE GROUP NAME       - POST   /devicegroups/group/DEVICEGROUPNAME/name
		G. ADD DEVICE TO GROUP            - POST   /devicegroups/group/DEVICEGROUPNAME/device/DEVICENAME
		H. REMOVE DEVICE FROM GROUP       - DELETE /devicegroups/group/DEVICEGROUPNAME/device/DEVICENAME
		I. SET DEVICES IN DEVICE GROUP    - POST   /devicegroups/group/DEVICEGROUPNAME/devices
		J. GET UNGROUPED DEVICES          - GET    /devicegroups/ungrouped
		K. GET DEVICE GROUPS & UNGROUPED DEVICES   - GET    /devicegroups/mixed

		//
		// location
		L. GET DEVICE GROUP LOCATION      - GET    /devicegroups/group/DEVICEGROUPNAME/location
		M. SET DEVICE GROUP LOCATION      - POST   /devicegroups/group/DEVICEGROUPNAME/location
		N. DELETE DEVICE GROUP LOCATION   - DELETE /devicegroups/group/DEVICEGROUPNAME/location

		//
		// ota firmware update
		O. GET DEVICE GROUP OTA STATUSES  - GET    /devicegroups/group/DEVICEGROUPNAME/ota


	5. Device access and control APIs (LDSBUS)

		A. GET LDS BUS                    - GET    /devices/device/DEVICENAME/ldsbus/PORT
		B. DELETE LDS BUS                 - DELETE /devices/device/DEVICENAME/ldsbus/PORT
		C. SCAN LDS BUS                   - POST   /devices/device/DEVICENAME/ldsbus/PORT

		D. GET LDS BUS LDSUS              - GET    /devices/device/DEVICENAME/ldsbus/PORT/ldsus
		E. GET LDS BUS SENSORS            - GET    /devices/device/DEVICENAME/ldsbus/PORT/sensors
		F. GET LDS BUS ACTUATORS          - GET    /devices/device/DEVICENAME/ldsbus/PORT/actuators

		G. CHANGE LDSU NAME               - POST   /devices/device/DEVICENAME/ldsu/LDSUUUID/name
		H. IDENTIFY LDSU                  - POST   /devices/device/DEVICENAME/ldsu/LDSUUUID/identify

		I. GET LDSU                       - GET    /devices/device/DEVICENAME/ldsu/LDSUUUID
		J. DELETE LDSU                    - DELETE /devices/device/DEVICENAME/ldsu/LDSUUUID

		//
		// LDSU DEVICE refers to SENSOR or ACTUATOR
		K. SET LDSU DEVICE PROPERTIES     - POST   /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
		L. GET LDSU DEVICE PROPERTIES     - GET    /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
		M. DELETE LDSU DEVICE PROPERTIES  - DELETE /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties

		N. ENABLE/DISABLE LDSU DEVICE     - POST   /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/enable
		O. CHANGE LDSU DEVICE NAME        - POST   /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/name

		//
		// LDSU DEVICE SENSOR READINGS
		P. GET LDSU SENSOR READINGS       - GET    /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/readings


	6. Device access and control APIs (STATUS, UART, GPIO)

		//
		// status
		A. GET STATUS                     - GET    /devices/device/DEVICENAME/status
		B. GET STATUSES                   - GET    /devices/status
		C. SET STATUS                     - POST   /devices/device/DEVICENAME/status

		//
		// settings
		D. GET SETTINGS                   - GET    /devices/device/DEVICENAME/settings
		E. SET SETTINGS                   - POST   /devices/device/DEVICENAME/settings

		//
		// uart
		F. GET UARTS                      - GET    /devices/device/DEVICENAME/uarts
		G. GET UART PROPERTIES            - GET    /devices/device/DEVICENAME/uart/properties
		H. SET UART PROPERTIES            - POST   /devices/device/DEVICENAME/uart/properties
		I. ENABLE/DISABLE UART            - POST   /devices/device/DEVICENAME/uart/enable

		//
		// gpio
		J. GET GPIOS                      - GET    /devices/device/DEVICENAME/gpios
		K. GET GPIO PROPERTIES            - GET    /devices/device/DEVICENAME/gpio/NUMBER/properties
		L. SET GPIO PROPERTIES            - POST   /devices/device/DEVICENAME/gpio/NUMBER/properties
		M. ENABLE/DISABLE GPIO            - POST   /devices/device/DEVICENAME/gpio/NUMBER/enable
		N. GET GPIO VOLTAGE               - GET    /devices/device/DEVICENAME/gpio/voltage
		O. SET GPIO VOLTAGE               - POST   /devices/device/DEVICENAME/gpio/voltage
		   (NUMBER can be 1-4 only and corresponds to GPIO1,GPIO2,GPIO3,GPIO4)

		//
		// sensor properties
		P. DELETE PERIPHERAL SENSOR PROPERTIES             - DELETE /devices/device/DEVICENAME/sensors/properties


	7. Device access and control APIs (I2C)

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


	8. Device access and control APIs (ADC)

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


	9. Device access and control APIs (1WIRE)

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


	10. Device access and control APIs (TPROBE)

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


	11. Device sensor dashboarding

		A. GET SENSOR READINGS DATASET FILTERED - POST   /devices/sensors/readings/dataset
		B. DELETE SENSOR READINGS DATASET       - DELETE /devices/sensors/readings/dataset


	12. Device transaction recording APIs

		A. GET HISTORIES                  - GET    /devices/histories
		B. GET HISTORIES FILTERED         - POST   /devices/histories
		   (filter by device name, direction, topic, date start, date end)

		C. GET MENOS HISTORIES            - GET    /devices/menos
		D. GET MENOS HISTORIES FILTERED   - POST   /devices/menos


	13. Account subscription and payment APIs

		A. GET SUBSCRIPTION               - GET    /account/subscription
		B. PAYPAL SETUP                   - POST   /account/payment/paypalsetup
		C. PAYPAL STORE PAYERID           - POST   /account/payment/paypalpayerid/PAYMENTID
		D. PAYPAL EXECUTE                 - POST   /account/payment/paypalexecute/PAYMENTID
		E. GET PAYPAL TRANSACTIONS        - GET    /account/payment/paypal


	14. Mobile services

		A. REGISTER DEVICE TOKEN          - POST   /mobile/devicetoken


	15. Supported devices and firmware updates

		A. GET SUPPORTED SENSOR DEVICES   - GET    /others/sensordevices
		B. GET DEVICE FIRMWARE UPDATES    - GET    /others/firmwareupdates


	16. Others

		A. SEND FEEDBACK                  - POST   /others/feedback
		B. GET FAQS                       - GET    /others/faqs
		C. GET ABOUT                      - GET    /others/about


	17. OTA Firmware Update

		A. DOWNLOAD FIRMWARE              - GET    /firmware/DEVICE/FILENAME
		   (WARNING: This API is to be called by ESP device, not by web/mobile apps)


	18. HTTP error codes

		A. HTTP_400_BAD_REQUEST           - Invalid input
		B. HTTP_401_UNAUTHORIZED          - Invalid password or invalid/expired token
		C. HTTP_404_NOT_FOUND             - User or device not found
		D. HTTP_409_CONFLICT              - User or device or device group already exist
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
		   // phone number must be unique for all users (since LOGIN via phone number is now supported)
		   // name can be 1 or multiple words
		   // password length must be atleast 8 characters minimum 
		   // pasword must contain uppercase character, lowercase character, special character and a number
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
		   //
		   // Resend OTP 
		   //   To resend OTP for CONFIRM SIGN-UP page, use RESEND CONFIRMATION CODE api
		   //   To resend OTP for CONFIRM FORGOT PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for CONFIRM VERIFY PHONE NUMBER page, use VERIFY PHONE NUMBER api
		   //   To resend OTP for USER LOCKOUT RESET PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for LOGIN MFA page is NOT possible with Cognito
		   //
		   // There is no lockout due for invalid OTP. Lockout is only for invalid password

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
		   // password must conform to the password requirements. refer to SIGNUP api
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
		   //
		   // Resend OTP 
		   //   To resend OTP for CONFIRM SIGN-UP page, use RESEND CONFIRMATION CODE api
		   //   To resend OTP for CONFIRM FORGOT PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for CONFIRM VERIFY PHONE NUMBER page, use VERIFY PHONE NUMBER api
		   //   To resend OTP for USER LOCKOUT RESET PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for LOGIN MFA page is NOT possible with Cognito
		   //
		   // There is no lockout due for invalid OTP. Lockout is only for invalid password
		   
		F. LOGIN
		-  Request:
		   POST /user/login
		   headers: {'Authorization': 'Bearer ' + jwtEncode(username, password)}
		   // User can now login using email or phone_number so the username parameter can be either an email or phone_number
		   // When username is a phone_number,
		   //   It must be unique for all users
		   //     Signing up with an already registered phone number will now fail
		   //     Saving user info using an already registered phone number will now fail
		   //     Verifying a phone number with an already registered phone number will now fail
		   //   It must start with '+'
		   //   It must be verified first via OTP
		-  Response:
		   {'status': 'OK', 'message': string, 
		    'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
		   // name is now included in the response as per special UX requirement
		   {'status': 'NG', 'message': string}
		   // LOCKOUT SECURITY. When user logins with incorrect password for 5 consecutive times, user needs to reset the password
		   //   When this happens, the error HTTP_401_UNAUTHORIZED is returned.
		   //   The web/mobile app should check message parameter.
		   //   If message is "PasswordResetRequiredException", the web/mobile app should redirect user to the CONFIRM FORGOT PASSWORD/RESET PASSWORD page.
		   //   where user should input the OTP code sent in email and the new password to be used.
		   // MFA SECURITY. When user enables Multi-Factor Authentication (MFA), user needs to input the MFA code sent to mobile phone.
		   //   MFA only works when user sets his phone number and MFA is manually enabled.
		   //   When user logins, the error HTTP_401_UNAUTHORIZED is returned.
		   //   The web/mobile app should check message parameter.
		   //   If message is "MFARequiredException", the web/mobile app should redirect user to the CONFIRM MFA page.
		   //   where user should input the OTP code sent in SMS.
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
		    'info': {'name': string, 
		             'email': string, 
		             'email_verified': boolean, 
		             'phone_number': string, 
		             'phone_number_verified': boolean, 
		             'phone_number_country': string, 
		             'phone_number_isocode': string, 
		             'phone_number_carrier': string, 
		             'mfa_enabled': boolean,
		             'last_login': int,
		             'last_failed_login': int,
		             'identity': {'providerName': string, 'userId': string}, 'username': string} }
		   // phone_number and phone_number_verified are not included if no phone_number has been added yet
		   // phone_number can be added using SIGN UP or UPDATE USER INFO
		   // phone_number_verified will return true once it has been verified using VERIFY PHONE NUMBER and CONFIRM VERIFY PHONE NUMBER
		   // identity is optional and appears only when user logged in using social identity provider like Facebook
		   // phone_number_country refers to the country of the phone number
		   //   phone_number_country is optional and appears only when user has provided and verified his phone number
		   // phone_number_isocode refers to the 2-character ISO code of the country (ex. US for United States of America, PH for Philippines, SG for Singapore)
		   //   phone_number_isocode is optional and appears only when user has provided and verified his phone number
		   // phone_number_carrier refers to the network carrier of the phone number
		   //   phone_number_carrier is optional and appears only when user has provided and verified his phone number
		   // mfa_enabled is optional and appears only when user has provided and verified his phone number
		   // last_login specifies the user's previous successful login time in epoch
		   // last_failed_login specifies the user's previous failed login time in epoch
		   {'status': 'NG', 'message': string}

		I. UPDATE USER INFO
		-  Request:
		   POST /user
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'name': string, 'phone_number': string}
		   // phone_number is optional
		   // phone_number should begin with "+" followed by country code then the number (ex. SG number +6512341234)
		   // phone number must be unique for all users (since LOGIN via phone number is now supported)
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
		   // phone number must be unique for all users (since LOGIN via phone number is now supported)
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
		   //
		   // Resend OTP 
		   //   To resend OTP for CONFIRM SIGN-UP page, use RESEND CONFIRMATION CODE api
		   //   To resend OTP for CONFIRM FORGOT PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for CONFIRM VERIFY PHONE NUMBER page, use VERIFY PHONE NUMBER api
		   //   To resend OTP for USER LOCKOUT RESET PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for LOGIN MFA page is NOT possible with Cognito
		   //
		   // There is no lockout due for invalid OTP. Lockout is only for invalid password

		N. CHANGE PASSWORD
		-  Request:
		   POST /user/change_password
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'token': jwtEncode(password, newpassword)}
		   // newpassword must conform to the password requirements. refer to SIGNUP api
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


		O. LOGIN IDP STORE CODE
		-  Request:
		   POST /user/login/idp/code/ID
		   headers: {'Content-Type': 'application/json'}
		   data: {'code': string}
		   // code can be empty string "" to indicate failed login via idp
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   //
		   // SUMMARY:
		   // 
		   // Login via social identity providers (Facebook/Google/Amazon) consists of two steps:
		   // 1. Web/mobile app opens a system browser to let user LOGIN with his social account.
		   //    INPUT: web/mobile CALLBACK URL, etc.
		   //    OUTPUT: OAuth2 authorization CODE, etc
		   //    https://docs.aws.amazon.com/cognito/latest/developerguide/login-endpoint.html
		   //    "The /login endpoint ... client makes this request through a system browser. 
		   //
		   // 2. Web/mobile app requests for TOKENS by providing the OAuth2 authorization CODE (from step 1)
		   //    INPUT: authorization CODE
		   //    OUTPUT: TOKENS (access_token, id_token, refresh_token)
		   //    https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
		   //    "The /oauth2/token endpoint ... client makes requests to this endpoint directly and not through the system browser."
		   //
		   // Two new REST APIs are available: LOGIN IDP STORE CODE and LOGIN IDP QUERY CODE
		   // - WEB app
		   //   In the case of WEB apps, these APIs are necessary as a way to pass the OAuth2 authorization CODE between 2 processes - 2 browser windows.
		   //   One browser window processes the login process to get the OAuth2 authorization CODE,
		   //   while the other browser window waits for the other browser window to complete and make the OAuth2 authorization CODE available and then request the TOKENS.
		   //
		   // - MOBILE apps
		   //   In the case of MOBILE apps, these APIs are OPTIONAL, as they are NOT necessary.
		   //   The mobile app CALLBACK URI will be called with the OAuth2 authorization CODE.
		   //   The callback thread and the login thread belong to the SAME process of the mobile app, 
		   //   so they pass the TOKENS without needing to call the backend REST APIs.
		   //
		   //
		   // DETAILS:
		   //
		   // When user clicks on the login via social accounts (on the web/mobile apps),
		   // a system browser window is opened which handles getting of the OAuth2 authorization code.
		   //
		   // The new window uses the OAuth2 Domain server https://ft900iotportal.auth.ap-southeast-1.amazoncognito.com
		   // with API /login and the following URL parameters
		   //   client_id=AWS_APP_CLIENT_ID
		   //   response_type=code
		   //   scope=email+openid+phone+aws.cognito.signin.user.admin
		   //   state=ID_RANDOM
		   //   identity_provider=SOCIAL_ACCOUNT [Facebook, Google or LoginWithAmazon]
		   //   redirect_uri=APP_CALLBACK_URL
		   //
		   //     Request:
		   //     HOST: https://ft900iotportal.auth.ap-southeast-1.amazoncognito.com
		   //     GET /login?client_id=AWS_APP_CLIENT_ID&response_type=code&scope=email+openid+phone+aws.cognito.signin.user.admin&state=ID_RANDOM&identity_provider=SOCIAL_ACCOUNT&redirect_uri=APP_CALLBACK_URL
		   //     headers: {'Content-Type': 'application/x-www-form-urlencoded'}
		   //
		   // Once the login operation completed, the WEB/MOBILE APP callback uri will be called
		   //   When operation is successful, the callback URL will be called with 'code' and 'state' parameters
		   //     The WEB app shall then use LOGIN IDP STORE CODE and LOGIN IDP QUERY CODE to pass the code from 1 browser window to the other browser window
		   //
		   //     Given the OAuth2 authorization code, the WEB/MOBILE APP shall continue with the OAuth2 process by calling
		   //     the API /ouath2/token with the following BODY parameters
		   //       grant_type=authorization_code
		   //       client_id=AWS_APP_CLIENT_ID
		   //       code=CODE <parse from the URL parameter in the callback>
		   //       redirect_uri=APP_CALLBACK_URL
		   //
		   //         Request:
		   //         HOST: https://ft900iotportal.auth.ap-southeast-1.amazoncognito.com
		   //         POST /oauth2/token
		   //         headers: {'Content-Type': 'application/x-www-form-urlencoded'}
		   //         data: grant_type=authorization_code&client_id=AWS_APP_CLIENT_ID&code=CODE&redirect_uri=APP_CALLBACK_URL
		   //
		   //   When operation is failed, the URL will be called with 'error' and 'state' parameters
		   //     The page shall then call LOGIN IDP STORE CODE with ID=state and code="" empty string
		   //
		   // Notes:
		   //   1. Request from me the AWS_CLIENT_ID
		   //   2. Request from me to have your APP_CALLBACK_URL registered in Amazon Cognito

		P. LOGIN IDP QUERY CODE
		-  Request:
		   GET /user/login/idp/code/ID
		   headers: {'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string, 'code': string}
		   {'status': 'NG', 'message': string}
		   // code can be empty string "" to indicate failed login via idp
		   //
		   // When user clicks on the login via social accounts (on the web/mobile apps),
		   // a system browser window is opened which handles getting of the OAuth2 authorization code (OAuth process)
		   // The window will then call the web/mobile apps callback URL providing the authorization CODE.
		   // The web/mobile app will call LOGIN IDP STORE CODE to save the OAuth2 authorization CODE.
		   //
		   // To check if the system browser window has completed its operation,
		   // The web/mobile app shall call LOGIN IDP QUERY CODE
		   // The API returns successful when login via social account is completed
		   // To differentiate between successful or failed login, the app shall check if the code returned is not an empty string
		   //
		   // After retrieving the OAuth2 authorization code, the thread shall request for the user TOKENS.

		Q. ENABLE MFA
		-  Request:
		   POST /user/mfa
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'enable': boolean }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		R. LOGIN MFA
		-  Request:
		   POST /user/login/mfa
		   headers: {'Content-Type': 'application/json'}
		   data: { 'username': string, 'confirmationcode': string }
		-  Response:
		   {'status': 'OK', 'message': string, 'token': {'access': string, 'id': string, 'refresh': string}, 'name': string }
		   // output is the same as Login API
		   {'status': 'NG', 'message': string}
		   MFA must be manually enabled before Login within MFA
		   MFA code has 3 minutes validity. It cannot be modified in Cognito.
		   //
		   // Resend OTP 
		   //   To resend OTP for CONFIRM SIGN-UP page, use RESEND CONFIRMATION CODE api
		   //   To resend OTP for CONFIRM FORGOT PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for CONFIRM VERIFY PHONE NUMBER page, use VERIFY PHONE NUMBER api
		   //   To resend OTP for USER LOCKOUT RESET PASSWORD page, use FORGOT PASSWORD api
		   //   To resend OTP for LOGIN MFA page is NOT possible with Cognito
		   //
		   // There is no lockout due for invalid OTP. Lockout is only for invalid password

		S. GET ORGANIZATIONS
		-  Request:
		   GET /user/organizations
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 
		    'organizations': [
		      { 
		        'orgname': string, 
		        'orgid': string, 
		        'membership': string, 
		        'status': string, 
		        'date': int, 
		        'active': int
		      }, ...
		    ]}
		   {'status': 'NG', 'message': string}
		   // user can belong to multiple organizations

		T. SET ACTIVE ORGANIZATION
		-  Request:
		   POST /user/organizations
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'orgname': string, 'orgid': string }
		   // both orgname and orgid are mandatory 
		   //   because its possible for user to belong into 2 or more organizations with the same orgname
		   // to set all organization inactive, both orgname and orgid can be set to string 'None'
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}


		U. GET ORGANIZATION
		-  Request:
		   GET /user/organization
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 
		    'organization': {
		      'orgname': string, 
		      'orgid': string, 
		      'membership': string, 
		      'status': string, 
		      'date': int,
		      'members':[
		        { 
		          'username': string,
		          'membership': string,
		          'status': string,
		          'date': int,
		        }, ...
		      ], 
		     }
		    }
		   }
		   {'status': 'NG', 'message': string}
		   //
		   // This API retreives the ACTIVE organization
		   //   If no organization is active, this 
		   // members only appears when user is the OWNER of the organization
		   // membership is Owner, Member, Not member
		   // status is Invited or Joined
		   // date is the date in epoch in seconds when user was invited or joined the organization

		V. LEAVE ORGANIZATION INVITATION
		-  Request:
		   DELETE /user/organization
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // This API removes user from the ACTIVE organization

		W. ACCEPT ORGANIZATION INVITATION
		-  Request:
		   POST /user/organization/invitation
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // This API accepts invitation from the ACTIVE organization

		X. DECLINE ORGANIZATION INVITATION
		-  Request:
		   DELETE /user/organization/invitation
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // This API declines invitation from the ACTIVE organization


	2. Organization management APIs 

		* All organization APIs points to the ACTIVE organization ONLY.
		  (That's why specifying the orgname is NOT REQUIRED except for creating an organization.)

		A. CREATE ORGANIZATION
		-  Request:
		   POST organization
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'orgname': string}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // User cannot create an organization if he is already a part of an organization. 
		   //   User has to leave the current organization in order to create a new organization.
		   //   HTTP_401_UNAUTHORIZED error is returned if user tries to create an organization but already a part of an organization.
		   // Organization names do not have to be unique across all organizations.
		   // Organization name 'None' is not allowed

		B. DELETE ORGANIZATION
		-  Request:
		   DELETE organization
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // The organization must exist in order to be deleted.
		   //   HTTP_404_NOT_FOUND error is returned if the organization being deleted does not exist.
		   // Only the owner of the organization can delete an organization.
		   //   HTTP_401_UNAUTHORIZED error is returned if the organization is being deleted by a member, not the owner.

		C. CREATE/CANCEL INVITATIONS
		-  Request:
		   POST organization/invitation
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'emails': [], 'cancel': 1}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // emails is a list of emails to be invited to join the organization
		   // cancel flag is optional and only appears if user wants to cancel invitation 
		   // Only the owner of the organization can create/cancel invitation to join the organization
		   //   HTTP_401_UNAUTHORIZED error is returned if a user is being invited by a member, not the owner.
		   // The organization must exist in order to create/cancel invitation.
		   //   HTTP_404_NOT_FOUND error is returned if the organization does not exist.
		   // HTTP_400_BAD_REQUEST error is returned if the user being invited is already part of the organization.

		D. UPDATE/REMOVE MEMBERSHIPS
		-  Request:
		   POST organization/membership
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'emails': [], 'remove': 1}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // emails is a list of emails to be invited to join the organization
		   // remove flag is optional and only appears if user wants to remove members 
		   // Only the owner of the organization can update/remove users to join the organization
		   //   HTTP_401_UNAUTHORIZED error is returned if a user is being invited by a member, not the owner.
		   // The organization must exist in order to update/remove users.
		   //   HTTP_404_NOT_FOUND error is returned if the organization does not exist.
		   // HTTP_400_BAD_REQUEST error is returned if the user being invited is already part of the organization.


		E. GET USER GROUPS
		-  Request:
		   GET organization/groups
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'groups': [{'groupname': string, 'members': [string]}, ...]}
		   {'status': 'NG', 'message': string}

		F. CREATE USER GROUP
		-  Request:
		   POST organization/groups/group/GROUPNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		G. DELETE USER GROUP
		-  Request:
		   DELETE organization/groups/group/GROUPNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		H. GET MEMBERS IN USER GROUP
		-  Request:
		   GET organization/groups/group/GROUPNAME/members
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'members': [string]}
		   {'status': 'NG', 'message': string}
		   // To get Organization members that has no group, use "Ungrouped" for GROUPNAME

		I. UPDATE MEMBERS IN USER GROUP
		-  Request:
		   POST organization/groups/group/GROUPNAME/members
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'members': [strings]}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		J. ADD MEMBER TO USER GROUP
		-  Request:
		   POST organization/groups/group/GROUPNAME/members/member/MEMBERNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		K. REMOVE MEMBER FROM USER GROUP
		-  Request:
		   DELETE organization/groups/group/GROUPNAME/members/member/MEMBERNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}


		L. GET POLICIES
		-  Request:
		   GET organization/policies
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 
		    'policies': [
		      {
		        'policyname': string, 
		        'type': string, 
		        'settings': [{'label': string, 'crud': [boolean, boolean, boolean, boolean]}, ...]
		      }, ...
		    ]
		   }
		   {'status': 'NG', 'message': string}
		   // crud is an array of 4 booleans and corresponds to Create, Read, Update and Delete

		M. GET POLICY
		-  Request:
		   GET organization/policies/policy/POLICYNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 
		    'settings': [
		      {
		        'label': string, 
		        'crud': [boolean, boolean, boolean, boolean]
		      }, ...
		    ]
		   }
		   {'status': 'NG', 'message': string}
		   // crud is an array of 4 booleans and corresponds to Create, Read, Update and Delete

		N. CREATE/UPDATE POLICY
		-  Request:
		   POST organization/policies/policy/POLICYNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'settings': [{'label': string, 'crud': [boolean, boolean, boolean, boolean]}, ...] }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // crud is an array of 4 booleans and corresponds to Create, Read, Update and Delete

		O. DELETE POLICY
		-  Request:
		   DELETE organization/policies/policy/POLICYNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		P. GET POLICY SETTINGS/OPTIONS
		-  Request:
		   GET organization/policies/settings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'settings': {'label': string, 'crud': [boolean, boolean, boolean, boolean]}}
		   {'status': 'NG', 'message': string}

		Q. GET POLICIES IN USER GROUP
		-  Request:
		   GET organization/groups/group/GROUPNAME/policies
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'policies': [string]}
		   {'status': 'NG', 'message': string}

		R. UPDATE POLICIES IN USER GROUP
		-  Request:
		   POST organization/groups/group/GROUPNAME/policies
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'policies': [strings]}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		S. ADD POLICY TO USER GROUP
		-  Request:
		   POST organization/groups/group/GROUPNAME/policies/policy/POLICYNAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}

		T. REMOVE POLICY FROM USER GROUP
		-  Request:
		   DELETE organization/groups/group/GROUPNAME/policies/policy/POLICYNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}


	3. Device registration and management APIs 

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
		     'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // deviceid refers to UUID
		   // timestamp refers to the epoch time (in seconds) the device was registered/added
		   // heartbeat refers to the epoch time (in seconds) of the last publish packet sent by the device
		   // heartbeat will only appear if device has published an MQTT packet
		   // In Javascript, heartbeat can be converted to a readable date using "new Date(heartbeat* 1000)"
		   // version will only appear if device has previously been queried already
		   // heartbeat and version are cached values
		   // location will only appear if location has been set already

		B. GET DEVICES FILTERED
		-  Request:
		   GET /devices/filter/FILTERSTRING
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devices': array[{'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // filter will be applied to devicename and deviceid
		   // if devicename or deviceid contains the filter string, the device will be returned
		   // location will only appear if location has been set already

		C. ADD DEVICE
		-  Request:
		   POST /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'deviceid': string, 'serialnumber': string, 'poemacaddress': string}
		   // deviceid refers to UUID and must be unique
		   // serialnumber is some derivative of UUID
		   // poemacaddress is a unique mac address in uppercase string ex. AA:BB:CC:DD:EE:FF
		   //
		   //   Actual definition of UUID and Serial Number is not yet fully defined
		   //   For now, below are the KNOWN restrictions:
		   //
		   //     UUID: PH80XXRRMMDDYYZZ (16 characters - digits and uppercase letters) 
		   //     SerialNumber: SSSSS (5 characters - digits and uppercase letters)
		   //     POE MAC Address: 00:00:00:00:00:00 (17 characters - digits and A-F uppercase letters)
		   //
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

		E. UPDATE DEVICE NAME
		-  Request:
		   POST /devices/device/DEVICENAME/name
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'new_devicename': string}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // new_devicename refers to the new name of the device

		F. GET DEVICE
		-  Request:
		   GET /devices/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'device': {'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string }}
		   { 'status': 'NG', 'message': string}
		   // deviceid refers to UUID
		   // timestamp refers to the epoch time (in seconds) the device was registered/added
		   // heartbeat refers to the epoch time (in seconds) of the last publish packet sent by the device
		   // heartbeat will only appear if device has published an MQTT packet
		   // In Javascript, heartbeat can be converted to a readable date using "new Date(heartbeat* 1000)"
		   // version will only appear if device has previously been queried already
		   // heartbeat and version are cached values
		   // location will only appear if location has been set already

		G. GET DEVICE DESCRIPTOR
		-  Request:
		   GET /devices/device/DEVICENAME/descriptor
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'descriptor': {}}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'descriptor': {
		          // RO
		          "UUID": string, // UUID
		          "SNO" : string, // Serial Number
		          "PMAC": string, // PoE MAC ID
		          "WMAC": string, // WiFi MAC ID
		          "MOD" : string, // Model Number
		          "PRV" : string, // Product Version
		          "FWV" : string, // Firmware Version and date
		          "ICAC": string, // Sensor Cache Storage Size
		          "IPRT": string, // Number of LDS Ports
		          "ICFG": string, // Configuration Storage
		          "MLG":  string,  // Maximum LDSUs Allowed for Gateway 80
		          "M2M":  string,
		          // RW
		          "WGPS": string, // GPS Location
		          "WASC": string, // Auto-scan
		          "WSCS": string, // Sensor Cache Status
		          "OBJ" : string  // Newly added
		     }
		   }
		   { 'status': 'NG', 'message': string}

		H. GET DEVICES LOCATION
		-  Request:
		   GET /devices/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'locations': [{'devicename': string, location: {'latitude': float, 'longitude': float}}, ...] }
		   { 'status': 'NG', 'message': string}
		   // latitude and longitude can be negative values
		   // by default, location is set to latitude = 0, longitude = 0

		I. SET DEVICES LOCATION
		-  Request:
		   POST /devices/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'locations': [{'devicename': string, location: {'latitude': float, 'longitude': float}}, ...]}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // latitude and longitude can be negative values

		J. DELETE DEVICES LOCATION
		-  Request:
		   DELETE /devices/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // This will just reset location to latitude = 0, longitude = 0 of all devices

		K. GET DEVICE LOCATION
		-  Request:
		   GET /devices/device/DEVICENAME/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'location': {'latitude': float, 'longitude': float} }
		   { 'status': 'NG', 'message': string}
		   // latitude and longitude can be negative values
		   // by default, location is set to latitude = 0, longitude = 0

		L. SET DEVICE LOCATION
		-  Request:
		   POST /devices/device/DEVICENAME/location
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'latitude': float, 'longitude': float}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // latitude and longitude can be negative values

		M. DELETE DEVICE LOCATION
		-  Request:
		   DELETE /devices/device/DEVICENAME/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // This will just reset location to latitude = 0, longitude = 0

		N. UPDATE FIRMWARE
		-  Request:
		   POST /devices/device/DEVICENAME/firmware
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'version': string}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // version is the version of the firmware to use
		   // note that user can select the latest version or the same version (as per Sree)
		   // This API will return immediately if the device to be updated is online.
		   //   If the device is offline, it takes 3 seconds to find out (timeout for waiting device response) so the API will only return after 3 seconds.
		   // GET OTA STATUS should be polled to determine if the OTA update is completed.

		O. UPDATE FIRMWARES
		-  Request:
		   POST /devices/firmware
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'version': string, 'devices': ["devicename", ...]}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // version is the version of the firmware to use
		   // note that user can select the latest version or the same version (as per Sree)
		   // This API will return immediately if all devices to be updated are online.
		   //   If atleast 1 is offline, it takes 3 seconds to find out (timeout for waiting device response) so the API will only return after 3 seconds.
		   // GET OTA STATUSES should be polled to determine if the OTA update is completed.

		P. GET OTA STATUS
		-  Request:
		   GET /devices/device/DEVICENAME/ota
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'ota': {"version": string, "status":string, "time": string, "timestamp": int} }
		   { 'status': 'NG', 'message': string}
		   // version is the update version 
		   // status is the update status 
		   //   pending - device is offline; scheduled for update on device bootup
		   //   ongoing - device ota update is not yet finished
		   //   completed - device ota update is finished
		   // time is the duration for the update
		   // timestamp is the completion datetime in epoch of the update
		   // This API should be polled until the device has completed or pending state.

		Q. GET OTA STATUSES
		-  Request:
		   GET /devices/ota
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'ota': [{"devicename": string, "deviceid", string, "version": string, "status":string, "time": string, "timestamp": int}, ...] }
		   { 'status': 'NG', 'message': string}
		   // version is the update version 
		   // status is the update status 
		   //   pending - device is offline; scheduled for update on device bootup
		   //   ongoing - device ota update is not yet finished
		   //   completed - device ota update is finished
		   // time is the duration for the update
		   // timestamp is the completion datetime in epoch of the update
		   // This API should be polled until all devices have a completed or pending state (no ongoing state)

		R. GET DEVICE HIERARCHY TREE
		-  Request:
		   GET /devices/device/DEVICENAME/hierarchy
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'hierarchy': {"name": string, "children": [{"name": string, "children": []}, ...]} }
		   { 'status': 'NG', 'message': string}

		S. GET DEVICE HIERARCHY TREE (WITH STATUS)
		-  Request:
		   POST /devices/device/DEVICENAME/hierarchy
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'checkdevice': int, 'status': int}
		   // checkdevice and status are both optional.
		   // checkdevice is 1 or 0. it indicates if backend will check the status of the sensors of the device
		   // status is 1 or 0. it indicates if device is online. (DEVICE page needs to query the status of the device. To prevent repeating the call, user can provide the result when calling the API.)
		-  Response:
		   { 'status': 'OK', 'message': string, 'hierarchy': {"name": string, "active": string, "children": [{"name": string, "active": int, "children":[]}, ...]} }
		   { 'status': 'NG', 'message': string}
		   // active is 1 or 0 to indicate if online/offline or enabled/disabled


		T. DOWNLOAD DEVICE SENSOR DATA
		-  Request:
		   POST /devices/device/DEVICENAME/sensordata
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
			//
			// Downloading of device sensor datasets is now supported.
			// -  a ZIP file containing CSV files for each sensor of each LDSU of the device is generated
			// -  then uploaded to AWS S3 before sending an email containing the AWS S3 URL
			// -  refer to DOWNLOAD DEVICE SENSOR DATA api
			// 
			// -  additional info:
			// 1. current performance (local setup):
			//    10K  data points across 16 sensors - 3 seconds
			//    100K data points across 16 sensors - 8 seconds
			//    1M   data points across 16 sensors - 31 seconds
			//    to test more data points; can still be optimized
			// 
			// 2. the CSV file is just a 2-column table with timestamp and value
			// 3. timestamp is the epoch time in seconds (no formatting done so that filesize doesn't become big)
			// 4. value is formatted according to the corresponding sensor format and accuracy
			// 5. the filename of the CSV file is <LDSUUUID>-<LDSUSAID>.csv
			// 6. the filename of the ZIP file is <DEVICEID>.zip
			// 7. if a device has 1 LDSU and that LDSU has 4 sensors, the zip file contains 4 CSV files.
			//    all files are generated even when no data is available for specific sensors.
			// 8. format of the email is below:
			//    Hi <full name>,
			// 
			//    Sensor data for device Dev1 with UUID PH80XXRR0507208E is now available.
			//    Click the link below to download.
			//    https:// ft900-iot-portal.s3.amazonaws.com/sensordata/PH80XXRR0507208E.zip
			// 
			//    Best Regards,
			//    Bridgetek Pte. Ltd.
			// 
			// 9. to test using web app, go to the OLD sensor dashboard page, 
			//    (in the figma UI, this is located in the device subscription page)
			// 
			//    select a device and click download sensor data button.
			//    you shall receive an email containing the link.
			//    it can take seconds to minutes depending on the size of the sensor data.
			//
			// 10. if a device has 4 LDSUs with 4 sensors each => 16 sensors total 
			//     then there will be 16 CSV files in the ZIP file
			//

		U. CLEAR DEVICE SENSOR DATA
		-  Request:
		   DELETE /devices/device/DEVICENAME/sensordata
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}


	4. Device group registration and management APIs

		A. GET DEVICE GROUPS
		-  Request:
		   GET /devicegroups
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devicegroups': array[
		       {
		         'groupname': string, 'timestamp': int, 
		         'devices': [
		           {
		             'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string,
		             'location': {'latitude': float, 'longitude': float}
		           },...
		         ]
		       }, ...
		     ] 
		   }
		   { 'status': 'NG', 'message': string}

		B. ADD DEVICE GROUP
		-  Request:
		   POST /devicegroups/group/DEVICEGROUPNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'devices': ["devicename", ...]}
		   // devices is optional; if provided then the list of devices will be included in the group to be created
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // HTTP_409_CONFLICT is returned if group name is already used

		C. REMOVE DEVICE GROUP
		-  Request:
		   DELETE /devicegroups/group/DEVICEGROUPNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		D. GET DEVICE GROUP
		-  Request:
		   GET /devicegroups/group/DEVICEGROUPNAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devicegroup': {'groupname': string, 'timestamp': int, 'devices': ["devicename", ...]} }
		   { 'status': 'NG', 'message': string}

		E. GET DEVICE GROUP DETAILED
		-  Request:
		   GET /devicegroups/group/DEVICEGROUPNAME/devices
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devicegroup': {
		       'groupname': string, 'timestamp': int, 
		       'devices': array[
		         {
		           'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string,
		           'location': {'latitude': float, 'longitude': float}
		         }, ...
		       ]
		     }
		   }
		   { 'status': 'NG', 'message': string}

		F. UPDATE DEVICE GROUP NAME
		-  Request:
		   POST /devicegroups/group/DEVICEGROUPNAME/name
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'new_groupname': string}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		G. ADD DEVICE TO GROUP
		-  Request:
		   POST /devicegroups/group/DEVICEGROUPNAME/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'destdevicegroupname': string}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // destdevicegroupname is optional and appears if device is to be transferred from DEVICEGROUPNAME group to destdevicegroupname group
		   // HTTP_400_BAD_REQUEST is returned if device already added in group

		H. REMOVE DEVICE FROM GROUP
		-  Request:
		   DELETE /devicegroups/group/DEVICEGROUPNAME/device/DEVICENAME
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		I. SET DEVICES IN DEVICE GROUP
		-  Request:
		   POST /devicegroups/group/DEVICEGROUPNAME/devices
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'devices': ["devicename", ...]}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // devices is an array of device names
		   // devices can be an empty array, meaning remove all devices in the group

		J. GET UNGROUPED DEVICES
		-  Request:
		   GET /devicegroups/ungrouped
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'devices': array[
		       {
		         'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string,
		         'location': {'latitude': float, 'longitude': float}
		       }, ...
		     ]
		   }
		   { 'status': 'NG', 'message': string}
		   // The return value is similar to GET DEVICES api

		K. GET DEVICE GROUPS AND UNGROUPED DEVICES
		-  Request:
		   GET /devicegroups/mixed
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'data': {
		       'devices': array[
		         {
		           'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string, 
		           'location': {'latitude': float, 'longitude': float}
		         }, ...
		       ],
		       'devicegroups': array[
		         {
		           'groupname': string, 'timestamp': int, 
		           'devices': [
		             {
		               'devicename': string, 'deviceid': string, 'serialnumber': string, 'timestamp': int, 'heartbeat': int, 'version': string, 
		               'location': {'latitude': float, 'longitude': float}
		             }, ...
		           ]
		         }, ...
		       ]
		     }
		   }
		   { 'status': 'NG', 'message': string}
		   // Yes, this is a weird API because of the weird FIGMA UI (All, Groups, Standalone - WTF!)

		L. GET DEVICE GROUP LOCATION
		-  Request:
		   GET /devicegroups/group/DEVICEGROUPNAME/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'locations': [{'devicename': string, location: {'latitude': float, 'longitude': float}}, ...] }
		   { 'status': 'NG', 'message': string}
		   // latitude and longitude can be negative values
		   // by default, location is set to latitude = 0, longitude = 0

		M. SET DEVICE GROUP LOCATION
		-  Request:
		   POST /devicegroups/group/DEVICEGROUPNAME/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'locations': [{'devicename': string, location: {'latitude': float, 'longitude': float}}, ...]}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // latitude and longitude can be negative values

		N. DELETE DEVICE GROUP LOCATION
		-  Request:
		   DELETE /devicegroups/group/DEVICEGROUPNAME/location
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}
		   // This will just reset location to latitude = 0, longitude = 0 of each device in the group
	
		O. GET DEVICE GROUP OTA STATUSES
		-  Request:
		   GET /devicegroups/group/DEVICEGROUPNAME/ota
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'ota': [{"devicename": string, "deviceid", string, "version": string, "status":string, "time": string, "timestamp": int}, ...] }
		   { 'status': 'NG', 'message': string}
		   // version is the update version 
		   // status is the update status 
		   //   pending - device is offline; scheduled for update on device bootup
		   //   ongoing - device ota update is not yet finished
		   //   completed - device ota update is finished
		   // time is the duration for the update
		   // timestamp is the completion datetime in epoch of the update
		   // This API should be polled until all devices have a completed or pending state (no ongoing state)


	5. Device access and control APIs (LDSBUS)

		A. GET LDS BUS
		-  Request:
		   GET /devices/device/DEVICENAME/ldsbus/PORT
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
		-  Response:
		   { 'status': 'OK', 'message': string, 'ldsbus': 
		     [ 
		       {
		         "ldsus"     : [
		           {
		             "status":   string,  // "reachable" or "unreachable"
		             "LABL":     string,  // LDSU Friendly name, value can be changed by user via CHANGE LDSU NAME api
		             "UID":      string,  // LDSU UUID
		             "PORT":     string,  // LDS Bus Port

		             // just for displaying, not really important
		             "descriptor": {
		                 "DID":  string,  // LDS device ID from eeprom. DID is unique within the Port
		                 "IID":  string,  // Instance ID. IID is unique within the GW
		                 "MFG":  string,  // Manufacturing date - DDMMYYYY
		                 "NAME": string,  // Product Name: "BRT 4-in-1 Sensor", "Thermocouple", "Air Quality Sensor", ...
		                 "OBJ":  string   // LDSU Object type: "32768", "32769", "32770", ...
		                 "PRV":  string,  // Product version
		                 "SNO":  string,  // Serial Number
		             }
		           }, 
		           ...
		         ], 
		         "sensors"  : [
		           {
		             "sensorname":   string,
		             "class":        string, // Class - "temperature", "humidity", "ambient light", "motion detection", "VOC gas"
		             "source":       string, // Refers to LDSU UUID
		             "number":       string, // Refers to the index in LDUS (Note: An LDSU can be composed of more than 1 sensor. This is the index of the sensor in the LDSU.)
		             "port":         string, // LDS PORT
		             "name":         string, // LDS LABL

		             // for sensor displaying
		             "accuracy": string,     // number of decimal places
		             "format":   string,     // float, integer, boolean
		             "minmax":   [string, string], // minimum and maximum
		             "type":     string,     // input, output
		             "unit":     string,     // C, %, ppm, ...
		             "address":  string,     // i2c address in LDSU
		             "obj":      string,     // LDSU Object type: "32768", "32769", "32770", ...

		             // optional, appears if sensor has various modes
		             "opmodes":  [
		               {
		                 "id":          int,
		                 "name":        string,
		                 "minmax":      [string, string],
		                 "accuracy":    string,
		                 "description": string,
		               }
		               , ...
		             ],

		             // for enabled/disabled/configured
		             "configured": int, 
		             "enabled":    int,

		             // optional, appears if sensor is enabled
		             'readings': {
		                 'value': float, 
		                 'lowest': float, 
		                 'highest': float
		             },

		           },
		           ...
		         ], 
		         "actuators": [] // TODO
		       },
		       ...
		     ] 
		   }
		   // if port number is 1,2 or 3, ldsbus length is 1
		   // if port number is 0, ldsbus contains all 3 ports so ldsbus is an arry of 3 items
		   // "unreachable" means the LDSU is not currently present but was previously registered by the IoT Gateway (ex. the LDSU was unplugged)
		   { 'status': 'NG', 'message': string }

		B. DELETE LDS BUS
		-  Request:
		   DELETE /devices/device/DEVICENAME/ldsbus/PORT
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}

		C. SCAN LDS BUS
		-  Request:
		   POST /devices/device/DEVICENAME/ldsbus/PORT
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
		-  Response:
		   { 'status': 'OK', 'message': string, 'ldsbus': json_object }
		   { 'status': 'NG', 'message': string }
		   // This is exactly the same as GET LDS BUS
		   // The only difference is that this API queries the device itself (to get the latest information, ex. if an LDSU was unplugged)
		   // Refer to the return value of GET LDS BUS

		D. GET LDS BUS LDSUS
		-  Request:
		   GET /devices/device/DEVICENAME/ldsbus/PORT/ldsus
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
		-  Response:
		   { 'status': 'OK', 'message': string, 'ldsus': 
		     [ 
		       {
		         "status":   string,  // "reachable" or "unreachable"
		         "LABL":     string,  // LDSU Friendly name, value can be changed by user via CHANGE LDSU NAME api
		         "UID":      string,  // LDSU UUID
		         "PORT":     string,  // LDS Bus Port

		         // just for displaying, not really important
		         "descriptor": {
		             "DID":  string,  // LDS device ID from eeprom. DID is unique within the Port
		             "IID":  string,  // Instance ID. IID is unique within the GW
		             "MFG":  string,  // Manufacturing date - DDMMYYYY
		             "NAME": string,  // Product Name: "BRT 4-in-1 Sensor", "Thermocouple", "Air Quality Sensor", ...
		             "OBJ":  string   // LDSU Object type: "32768", "32769", "32770", ...
		             "PRV":  string,  // Product version
		             "SNO":  string,  // Serial Number
		         }
		       }, 
		       ...
		     ] 
		   }
		   // if port number is 1,2 or 3, ldsbus length is 1
		   // if port number is 0, ldsbus contains all 3 ports so ldsbus is an arry of 3 items
		   // "unreachable" means the LDSU is not currently present but was previously registered by the IoT Gateway (ex. the LDSU was unplugged)
		   { 'status': 'NG', 'message': string }

		E. GET LDS BUS SENSORS
		-  Request:
		   GET /devices/device/DEVICENAME/ldsbus/PORT/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
		-  Response:
		   { 'status': 'OK', 'message': string, 'sensors': 
		     [ 
		       {
		         "sensorname":   string,
		         "class":        string, // Class - "temperature", "humidity", "ambient light", "motion detection", "VOC gas"

		         "source":       string, // Refers to LDSU UUID
		         "number":       string, // Refers to the index in LDUS (Note: An LDSU can be composed of more than 1 sensor. This is the index of the sensor in the LDSU.)
		         "port":         string, // LDS PORT
		         "name":         string, // LDS LABL

		         // for sensor displaying
		         "accuracy": string,     // number of decimal places
		         "format":   string,     // float, integer, boolean
		         "minmax":   [string, string], // minimum and maximum
		         "type":     string,     // input, output
		         "unit":     string,     // C, %, ppm, ...
		         "address":  string,     // i2c address in LDSU
		         "obj":      string,     // LDSU Object type: "32768", "32769", "32770", ...

		         // optional, appears if sensor has various modes
		         "opmodes":  [
		           {
		             "id":          int,
		             "name":        string,
		             "minmax":      [string, string]
		             "accuracy":    string,
		             "description": string,
		           }
		           , ...
		         ],

		         // for enabled/disabled/configured
		         "configured": int, 
		         "enabled":    int, 

		         // optional, appears if sensor is enabled
		         'readings': {
		             'value': float, 
		             'lowest': float, 
		             'highest': float
		         }

		       },
		       ...
		     ] 
		   }
		   // if PORT_NUMBER is 1,2 or 3, ldsbus length is 1
		   // if PORT_NUMBER is 0, ldsbus contains all 3 ports so ldsbus is an arry of 3 items
		   { 'status': 'NG', 'message': string }

		F. GET LDS BUS ACTUATORS
		-  Request:
		   GET /devices/device/DEVICENAME/ldsbus/PORT/actuators
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // PORT_NUMBER can be 1, 2, 3, or 0 (0 if all lds bus)
		-  Response:
		   { 'status': 'OK', 'message': string, 'actuators': 
		     [ 
		       {},
		       ...
		     ] 
		   }
		   // if PORT_NUMBER is 1,2 or 3, ldsbus length is 1
		   // if PORT_NUMBER is 0, ldsbus contains all 3 ports so ldsbus is an arry of 3 items
		   { 'status': 'NG', 'message': string }

		G. CHANGE LDSU NAME
		-  Request:
		   POST /devices/device/DEVICENAME/ldsu/LDSUUUID/name
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: {'name': string}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to ldsu["UID"]. Refer to GET LDSU.

		H. IDENTIFY LDSU
		-  Request:
		   POST /devices/device/DEVICENAME/ldsu/LDSUUUID/identify
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to ldsu["UID"]. Refer to GET LDSU.

		I. GET LDSU
		-  Request:
		   GET /devices/device/DEVICENAME/ldsu/LDSUUUID
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'ldsu': 
		       {
		         "status":   string,  // "reachable" or "unreachable"
		         "LABL":     string,  // LDSU Friendly name, value can be changed by user via CHANGE LDSU NAME api
		         "UID":      string,  // LDSU UUID
		         "PORT":     string,  // LDS Bus Port

		         // just for displaying, not really important
		         "descriptor": {
		             "DID":  string,  // LDS device ID from eeprom. DID is unique within the Port
		             "IID":  string,  // Instance ID. IID is unique within the GW
		             "MFG":  string,  // Manufacturing date - DDMMYYYY
		             "NAME": string,  // Product Name: "BRT 4-in-1 Sensor", "Thermocouple", "Air Quality Sensor", ...
		             "OBJ":  string   // LDSU Object type: "32768", "32769", "32770", ...
		             "PRV":  string,  // Product version
		             "SNO":  string,  // Serial Number
		         }
		       }
		    }
		   // LDSUUUID refers to ldsu["UID"]. Refer to GET LDSU.

		J. DELETE LDSU
		-  Request:
		   DELETE /devices/device/DEVICENAME/ldsu/LDSUUUID
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   // LDSUUUID refers to ldsu["UID"]. Refer to GET LDSU.

		K. SET LDSU DEVICE (SENSOR/ACTUATOR) PROPERTIES
		-  Request:
		   POST /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: { ... } // same as SET I2C DEVICE PROPERTIES
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }
		   //
		   // LDSUUUID refers to the sensor["source"]. Refer to GET LDS BUS SENSORS.
		   // NUMBER refers to the sensor["number"]. Refer to GET LDS BUS SENSORS.
		   // SENSORNAME refers to the sensor["sensorname"]. Refer to GET LDS BUS SENSORS.
		   //
		   // NOTIFICATION structure inside the sensor class data => data["notification"]
		        'notification': { // this notification object is generic for UART/GPIO/I2C
		            'messages': [
		                { 'message': string, 'enable': boolean }, // for GPIO, index 0 will always refer to message on activation
		                { 'message': string, 'enable': boolean }  // for GPIO, index 1 will always refer to message on deactivation
		            ],
		            'endpoints' : {
		                'mobile': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'email': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'notification': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'modem': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                    'isgroup': boolean    // true if all recipients are device groups, false if all recipients are devices
		                },
		                'storage': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		            }
		        }
		   //
		   // TEMPERATURE/HUMIDITY/AMBIENTLIGHT/MOTIONSENSOR/CO2GAS/VOCGAS class
		   data: {
		           "opmode": int,
		           "mode": int,              // single threshold, dual threshold, continuous
		           "threshold": {
		               "value": int/float,   // for single threshold mode, should use the sensor["minmax"][1] as default value, int/float depending on sensor["format"]
		               "min": int/float,     // for dual threshold mode, should use the sensor["minmax"][0] as default value, int/float depending on sensor["format"]
		               "max": int/float,     // for dual threshold mode, should use the sensor["minmax"][1] as default value, int/float depending on sensor["format"]
		               "activate": int       // for dual threshold mode
		           }, 
		           "alert": {
		               "type": int, 
		               "period": int
		           }, 
		           "hardware": {             // for continuous mode
		               'enable': boolean
		               'recipients': string, // can be multiple items separated by comma
		               'isgroup': boolean    // true if all recipients are device groups, false if all recipients are devices
		           }, 
		           "notification": json_obj, // see above
		      }
		   //
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
		   //   notification refers to the the same notification settings for MENOS alerting
		   //   hardware
		   //     appears when mode is Continuous
		   //     enable
		   //       default value is false in UI
		   //       if true, data is to be forwarded to an actuator given the specified devicename
		   //       else, data is not to be forwarded to an actuator
		   //     devicename
		   //       used when enable is set to true

		L. GET LDSU DEVICE (SENSOR/ACTUATOR) PROPERTIES
		-  Request:
		   GET /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': 
		   //
		   // TEMPERATURE class
		     {
		           "opmode": int,
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string, "enable": boolean}, 
		           "notification": json_obj,
		      }
		   //
		   // HUMIDITY class
		     {
		           "opmode": int,
		           "mode": int, 
		           "threshold": {"value": int, "min": int, "max": int, "activate": int}, 
		           "alert": {"type": int, 'period': int}, 
		           "hardware": {"devicename": string, "enable": boolean}, 
		           "notification": json_obj,
		      }

		   }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to the sensor["source"]. Refer to GET LDS BUS SENSORS.
		   // NUMBER refers to the sensor["number"]. Refer to GET LDS BUS SENSORS.
		   // SENSORNAME refers to the sensor["sensorname"]. Refer to GET LDS BUS SENSORS.

		M. DELETE LDSU DEVICE (SENSOR/ACTUATOR) PROPERTIES
		-  Request:
		   DELETE /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to the sensor["source"]. Refer to GET LDS BUS SENSORS.
		   // NUMBER refers to the sensor["number"]. Refer to GET LDS BUS SENSORS.
		   // SENSORNAME refers to the sensor["sensorname"]. Refer to GET LDS BUS SENSORS.

		N. ENABLE/DISABLE LDSU DEVICE (SENSOR/ACTUATOR)
		-  Request:
		   POST /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/enable
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to the sensor["source"]. Refer to GET LDS BUS SENSORS.
		   // NUMBER refers to the sensor["number"]. Refer to GET LDS BUS SENSORS.
		   // SENSORNAME refers to the sensor["sensorname"]. Refer to GET LDS BUS SENSORS.

		O. CHANGE LDSU DEVICE (SENSOR/ACTUATOR) NAME
		-  Request:
		   POST /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/name
		   headers: {'Authorization': 'Bearer ' + token.access}
		   data: { 'name': string }
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to the sensor["source"]. Refer to GET LDS BUS SENSORS.
		   // NUMBER refers to the sensor["number"]. Refer to GET LDS BUS SENSORS.
		   // SENSORNAME refers to the sensor["sensorname"]. Refer to GET LDS BUS SENSORS.

		P. GET LDSU DEVICE SENSOR READINGS
		-  Request:
		   GET /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/readings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string,
		     'readings': {
		       'value': float, 
		       'lowest': float, 
		       'highest': float
		     }
		   }
		   { 'status': 'NG', 'message': string }
		   // LDSUUUID refers to the sensor["source"]. Refer to GET LDS BUS SENSORS.
		   // NUMBER refers to the sensor["number"]. Refer to GET LDS BUS SENSORS.
		   // SENSORNAME refers to the sensor["sensorname"]. Refer to GET LDS BUS SENSORS.


	6. Device access and control APIs (STATUS, UART, GPIO)

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

		B. GET STATUSES
		-  Request:
		   GET /devices/status
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': [{ "devicename": string, "status": int, "version": string }] }
		   { 'status': 'NG', 'message': string, 'value': [{ "devicename": string, "heartbeat": string, "version": string}] }
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

		C. SET STATUS
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


		D. GET SETTINGS
		-  Request:
		   GET /devices/device/DEVICENAME/settings
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { "sensorrate": int } }
		   { 'status': 'NG', 'message': string }
		   // sensorrate is the time in seconds the device publishes sensor data for ENABLED devices

		E. SET SETTINGS
		-  Request:
		   POST /devices/device/DEVICENAME/settings
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'sensorrate': int }
		   // sensorrate is the time in seconds the device publishes sensor data for ENABLED devices
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }


		F. GET UARTS
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

		G. GET UART PROPERTIES
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
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'email': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'notification': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'modem': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                    'isgroup': boolean      // true if all recipients are device groups, false if all recipients are devices
		                },
		                'storage': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
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

		H. SET UART PROPERTIES
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
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'email': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'notification': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'modem': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'storage': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
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

		I. ENABLE/DISABLE UART
		-  Request:
		   POST /devices/device/DEVICENAME/uart/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }



		J. GET GPIOS
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

		K. GET GPIO PROPERTIES
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
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'email': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'notification': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'modem': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
		                },
		                'storage': {
		                    'enable': boolean,
		                    'recipients': string,   // can be multiple items separated by comma
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

		L. SET GPIO PROPERTIES
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
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'email': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'notification': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'modem': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
		                },
		                'storage': {
		                    'enable': boolean,
		                    'recipients': string, // can be multiple items separated by comma
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

		M. ENABLE/DISABLE GPIO
		-  Request:
		   POST /devices/device/DEVICENAME/gpio/NUMBER/enable
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'enable': int }
		   // enable is an int indicating if disabled (0) or enabled (1)
		-  Response:
		   { 'status': 'OK', 'message': string }
		   { 'status': 'NG', 'message': string }

		N. GET GPIO VOLTAGE
		-  Request:
		   GET /devices/device/DEVICENAME/gpio/voltage
		   headers: {'Authorization': 'Bearer ' + token.access}
		   // note that no gpio NUMBER is included because this applies to all 4 gpios
		-  Response:
		   { 'status': 'OK', 'message': string, 'value': { 'voltage': int } }
		   { 'status': 'NG', 'message': string }
		   // voltage is an index of the value in the list of voltages
		   //   ["3.3 V", "5 V"]

		O. SET GPIO VOLTAGE
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


	7. Device access and control APIs (I2C)


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
		     'sensor': {'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be SPEAKER, DISPLAY, LIGHT, POTENTIOMETER, TEMPERATURE

		D. GET I2C DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		E. GET ALL I2C DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		F. GET ALL I2C INPUT DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/sensors/input
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		G. GET ALL I2C OUPUT DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/i2c/sensors/output
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
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


	8. Device access and control APIs (ADC)


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
		     'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be ANEMOMETER

		D. GET ADC DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/adc/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		E. GET ALL ADC DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/adc/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
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


	9. Device access and control APIs (1WIRE)


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
		     'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be TEMPERATURE

		D. GET 1WIRE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added

		E. GET ALL 1WIRE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/1wire/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
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


	10. Device access and control APIs (TPROBE)


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
		     'sensor': {'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []} }
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // class can be TEMPERATURE with subclass of HUMIDITY

		D. GET TPROBE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/NUMBER/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}, 'attributes': []}, ...]}
		   { 'status': 'NG', 'message': string}
		   // timestamp refers to the epoch time the sensor was registered/added
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass

		E. GET ALL TPROBE DEVICES
		-  Request:
		   GET /devices/device/DEVICENAME/tprobe/sensors
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': array[{'sensorname': string, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': []}, ...]}
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


	11. Device sensor dashboarding

		A. GET SENSOR READINGS DATASET FILTERED
		-  Request:
		   POST /devices/sensors/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'devicename': string, 'class': string, 'status': string, 'timerange': string, 'points': int, 'checkdevice': int}
		   // devicename can be "All devices" or the devicename of specific device
		   // class can be ["All classes", "potentiometer", "temperature", "humidity", "anemometer", "battery", "fluid"]
		   // status can be ["All online/offline", "online", "offline"]
		   // timerange can be:
		        Last 5 minutes
		        Last 15 minutes
		        Last 30 minutes
		        Last 60 minutes
		        Last 3 hours
		        Last 6 hours
		        Last 12 hours
		        Last 24 hours
		        Last 3 days
		        Last 7 days
		        Last 2 weeks
		        Last 4 weeks
		        Last 3 months
		        Last 6 months
		        Last 12 months
		   // points can be 60, 30 or 15 points (for mobile, since screen is small, should use 30 or 15 instead of 60)
		   // index is 0 by default. 
		      To view the timeranges above, index is 0
		      To view the next timerange, ex. "Last Last 5 minutes", the previous instance, index is 1. and so on...
		   // checkdevice is 1 or 0. 1 if device status needs to be check if device is online and if sensor is active
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'sensors': [
		                  {
		                    'devicename': string, 'sensorname': string, 'address': int, 'manufacturer': string, 'model': string, 'class': string, 'type': string, 'timestamp': int, 'enabled': int, 'configured': int, 'units': [], 'formats': [], 'attributes': [], 
		                    'dataset':  {'labels': [], 'data': [[],...], 'low': [[],...], 'high': [[],...]}, 
		                    'readings': {'value': float, 'lowest': float, 'highest': float, 'subclass': {'value': float, 'lowest': float, 'highest': float}
		                  }
		                ],
		     'stats'  : { 
		                  'devices': {
		                    'statuses':    {'labels': [strings], 'data': [int]},
		                    'groups:       {'labels': [strings], 'data': [int]},
		                    'versions':    {'labels': [strings], 'data': [int]},
		                    'locations':   {'labels': [strings], 'data': [int]}
		                  },
		                  'sensors': {
		                    'statuses':    {'labels': [strings], 'data': [int]},
		                    'types':       {'labels': [strings], 'data': [int]},
		                    'peripherals': {'labels': [strings], 'data': [int]},
		                    'classes':     {'labels': [strings], 'data': [int]}
		                  },
		                },
		     'summary': { 
		                  'sensors': [{'sensorname': string, 'devicename': string, 'type': string, 'ldsu': string, 'number': string, 'classes': string, 'configuration': string, 'enabled': int}],
		                  'devices': [{'devicename': string, 'group': string, 'version': string, 'location': string, 'status': int}],
		                },
		     'usages':  {
		                  'alerts':  {'labels': ['sms', 'emails', 'notifications'], 'data': [int, int, int]},
		                  'storage': {'labels': ['sensor data', 'alerts data'], 'data': [int, int]},
		                  'login':   {'labels': ['email', 'sms'], 'data': [int, int]}
		                }

		   { 'status': 'NG', 'message': string}
		   //
		   // the subclass parameter of readings parameter will only appear if the sensor has a subclass
		   //   if sensor has a subclass:  'dataset': {'labels': [], 'data': [[],[]]}
		   //   if sensor has no subclass: 'dataset': {'labels': [], 'data': [[]]}
		   //   this make the dataset object directly usable by Chart.JS line charts
		   // low and high does NOT appear when "Last 5 minutes" timerange is selected.
		   //
		   // stats and summary will ONLY appear if checkdevice parameter is set to 1
		   //   stats is for doughnut/pie charts to show proportions of online/offline devices, enabled/disabled sensors, device peripheral types used, sensor classes used
		   //     uses labels and data arrays to make object directly usable by Chart.JS doughnut/pie charts
		   //   summary is for the table

		B. DELETE SENSOR READINGS DATASET
		-  Request:
		   DELETE /devices/sensors/readings/dataset
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'devicename': string}
		   // devicename can be "All devices" or the devicename of specific device
		-  Response:
		   { 'status': 'OK', 'message': string}
		   { 'status': 'NG', 'message': string}


	12. Device transaction recording APIs

		A. GET HISTORIES
		-  Request:
		   GET /devices/histories
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': int}, ...]}
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
		     'transactions': array[{'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': int}, ...]}
		   { 'status': 'NG', 'message': string}

		C. GET MENOS HISTORIES
		-  Request:
		   GET /devices/menos
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'timestamp': int, 'recipient': string, 'messagelen': int, 'type': string, 'source': string, 'sensorname': string, 'condition': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // sensorname and condition are optional (ex. when source is UART/GPIOX, then both sensorname and condition are not present

		D. GET MENOS HISTORIES FILTERED
		-  Request:
		   POST /devices/menos
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'devicename': string, 'type': string, 'source': string,  'datebegin': int, 'dateend': int }
		   // all data items are optional (when data is empty, that is no filters are set, it is actually equivalent to as GET MENOS HISTORIES)
		   // to filter by device name, include devicename
		   // to filter by type, include type
		   // to filter by source, include source
		   // to filter by date, include datebegin or both datebegin, dateend
		   // datebegin and dateend are both epoch computed values
		-  Response:
		   { 'status': 'OK', 'message': string, 
		     'transactions': array[{'devicename': string, 'deviceid': string, 'timestamp': int, 'recipient': string, 'messagelen': int, 'type': string, 'source': string, 'sensorname': string, 'condition': string}, ...]}
		   { 'status': 'NG', 'message': string}
		   // sensorname and condition are optional (ex. when source is UART/GPIOX, then both sensorname and condition are not present


	13. Account subscription and payment APIs

		// Use any of the following Paypal Sandbox accounts: (https://sandbox.paypal.com)
		   dev1.sg@brtchip.com (personal) - Singapore buyer
		   dev1.us@brtchip.com (personal) - United States buyer 
		   dev1.uk@brtchip.com (personal) - United Kingdom buyer
		   dev1.in@brtchip.com (personal) - India buyer
		   dev1.ch@brtchip.com (personal) - China buyer
		   dev1.ge@brtchip.com (personal) - Germany buyer
		   The account that receives the payments is iotportal@brtchip.com (business)

		A. GET SUBSCRIPTION
		-  Request:
		   GET /account/subscription
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'subscription': {'type': string, 'credits': int} }
		   {'status': 'NG', 'message': string}

		B. PAYPAL SETUP
		-  Request:
		   POST /account/payment/paypalsetup
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: { 'returnurl': string, 'cancelurl', string, 'amount': int }
		-  Response:
		   {'status': 'OK', 'message': string, 'payment': {'approvalurl': string, 'paymentid': string}}
		   {'status': 'NG', 'message': string}
		   // returnurl is your web/mobile callback URL for approval
		   // cancelurl is your web/mobile callback URL for cancellation (user does not proceed to approving the payment)
		   // " For a web app, the urls should start with https://, such as https://www.example.com.
		   //   For an iOS or Android app, you can use a callback URL such as myapp://. "
		   // amount is in USD
		   // Web/mobile app shall open a system browser (Android: Google Chrome, IOS: Safari) for approvalurl.
		   //   Mobile apps can open a webview instead of a system browser to open the approvalurl.
		   //   So it doesn't matter if its a system browser or a webview.
		   // Customer logins to their Paypal account on the system browser and approves the payment transaction.
		   // Once the payment transaction is approved by the customer, the returnurl callback will be called.
		   //   Paypal will make the browser invoke the mobile app callback (from the system browser or webview).
		   //   When the callback is called, the paymentID and PayerID is appended to the URL, in url encoded ?&= notation.
		   // When the URL callback URL is called, the web app shall call PAYPAL STORE PAYERID, 
		   //   while the mobile app can already call PAYPAL EXECUTE 
		   //   (since it can pass the paymentID and PayerID from one thread to another thread. 
		   //   In the web app case, it has to pass from 1 browser to another browser so PAYPAL STORE PAYERID is necessary.)

		C. PAYPAL STORE PAYERID
		-  Request:
		   POST /account/payment/paypalpayerid/PAYMENTID
		   headers: {'Content-Type': 'application/json'}
		   data: { 'payerid': string }
		-  Response:
		   {'status': 'OK', 'message': string}
		   {'status': 'NG', 'message': string}
		   // This API is only applicable for web app; not for mobile apps; see UML sequence diagram
		   // When the returnurl callback from PAYPAL SETUP is called, the web app shall call PAYPAL STORE PAYERID.
		   // This callback contains the parameters: PayerID and paymentID, needed for payerid and PAYMENTID, respectively
		   // These parameters should then be stored 

		D. PAYPAL EXECUTE
		-  Request:
		   POST /account/payment/paypalexecute/PAYMENTID
		   headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}
		   data: {'payerid': string}
		   // payerid is optional - only applicable for mobile apps; not for web app; see UML sequence diagram
		-  Response:
		   {'status': 'OK', 'message': string, 'subscription': {'type': string, 'credits': int, 'prevcredits': int}}
		   {'status': 'NG', 'message': string}
		   // When the callback window completes and exits, the web/mobile app shall call PAYPAL EXECUTE
		   // This API will internally read the QUERY PAYERID given the PAYMENTID
		   // and then proceed with execution of the payment transaction
		   // NG is returned when transaction fails (due to user cancelled or closed the window, etc)

		E. GET PAYPAL TRANSACTIONS
		-  Request:
		   GET /account/payment/paypal
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'transactions': [{'id': string, 'timestamp': int, 'amount': float, 'value': int, 'newcredits': int, 'prevcredits': int}, ...]}
		   // id refers to the transaction id, which appears on both the buyer and seller invoices on Paypal website
		   {'status': 'NG', 'message': string}
		   // This API returns the list of paypal payment transactions from backend database
		   // The PaymentID and PayerID are not included in the returned structure as they will only be needed for retrieving detailed info from PAYPAL
		      Paypal Payment ID // abstracted from both buyer and seller
		      Paypal Payer ID // no need to store the Paypal email, first name, last name, address, phone, country
		      Paypal Transaction ID // this is what appears on both the buyer and seller invoices on Paypal website
		      Paypal Transaction amount
		      Paypal Transaction timestamp
		      New credit balance
		      Previous credit balance
		   // Paypal will store the transaction details for 7 years, as mandated by law. 
		   // To retrieve detailed information about a transaction (if necessary for customer legal disputes), the PaymentID from the database shall be used. 
		   // Note that in the Paypal website, it seems its only possible to query up to 3 years but invoices can be requested up to 7 years.


	14. Mobile services

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


	15. Supported devices/firmware updates

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

		C. GET DEVICE FIRMWARE UPDATES
		-  Request:
		   GET /others/firmwareupdates
		   headers: {'Authorization': 'Bearer ' + token.access}
		-  Response:
		   {'status': 'OK', 'message': string, 'document': json_object }
		   {'status': 'NG', 'message': string }
		   // document refers to the JSON document file uploaded in AWS S3
		   // the file has been temporarily made public at https://ft900-iot-portal.s3.amazonaws.com/latest_firmware_updates.json
		   // this API provides access to the contents of the JSON file


	16. Others

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


	17. OTA Firmware Update

		A. DOWNLOAD FIRMWARE
		-  Request:
		   GET /firmware/<device>/<filename>
		   headers: { 'Connection': 'keep-alive', 'Authorization': 'Bearer ' + authcode }
		   // authcode is computed as JWT.encode(
		      {
		        "username": string, // device uuid
		        "password": string, // device password (this is JWT encode of uuid, serialnumber, poemacaddress with shared_secret_key)
		        "iat": int,         // current time in epoch (seconds)
		        "exp": int          // expiry time in epoch (seconds), should be iat + 10
		      })
		-  Response:
		   if SUCCESS, returns binary file
		   // WARNING: This API is to be called by ESP device, not by web/mobile apps
		   // device can be ft900 or esp32
		   // if username is invalid uuid, HTTP_404_NOT_FOUND is returned
		   // if password is invalid, HTTP_401_UNAUTHORIZED
		   // if iat or exp is invalid, HTTP_401_UNAUTHORIZED and check the message
		   if FAILED, returns
		   // {'status': 'NG', 'message': string }

