# Developer Guide

Below contains a step-by-step instructions on installing and setting up the frontend and backend web infrastructure of <b>IoT Portal on local machine</b>.

It also contains the documentation of <b>REST APIs<b> useful for native Android/IOS mobile app development.


### Development Tools

1. Github Desktop

    A. [Windows](https://central.github.com/deployments/desktop/desktop/latest/win32)
    
    B. [Mac OS](https://central.github.com/deployments/desktop/desktop/latest/darwin)

   
2. Docker Toolbox or Docker Desktop

    A. Windows 7 - [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)
    
    B. Windows 10 Home - [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)
    
    C. Windows 10 Pro - [Docker Desktop](https://docs.docker.com/docker-for-windows/) 
    
    D. Mac OS - [Docker Desktop](https://docs.docker.com/docker-for-mac/)

    Note that I'm using both A and B on my PC and laptop, respectively.


3. Python 3.X.X

    A. [Windows](https://www.python.org/downloads/windows/)
    
    B. [Mac OS](https://www.python.org/downloads/mac-osx/)   


4. NodeJS 12.X.X

    A. [Windows](https://nodejs.org/dist/v12.13.0/node-v12.13.0-x64.msi)
    
    B. [Mac OS](https://nodejs.org/dist/v12.13.0/node-v12.13.0.pkg)


5. (Optional) [RabbitMQ](https://www.rabbitmq.com/download.html) 

    To be used for non-Docker version.
    Note that the configuration file needs to be updated. Refer to <b>rabbitmq.config</b> and <b>cert_ecc</b> folder in libpyiotcloud/rabbitmq/src


6. (Optional) [MongoDB](https://www.mongodb.com/download-center/community)

    To be used for non-Docker version.


### Development Setup

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

    <b>// User sign-up/sign-in</b>

    A. SIGN-UP

    -  Request:
       POST /user/signup
       { 'username': string, 'password': string, 'email': string, 'givenname': string, 'familyname': string }

    -  Response:
       {'status': 'OK', 'message': string}
       {'status': 'NG', 'message': string}


    B. CONFIRM SIGN-UP

    -  Request:
       POST /user/confirm_signup
       { 'username': string, 'confirmationcode': string }

    -  Response:
       {'status': 'OK', 'message': string}
       {'status': 'NG', 'message': string}


    C. RESEND CONFIRMATION CODE

    -  Request:
       POST /user/resend_confirmation_code
       { 'username': string }

    -  Response:
       {'status': 'OK', 'message': string}
       {'status': 'NG', 'message': string}


    D. FORGOT PASSWORD

    -  Request:
       POST /user/forgot_password
       { 'email': string }

    -  Response:
       {'status': 'OK', 'message': string, 'username': string}
       {'status': 'NG', 'message': string}


    E. CONFIRM FORGOT PASSWORD

    -  Request:
       POST /user/confirm_forgot_password
       { 'username': string, 'confirmationcode': string, 'password': string }

    -  Response:
       {'status': 'OK', 'message': string}
       {'status': 'NG', 'message': string}


    F. LOGOUT

    -  Request:
       POST /user/logout
       { 'username': string, 'token': {'access': string, 'id': string, 'refresh': string} }

    -  Response:
       {'status': 'OK', 'message': string}
       {'status': 'NG', 'message': string}


    G. GET USER INFO

    -  Request:
       POST /user/logout
       { 'username': string, 'token': {'access': string, 'id': string, 'refresh': string} }

    -  Response:
       {'status': 'OK', 'message': string, 'info': {} }
       {'status': 'NG', 'message': string}










