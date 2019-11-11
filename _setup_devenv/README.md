# Developer Guide

Below contains a step-by-step instructions on installing and setting up the frontend and backend web infrastructure of IoT Portal on local machine.


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


5. [Google Chrome](https://www.google.com/chrome/)


6. (Optional) [RabbitMQ](https://www.rabbitmq.com/download.html) 

    To be used for non-Docker version.
	Note that the configuration file needs to be updated.


7. (Optional) [MongoDB](https://www.mongodb.com/download-center/community)

    To be used for non-Docker version.


### Development Setup

1. Download the code from the repository.
 
    A. Run Docker Toolbox/Desktop as administrator.
    
    B. Type "git clone https://github.com/richmondu/libpyiotcloud"
    
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
	
    In Linux/MacOS, use export ENVIRONMENT_SYSTEM_VARIABLE="ENVIRONMENT_SYSTEM_VALUE"
    In Windows, restart the Docker Toolbox/Desktop after updating the environment variable.
	
	
3. Run the Docker images using the following commands.
    
    A. Type "cd libpyiotcloud"

    B. Type "docker-compose -f docker-compose.yml config"
    
    C. Type "docker-compose build"
	
    D. Type "docker-compose up"
    
    E. Browse https://docker-machine_ip // Refer to value of "docker-machine ip"


    // Note to stop the docker containers, do the following:
	
    F. Type "Ctrl+C"
	
    G. Type "docker-compose down"
	
    H. Type "docker-compose rm"
	
    I. Type "docker network prune -f"
	

4. Run a device simulator.

    A. Type "cd libpyiotcloud"

    // Python device simulator
    B. Type "pip install -r requirements.py.txt"
	
    C. In Windows, update HOST variable in device_simulator.py.bat to the docker-machine ip
       In Mac OS,  update HOST variable in device_simulator.py.sh to the docker-machine ip
	
    D. In Windows, run device_simulator.py.bat
       In Mac OS,  run device_simulator.py.sh
	
    E. You should see "Device is now ready! ..."
	
    // NodeJS device simulator
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
	

### Backend REST APIs

1.
2.
3.

