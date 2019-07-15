# libpyiotcloud

libpyiotcloud platform demonstrates a custom IoT cloud platform for secure access and control of an MCU-based smart device 
remotely from a mobile or desktop web application via REST APIs (<b>HTTP over TLS</b>) 
with back-end <b>AMQP over TLS</b> connectivity and device-side <b>MQTT over TLS</b> connectivity.


# Background

Popular cloud platforms such as Amazon Web Services, Google Cloud Platform and Microsoft Azure provide their IoT platforms, namely, [AWS IoT Core](https://aws.amazon.com/iot/), [GCP IoT Core](https://cloud.google.com/iot-core/) or [Azure IoT Hub](https://azure.microsoft.com/en-us/services/iot-hub/). There are also dedicated IoT providers such as [Adafruit.IO](https://io.adafruit.com/), [Ubidots](https://ubidots.com/) and [ThingSpeak](https://thingspeak.com/). 
These IoT platforms are good (in fact, I have tested it with FT900 - refer to [ft90x_iot_aws_gcp_azure](https://github.com/richmondu/FT900/tree/master/IoT/ft90x_iot_aws_gcp_azure). 
But these IoT platforms are limited in that they are focused on sensor data dashboarding.
This requires device to frequently send sensor data in order to generate graphs. 
It lacks support for the use-case of remote access and control memory-constrained microcontrollers.
In this use-case, the device only sends the data when queried.


# Architecture

This IoT platform is a server-based IoT cloud platform that leverages Flask, GUnicorn, Nginx, RabbitMQ, MongoDB, Amazon Cognito and Amazon Pinpoint.
It can be deployed in local PC or in the cloud - AWS EC2, Linode, Heroku, Rackspace, DigitalOcean or etc.

- Nginx web server - https://www.nginx.com/
- GUnicorn WSGI server - https://gunicorn.org/
- Flask web framework (REST API) - http://flask.pocoo.org/
- RabbitMQ message broker (MQTT, AMQP) - https://www.rabbitmq.com/
- MongoDB NoSQL database - https://www.mongodb.com/
- OpenSSL cryptography (X509 certificates) - https://www.openssl.org/
- Amazon Cognito (user sign-up/sign-in) - https://aws.amazon.com/cognito/
- Amazon Pinpoint (email/SMS notifications) - https://aws.amazon.com/pinpoint/
- Amazon SNS (email/SMS notifications) - https://aws.amazon.com/sns/

An alternative solution is using an AWS serverless solution wherein:

- AWS API Gateway+AWS Lambda will replace Flask+Gunicorn+Nginx
- AWS DynamoDB will replace MongoDB
- AmazonMQ will replace RabbitMQ


### High-level architecture diagram:
<img src="https://github.com/richmondu/libpyiotcloud/blob/master/images/architecture.png" width="1000"/>

### UML Use case diagram:
<img src="https://github.com/richmondu/libpyiotcloud/blob/master/images/usecase.png" width="800"/>

### UML Sequence diagram (user sign-up/sign-in):
<img src="https://github.com/richmondu/libpyiotcloud/blob/master/images/sequence1.png" width="800"/>

### UML Sequence diagram (device registration):
<img src="https://github.com/richmondu/libpyiotcloud/blob/master/images/sequence2.png" width="800"/>

### UML Sequence diagram (device access/control):
<img src="https://github.com/richmondu/libpyiotcloud/blob/master/images/sequence3.png" width="800"/>

### Notes:

    1. This is a simple design and will not likely scale to millions of devices.
    2. RabbitMQ supports AMQP and MQTT.
    3. For MQTT to work, MQTT plugin must be installed in RabbitMQ.
    4. Login API will return an access token that will be used for succeeding API calls.
    5. Register device API will return deviceid, rootca, device certificate and device private key.
    6. Device shall use deviceid as MQTT client id and use the rootca, device certificate and device private key.
    7. The webserver has been tested on Linux using GUnicorn.



# Design

### Features

    1. User sign-up/sign-in and Device Registration
       A. Using Amazon Cognito for user sign-up/sign-in
       B. Using MongoDB NoSQL database for storing device info during device registration
       C. Unique ca-signed certificate + privatekey generated for registered devices
    2. Device Access/Control
       A. get/set GPIOs
       B. get/set RTC
       C. get MAC address
       D. get IP/Subnet/Gateway addresses
       E. reset device
       F. write UART
    3. HTTPS/AMQPS/MQTTS Protocol Support
       [client --HTTPS--> webserver <--AMQPS--> messagebroker <--MQTTS--> device]
       A. HTTP over TLS: client app accessing REST APIs from webserver
       B. AMQP over TLS: webserver and messagebroker communication
       C. MQTT over TLS: messagebroker and device communication
    4. Device examples
       A. FT900 MCU device (LWIP-MQTT client)
       B. Python Paho-MQTT client device simulator
       C. Python Pika-AMQP client device simulator
       D. NodeJS MQTT client device simulator
    5. Email/SMS notifications
       A. Using Amazon Pinpoint
       B. Device-initiated: [device --> messagebroker --> notifmanager -> amazonpinpoint]
       C. Client-initiated: [client --> webserver --> messagebroker --> device --> messagebroker --> notifmanager -> amazonpinpoint]
 
      
### REST APIs for User Sign-up/Sign-In

    1. sign_up
       - requires username, password, email, firstname, lastname
       - confirmation code will be sent to email
    2. confirm_sign_up
       - requires username, confirmation
    3. login
       - requires username, password
       - returns access_token
    4. logout
       - requires username, access key
    5. forgot_password
       - requires email address
       - confirmation code will be sent to email
    6. confirm_forgot_password
       - requires username, new password, confirmation code

### REST APIs for Device Registration/Management

    1. register_device
       - requires username, access_token, devicename
       - returns deviceid, rootca, devicecert, devicepkey
         which shall be used on the actual microcontroller device
    2. unregister_device
       - requires username, access_token, devicename
    3. get_device_list
       - requires username, access_token
       - returns device info [devicename, deviceid, rootca, devicecert, devicepkey for all devices registered by user]
    4. get_device_list_count
       - requires username, access_token
       - returns length of device list
    5. get_device_index
       - requires username, access_token, index
       - returns device info for device[index]

### REST APIs for Device Access/Control

    1. get_gpio
    2. set_GPIO
    3. get_rtc
    4. set_rtc
    5. get_mac
    6. get_ip
    7. get_subnet
    8. get_gateway
    9. get_status
    10. set_status (including reset device)
    11. write_uart
    12. trigger_notification


### Device settings for MQTT/AMQP Connectivity

    User must first register a device in the portal. Registering a device will return deviceid, rootca, cert and pkey.
    1. HOST: ip address of RabbitMQ broker
    2. PORT: 8883 (MQTT) or 5671 (AMQP)
    3. USERNAME: guest
    4. PASSWORD: guest
    5. CLIENTID: deviceid returned by register_device API
    6. TLS ROOTCA: returned by register_device API
    7. TLS CERT: returned by register_device API
    8. TLS PKEY: returned by register_device API
    9. MQTT SUBSCRIBE: deviceid/#
    10. MQTT PUBLISH: server/deviceid/api
    11. AMQP SUBSCRIBE: mqtt-subscription-deviceidqos1
    12. AMQP PUBLISH: server.deviceid.api


### Device MQTT/AMQP Processing

    Device can either use MQTT or AMQP. For FT900 MCU device, only MQTT is currently supported.
    MQTT
    1. Subscribe to deviceid/#
    2. Receive MQTT payload with topic "deviceid/api"
    3. Parse the api
    4. Process the api with the given payload
    5. Publish answer to topic "server/deviceid/api"

    AMQP
    1. Subscribe to mqtt-subscription-deviceidqos1
    2. Receive MQTT payload with topic "deviceid.api"
    3. Parse the api
    4. Process the api with the given payload
    5. Publish answer to topic "server.deviceid.api"

### Email/SMS Notifications

    1. Device can trigger Notification Manager to send email/SMS via Amazon Pinpoint
       device -> messagebroker -> notificationmanager -> pinpoint
    2. Notification manager subscribes to topic "server/deviceid/trigger_notifications"
       Once it receives a message on this topic, it will trigger Amazon Pinpoint to send the email or SMS.
    3. Web client application can also trigger device to send email/SMS notifications via the trigger_notification REST API.
       webclient -> webserver(rest api) -> messagebroker -> device -> messagebroker -> notificationmanager -> pinpoint

# Instructions

    0. Install Python 3.6.6
       sudo apt-get install build-essential checkinstall
       sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
       cd /usr/src
       sudo wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
       sudo tar xzf Python-3.6.6.tgz
       cd Python-3.6.6
       sudo ./configure --enable-optimizations
       sudo make altinstall
       python3.6 -V

    1. Install Python and python libraries in requirements.txt

       pip install -r requirements.txt

       When running in Linux, need to install gunicorn and nginx as well
       sudo pip install gunicorn 
       sudo apt-get install nginx 
       Then setup Nginx using the links below:
       [https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04]
       [https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-16-04]
      
    2. Setup and run RabbitMQ broker

        // Installation
        A. Install Erlang http://www.erlang.org/downloads]
        B. Install RabbitMQ [https://www.rabbitmq.com/install-windows.html]
        C. Install RabbitMQ MQTT plugin [https://www.rabbitmq.com/mqtt.html]
           >> Open RabbitMQ Command Prompt
           >> rabbitmq-plugins enable rabbitmq_mqtt

        // Configuration
        D. Add environment variable RABBITMQ_CONFIG_FILE %APPDATA%\RabbitMQ\rabbitmq.config
        E. Create configuration file %APPDATA%\RabbitMQ\rabbitmq.config based on rabbitmq.config.example
        F. Update configuration file to enable the following
           {tcp_listeners, []},
           {ssl_listeners, [5671]},
           {loopback_users, []},
           {ssl_options, [{cacertfile, "rootca.pem"},
                          {certfile,   "server_cert.pem"},
                          {keyfile,    "server_pkey.pem"},
                          {verify,     verify_peer},
                          {fail_if_no_peer_cert, false},
                          {ciphers,  ["RSA-AES128-SHA", "RSA-AES256-SHA"]} ]}
           {allow_anonymous, true},
           {tcp_listeners, []},
           {ssl_listeners, [8883]}
        G. Restart RabbitMQ
           >> Open RabbitMQ Command Prompt
           >> rabbitmq-service.bat stop 
           >> rabbitmq-service.bat remove
           >> rabbitmq-service.bat install
           >> rabbitmq-service.bat start
        H. Copy certificates to %APPDATA%\RabbitMQ 
           rootca.pem, server_cert.pem, server_pkey.pem

    3. Install MongoDB database.

    4. Setup Amazon Cognito account
       A. Click on "Manage User Pools"
       B. Click on "Create a user pool"
       C. Type Pool name and click "Step through settings"
       D. Check "family name" and "given name" and click "Next step"
       E. Click "Next step"
       F. Click "Next step"
       G. Click "Next step"
       H. Click "Next step"
       I. Click "Next step"
       J. Click "Add an app client", type App client name, uncheck "Generate client secret", 
          click "Create app client" and click "Next step"
       K. Click "Next step"
       L. Click "Create pool"
   
    5. Update web_server_cognito_config.py
       A. CONFIG_USER_POOL_REGION = Region of Cognito User Pool ex. "ap-southeast-1"
       B. CONFIG_USER_POOL_ID     = Copy from General settings/Pool Id
       C. CONFIG_CLIENT_ID        = Copy from General settings/App clients/App client id

    6. Run web_server.bat

       When running in Linux, run web_server.sh

    7. Run device_simulator.py_mqtt_ft900device1.bat and device_simulator.py_mqtt_ft900device2.bat OR 
       run device_simulator.py_amqp_ft900device1.bat and device_simulator.py_amqp_ft900device2.bat OR 
       run device_simulator.js_mqtt_ft900device1.bat and device_simulator.js_mqtt_ft900device2.bat OR 
       run FT900 MCU with the following details:

       device id: ft900device1
       device ca: rootca.pem
       device cert: ft900device1_cert.pem
       device pkey: ft900device1_pkey.pem
       OR
       device id: ft900device2
       device ca: rootca.pem
       device cert: ft900device2_cert.pem
       device pkey: ft900device2_pkey.pem

    8. Run client.bat


# Testing

### MQTT/AMQP Device

- [FT900 MCU device (LWIP-MQTT client)](https://github.com/richmondu/FT900/tree/master/IoT/ft90x_iot_brtcloud)

### MQTT/AMQP Device simulators

- [Python Paho-MQTT client device simulator](https://github.com/richmondu/libpyiotcloud/blob/master/device_simulator.py)
- [Python Pika-AMQP client device simulator](https://github.com/richmondu/libpyiotcloud/blob/master/device_simulator.py)
- [NodeJS MQTT client device simulator](https://github.com/richmondu/libpyiotcloud/blob/master/device_simulator.js)

### Test utilities

- web_server_database_viewer.bat - view registered devices (MongoDB) and registered users (Amazon Cognito)



# Performance

### Windows 

The total round trip time for setting or getting the MCU GPIO is 2.01 seconds from the client application. But round trip time for the web server for sending MQTT publish and receiving MQTT response to/from MCU is only 1 second.

    client <-> webserver <-> messagebroker <-> MCU: 2.01 seconds
               webserver <-> messagebroker <-> MCU: 1.00 second
    Note: the webserver is still on my local PC, not yet on Linode or AWS EC2.

The client call to HTTP getresponse() is causing the additional 1 second delay. https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection.getresponse For mobile client application, this 1 second delay maybe less or more. This will depend on the equivalent function HTTP client getresponse() in Java for Android or Swift for iOS..

### Linux

In Linux, the total round trip time is only 1 second.


# Action Items

1. Support Docker containerization
2. Support AWS EC2 deployment
3. Support Kubernetes scalability
4. Add manager/admin page in Web client (see all users and devices registered by each user)
5. Add logging for debugging/troubleshooting
6. Access key timeout/refresh
