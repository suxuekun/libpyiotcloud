# Developer Guide

Below contains a step-by-step instructions on installing and setting up the frontend and backend web infrastructure of <b>IoT Portal on local machine</b>.

It also contains the documentation of <b>REST APIs</b> useful for native Android/IOS mobile app development.


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

    C. Type <b>"docker-machine ip"</b>
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
    
    C. Type "docker-compose build" <b>// To rebuild from scratch, add "--no-cache"</b>
    
    D. Type "docker-compose up" <b>// To run asynchronously, add "-d"</b>
    
    E. Open a browser and browse https://docker-machine_ip <b>// Refer to value of "docker-machine ip"</b>


    <b>// Note to stop the docker containers, do the following:</b>
    
    F. Type "Ctrl+C"
    
    G. Type "docker-compose down"
    
    H. Type "docker-compose rm"
    
    I. Type "docker network prune -f"
    

4. Run a device simulator.

    A. Type "cd _device_simulator"


    <b>// PYTHON device simulator</b>
    
    B. Type "pip install -r requirements.py.txt"
    
    C. In Windows, update HOST variable in <b>device_simulator.py.bat</b> to the docker-machine ip
      
       In Mac OS,  update HOST variable in device_simulator.py.sh to the docker-machine ip
    
    D. In Windows, run <b>device_simulator.py.bat</b>
       
       In Mac OS,  run device_simulator.py.sh
    
    E. You should see "Device is now ready! ..."
    

    <b>// NODEJS device simulator</b>
    
    F. Type "npm install -g mqtt" 
    
    G. Type "npm install -g argparse" 
    
    H. Type "npm install -g system-sleep" 
    
    I. Type "npm install -g os" 
    
    J. Type "npm install -g fs"

    K. In Windows, update HOST variable in <b>device_simulator.js.bat</b> to the docker-machine ip
       
       In Mac OS,  update HOST variable in device_simulator.js.sh to the docker-machine ip
    
    L. In Windows, run <b>device_simulator.js.bat</b>
       
       In Mac OS,  run device_simulator.js.sh    
    
    M. You should see "Device is now ready! ..."


### REST API Documentation

Note that HTTP GET method requires no payload so username and token must be included in the URL path. 

1. <b>User sign-up/sign-in</b>

    A. SIGN-UP

    -  Request:

       POST <b>/user/signup</b>

       { 'username': string, 'password': string, 'email': string, 'givenname': string, 'familyname': string }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}


    B. CONFIRM SIGN-UP

    -  Request:

       POST <b>/user/confirm_signup</b>

       { 'username': string, 'confirmationcode': string }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}


    C. RESEND CONFIRMATION CODE

    -  Request:

       POST <b>/user/resend_confirmation_code</b>

       { 'username': string }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}


    D. FORGOT PASSWORD

    -  Request:

       POST <b>/user/forgot_password</b>

       { 'email': string }

    -  Response:

       {'status': 'OK', 'message': string, 'username': string}

       {'status': 'NG', 'message': string}


    E. CONFIRM FORGOT PASSWORD

    -  Request:

       POST <b>/user/confirm_forgot_password</b>

       { 'username': string, 'confirmationcode': string, 'password': string }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}


    F. LOGIN

    -  Request:

       POST <b>/user/login</b>

       { 'username': string, 'password': string }

    -  Response:

       {'status': 'OK', 'token': {'access': string, 'id': string, 'refresh': string} }

       {'status': 'NG', 'message': string}


    G. LOGOUT

    -  Request:

       POST <b>/user/logout</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}


    H. GET USER INFO

    -  Request:

       GET <b>/user/USERNAME</b>

       headers: {'Authorization': 'Bearer ' + token.access}

    -  Response:

       {'status': 'OK', 'message': string, 'info': {'email': string, 'family_name': string, 'given_name': string} }

       {'status': 'NG', 'message': string}



2. <b>Account subscription and payment</b>

    A. GET SUBSCRIPTION

    -  Request:

       GET /user/USERNAME/subscription

       headers: {'Authorization': 'Bearer ' + token.access}

    -  Response:

       {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }

       {'status': 'NG', 'message': string}


    B. SET SUBSCRIPTION

    -  Request:

       POST <b>/user/subscription</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string, 'token': {'access': string, 'id': string, 'refresh': string}, 'credits': string }

    -  Response:

       {'status': 'OK', 'message': string, 'subscription': {'credits': string, 'type': paid} }

       {'status': 'NG', 'message': string}


    C. PAYPAL SETUP

    -  Request:

       POST <b>/user/payment/paypalsetup</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string, 'payment': {'return_url': string, 'cancel_url', string, 'item_sku': string, 'item_credits': string, 'item_price': string} }

    -  Response:

       {'status': 'OK', 'message': string, , 'approval_url': string, 'paymentId': string, 'token': string}

       {'status': 'NG', 'message': string}


    D. PAYPAL EXECUTE

    -  Request:

       POST <b>/user/payment/paypalexecute</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string, 'payment': {'paymentId': string, 'payerId': string, 'token': string} }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}


    E. PAYPAL VERIFY

    -  Request:

       POST <b>/user/payment/paypalverify</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string, 'payment': {'paymentId': string} }

    -  Response:

       {'status': 'OK', 'message': string}

       {'status': 'NG', 'message': string}



3. <b>Device registration and management</b>

    A. GET DEVICES

    -  Request:

       GET <b>/user/USERNAME/ACCESS/devices</b>

       headers: {'Authorization': 'Bearer ' + token.access}

    -  Response:
       { 'status': 'OK', 'message': string, 
         'devices': array[{'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}, ...]}

       { 'status': 'NG', 'message': string}


    B. ADD DEVICE

    -  Request:

       POST <b>/devices/device</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string, 'devicename': string }

    -  Response:

       { 'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey, 'ca': ca}}

       { 'status': 'NG', 'message': string}


    C. DELETE DEVICE

    -  Request:

       DELETE <b>/devices/device</b>

       headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

       { 'username': string, 'devicename': string }

    -  Response:
    
       { 'status': 'OK', 'message': string}
       
       { 'status': 'NG', 'message': string}


    D. GET DEVICE

    -  Request:
    
       GET <b>/user/USERNAME/ACCESS/devices/device/DEVICENAME</b>

       headers: {'Authorization': 'Bearer ' + token.access}

    -  Response:
    
       { 'status': 'OK', 'message': string, 'device': {'devicename': string, 'deviceid': string, 'cert': cert, 'pkey': pkey}}
       
       { 'status': 'NG', 'message': string}



4. <b>Device access and control</b>

    A. GET DEVICE TRANSACTION HISTORIES

    -  Request:
    
       GET <b>/user/USERNAME/devices/histories</b>

       headers: {'Authorization': 'Bearer ' + token.access}

       { 'username': string }

    -  Response:
    
       { 'status': 'OK', 'message': string, 
         'histories': array[
           {'devicename': string, 'deviceid': string, 'direction': string, 'topic': string, 'payload': string, 'timestamp': string}, ...]}
           
       { 'status': 'NG', 'message': string}


    B. GET STATUS

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/status</b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    C. SET STATUS

    - Request:

      POST <b>/devices/device/status</b>

      headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

      { 'username': string, 'devicename': string, 'value': string }

    - Response:

      { 'status': 'OK', 'message': string, 'value': string}

      { 'status': 'NG', 'message': string}


    D. GET IP

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/ip</b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    E. GET SUBNET

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/subnet</b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    F. GET GATEWAY

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/gateway</b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    G. GET MAC

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/mac</b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    H. GET GPIO

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/gpio/<number></b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    I. SET GPIO

    - Request:

      POST <b>/devices/device/gpio</b>

      headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

      { 'username': string, 'devicename': string, 'number': string, 'value': string }

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    J. GET RTC

    - Request:

      GET <b>/user/USERNAME/devices/device/DEVICENAME/rtc</b>

      headers: {'Authorization': 'Bearer ' + token.access}

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    K. SET UART

    - Request:

      POST <b>/devices/device/uart</b>

      headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

      { 'username': string, 'devicename': string, 'value': string }

    - Response:

      { 'status': 'OK', 'message': string, 'value': string }

      { 'status': 'NG', 'message': string}


    L. SET NOTIFICATION

    - Request:

      POST <b>/devices/device/notification</b>

      headers: {'Authorization': 'Bearer ' + token.access, 'Content-Type': 'application/json'}

      { 'username': string, 'devicename': string, 'recipient': string, 'message': string }

    - Response:

      { 'status': 'OK', 'message': string}

      { 'status': 'NG', 'message': string}





### Database Documentation

1. TODO

