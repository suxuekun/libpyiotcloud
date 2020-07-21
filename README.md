# libpyiotcloud

libpyiotcloud is a dockerized IoT platform for secure remote access, control and management of microcontroller-based smart devices via Android/iOS hybrid mobile apps and web app with backend RESTful APIs accessing 3rd party APIs (Cognito user signup/login, Twilio SMS messaging, Nexmo SMS messaging, Pinpoint email/SMS messaging, Paypal payment gateway), integrated to containerized microservices (RabbitMQ message broker, Nginx web server, MongoDB database) and deployed to Amazon AWS EC2 utilizing Docker containerization, Kubernetes orchestration and Jenkins CI/CD automation.


# Notices

Readers are responsible for making their own independent assessment of the information in this documentation.

Warning: This github documentation is can appear as highly technical. 
It requires necessary technical experience and skills in the IoT domain, networking, security and web/mobile development to fully grasp the information. 
It would take some time to digest everything. But I've tried to simplify things in Laymans terms as much as possible. 
For any question or clarification, just message me on Skype, ftdi.richmond.umagat.


# Background

Popular cloud platforms such as Amazon Web Services, Google Cloud Platform and Microsoft Azure provide their IoT platforms, namely, [AWS IoT Core](https://aws.amazon.com/iot/), [GCP IoT Core](https://cloud.google.com/iot-core/) or [Azure IoT Hub](https://azure.microsoft.com/en-us/services/iot-hub/). There are also dedicated IoT providers such as [Adafruit.IO](https://io.adafruit.com/), [Ubidots](https://ubidots.com/) and [ThingSpeak](https://thingspeak.com/). 
These IoT platforms are good (in fact, I have tested it with FT900 - refer to [ft90x_iot_aws_gcp_azure](https://github.com/richmondu/FT900/tree/master/IoT/ft90x_iot_aws_gcp_azure). 
But these IoT platforms are limited in that they are focused on sensor data dashboarding.
This requires device to frequently send sensor data in order to generate graphs. 
It lacks support for the use-case of remote access and control memory-constrained microcontrollers.
In this use-case, the device only sends the data when queried.

Comparable IoT platforms for our use-case of remote device access and control include the IoT platforms of 

    - TP-Link (with Kasa mobile application) for TPLink smart bulbs/smart plugs, and 
    - Xiaomi (YeeLight mobile app) for Xiaomi's smart smart bulbs/smart plugs.
    - Tuya IoT platform
    - Blynk IoT platform

However, these IoT platforms are tied up to their smart devices.
This IoT platform is generic for all smart devices and IoT devices that can be build on top of any MCU, but preferably using FT9XX MCUs.

<b> 
Note: Due to requirement changes, this IoT platform has since evolved to be used entirely for the company's new IoT device used to seamlessly manage long-range sensors.
</b>


# Architecture

This IoT platform is the heart of the IoT system. 
It is the main service attachment point for the IoT platform clients and IoT devices and acts as the bridge to connect clients and devices together.
It acts as the central messaging broker that supports client to device and device to device communication.
It maintains the state of the entire system. It stores device and sensor information and all manner of device and sensor configurations and their routing information. 
It also ingests and stores the received sensor readings from the devices for real-time dashboard visualization and off-line analysis. 
It also keeps track of user details and user credit details and interfaces to 3rd party cloud systems such as identity services, alerting services, payment merchants and additional services.

All these are done securely as security is built-in from the design, not as an after-thought. Security by Design principle.
Security concerns is one of the major challenges slowing down IoT adoption. For some companies, it is mostly because of neglect than lack of skills.
Even though its impossible to defend against all sophisticated cyber-attacks, following industry-proven best practices and incorporating security and privacy in design is vital to any IoT platform. 
As security risks can never be completely eliminated, security enhancement will be an ongoing process. Incremental security improvements will be continuously applied.
Security will be enforced in an end-to-end approach, from physical devices and sensors, to data connections, to host systems, to the services and data stored in the cloud.


Below are the features of this secure, scalable and reliable IoT platform:

    1. Backend infrastructure
       Utilizes microservices architecture on AWS cloud for enabling scalability, high-availability and fault-tolerance
       A. IaaS service on reliable cloud platform using AWS EC2
       B. Containerized microservices architecture using Docker containers
       C. Reliable and scalable databases and message brokers using MongoDB, MongoDB Atlas, Redis and RabbitMQ
       D. Container orchestration tools using Docker-compose or Kubernetes (tested on Minikube and AWS EKS)
       E. Continuous integration/deployment (CI/CD) using Jenkins pipelines (automated deployment from Github to AWS EC2)
       F. Monitoring solution using Prometheus and Grafana (cAdvisor: Docker container monitoring, NodeExporter: AWS EC2 host monitoring)
       G. Logging solution using Elastic stack / ELK stack (Elasticsearch, Logstash, and Kibana)
       H. Limited ports exposed to fend off attacks in infrastructure level

    2. Device connectivity services
       Utilizes lightweight MQTT protocol for device connectivity ideal for low-powered devices and long-term reliability
       A. Device and backend communication via RabbitMQ message broker using MQTTS protocol
       B. Device authentication using unique username and JWT-encoded password (with shared secret key) credentials
       C. Device authentication using ECC-based X.509 client certificate with mutual authentication enforcement
       D. Secure communication using TLS, device athorization using MQTT topic permissions
       E. Company-generated ECC-based X.509 SSL certificates (server root certificate and client device certificates)
       F. Device simulator (Python) as reference implementation for actual IoT device

    3. Web/mobile connectivity services
       Access Portal from your desktop web browsers or mobile apps.
       A. Access from a specific domain (and subdomains) with SSL certificate/s from trusted certificate authorities
       B. Web/mobile app and backend communication via RESTful APIs using HTTPS protocol
       C. Secure communication using TLS, trusted SSL certificates, JWT authorization headers
       D. Hybrid web/mobile apps (using Ionic framework) as reference implementation for actual web/mobile clients
       E. SSL certificate registered in NGINX web server for specific domain mapped to EC2 instance using Amazon Route53

    4. Identity management services
       Access Portal in a secure way (using Amazon Cognito).
       A. User sign-up (and password reset/recovery) with secure OTP (one-time password)
       B. Login with verified email or mobile number
       C. Login with multi-factor authentication (MFA/2FA) security - disabled by default; must be explicitly enabled by user
       D. Login via social IDP (Facebook/Google/Amazon) via OAuth2 security
       E. User lockout security on consecutive failed attempts to alert suspicious behavior
       *  MFA/2FA using Google Authenticator

    5. Organization and access control management services
       Manage an organization of users and assign permissions (role-based access control aka RBAC).
       A. Create and manage an organization, adding new/existing users
       B. Group the users based on assigned tasks/roles
       C. Assign permissions policies to each user groups

    6. Alerting and messaging services
       Raise alarms over sMs, Email, push Notification, Other gateway, Storage (MENOS) so you can respond and analyze telemetry events in time.
       A. sMs: sending mobile SMS alerts via Amazon Pinpoint
       B. Email: sending email alerts via Amazon Pinpoint
       C. push Notification: sending mobile push notifications alerts to Android/IOS mobile via Amazon Pinpoint
       D. Other gateway: sending alerts to another gateway device
       E. Storage: sending alerts to Amazon S3 for file storage (user can download file for later analysis)
       F. Alert multiple registered recipients (for various combinations of sMs, Email, push Notification, Other gateway, Storage)
       *  IFTTT: trigger a 3rd-party application (like, Twitter, Facebook, Alexa, etc) via IFTTT
       *  Lambda: trigger a user-defined Python/NodeJS function for highly customized alerting

    7. Subscription and payment services
       Conveniently pay for subscription upgrade for each device to avail all services for all purchased IoT devices.
       A. Use free subscription for all purchased devices
       B. Upgrade free subscription to Basic/Pro/Enterprise subscription plans in prorated amount 
       C. Buy SMS add-ons on top of subscription plans to avail more SMS alerts
       D. Use promo codes to avail of price discounts or additional services
       E. Cancel paid subscription plan anytime and avail of the services until end of the month
       F. Use Paypal to pay for recurring subscription plan
       G. Receive email acknowledgement for payment including link to download the receipt
       H. View payment transaction histories and receipts for all purchased subscriptions and add-ons
       I. Monitor usage for SMS, email, push notifications and sensor data storage
       J. Receive email notices when alert usage or sensor data storage usage exceeded subscription plan allocation

    8. Device fleet management services
       Provision, manage and monitor devices or fleets of devices
       A. Register device manually or via QR code (QR code registration via mobile apps only)
       B. Receive email acknowledgement upon device registration and unregistration
       C. Manage device status remotely (restart, stop, start) and view device properties including last active time
       D. Configure and track location of a device (or a fleet of devices) via Google Maps (latitude, longitude)
       E. Seamlessly update firmware of a device (or fleet of devices - online and/or offline) remotely over-the-air (OTA) with secure checksum validation
       F. Organize devices into groups of devices for bulk/fleet-wide operations or for organizing several devices
       G. Scan devices to detect connected sensors/actuators (and sensors/actuators that were unplugged but were previously plugged)
       H. View device-sensor hierarchy tree and sensor configurations 
       *  Configure and manage organization-owned devices

    9. Sensor/actuator management services
       Configure sensors/actuators for customizable alerts/alarms or trigger/action
       A. Configure UART parameters
       B. Configure GPIO parameters - OBSOLETED
       C. Connect sensors/actuators via LDS Bus ports
       D. Connect sensors/actuators via I2C, ADC, TProbe, Onewire - OBSOLETED
       E. Connect sensors/actuators: 
          INPUT  [sensors]   : temperature, humidity, co2/voc gas, pressure, motion detection, ambient light
          OUTPUT [actuators] : speaker, display, light
       F. Configure sensors for data thresholding to trigger alerts
       G. Configure sensors for data thresholding to set actuators (from similar or other devices)
       H. Configure actuators to receive commands from sensors
       I. Configure sensors for data forwarding to pass values to actuators (from similar or other devices)
       J. Configure actuators to receive data from sensors

    10.Sensor data visualization and analytics services
       Understand device and sensor behaviour via the dashboard charts/graphs/infographics for complete holistic insight
       A. Ingest sensor data from sensors connected via peripherals: I2C, ADC, Onewire, TPROBE
       B. Store sensor data to a Big Data database using MongoDB Atlas
       C. Visualize real-time and historical sensor data via time-series line charts (with sensor filters, time range filter)
       D. Visualize device and sensor related metrics via pie, doughnut and bar charts
       E. Forward sensor data (forward INPUT sensor data to another OUTPUT sensor from same or different device)
       F. Threshold sensor data (trigger MENOS alerts when threshold limits are met)
       G. Download sensor data for data analysis, data backup, data recovery or data privacy
       *  Analyze sensor data using 3rd-party Business Intellegence / Analytics tools (PowerBI, Tableau, Qlik)


With IoT, the opportunities are endless. 
Below, we outline just some of the applications in which this IoT platform can used to influence outcomes, 
enhance business efficiencies and opportunities, and improve lives, in any type of businesses and industries:

- Agricultural and urban farming
- Amusement parks and recreational fields
- Data centers and facilities
- Government offices and municipals
- Hospitals and medical clinics
- Hotels and house rentals
- Industrial and manufacturing warehouses
- Logistics and transportation
- Schools and public libraries
- Stores and retail outlets
- Smart homes and smart offices


This IoT platform is a container-based IoT cloud platform that leverages 
Flask, GUnicorn, Nginx, RabbitMQ, MongoDB, Ionic, Amazon Cognito, Amazon Pinpoint, Twilio, Nexmo, Paypal, BrainTree, Docker, Kubernetes, Jenkins and many more.
It can be deployed in a local PC or in the cloud - AWS EC2, Linode, Heroku, Rackspace, DigitalOcean or etc.
The web app is made of Ionic framework so it can be compiled as Android and iOS mobile apps using one code base.

- <b>Amazon EC2</b> IaaS cloud service - https://aws.amazon.com/ec2/
- <b>Amazon Cognito</b> (sign-up/sign-in identity/authentication management with OTP, MFA/2FA, OAuth2, IdP) - https://aws.amazon.com/cognito/
- <b>Amazon S3</b> File data storage - https://aws.amazon.com/s3
- <b>Amazon Pinpoint</b> email/SMS/push notification messaging platform - https://aws.amazon.com/pinpoint/
- <b>Amazon SNS</b> email/SMS messaging platform - https://aws.amazon.com/sns/
- <b>Amazon Route 53</b> DNS domain resolution - https://aws.amazon.com/route53/
- <b>Amazon Cloudwatch</b> monitoring/alarm platform - https://aws.amazon.com/cloudwatch/
- <b>Amazon EKS</b> Kubernetes service - https://aws.amazon.com/eks/
- <b>Docker</b> containerization (dockerfiles, docker-compose) - https://www.docker.com/
- <b>Kubernetes</b> container orchestration - https://kubernetes.io/
- <b>Minikube</b> local Kubernetes cluster - https://github.com/kubernetes/minikube/
- <b>Nginx</b> web server - https://www.nginx.com/
- <b>GUnicorn</b> WSGI server - https://gunicorn.org/
- <b>Flask</b> web framework (REST API) - http://flask.pocoo.org/
- <b>RabbitMQ</b> message broker (AMQP, MQTT plugin, Management plugin) - https://www.rabbitmq.com/
- <b>MongoDB</b> NoSQL database - https://www.mongodb.com/
- <b>MongoDB Atlas</b> cloud database service - https://www.mongodb.com/cloud/atlas/
- <b>Redis</b> fast key-value data store (flexible: database, caching, mq) - https://redis.io/
- <b>Elastic stack/ELK stack</b> logging solution - https://www.elastic.co/elastic-stack/
- <b>Prometheus</b> monitoring solution - https://prometheus.io/
- <b>Grafana</b> visualization solution - https://grafana.com/
- <b>Ionic</b> mobile/web frontend framework - https://ionicframework.com/
- <b>Paypal</b> payment gateway - https://developer.paypal.com/
- <b>BrainTree</b> payment gateway - https://www.braintreepayments.com/
- <b>Apple Push Notification service (APNs)</b> for IOS push notifications
- <b>Google Firebase Cloud Messaging (FCM)</b> for Android push notifications
- <b>Apple IOS Test Flight</b> app distribution - https://developer.apple.com/testflight/
- <b>Google Firebase</b> app distribution - https://firebase.google.com/docs/app-distribution/
- <b>Google Maps Platform</b> for device location - https://developers.google.com/maps/documentation/
- <b>Chart.JS</b> Visualization charts/graphs - https://www.chartjs.org/
- <b>D3.JS</b> Visualization charts/graphs - https://observablehq.com/@d3/gallery/
- <b>GoDaddy</b> domain and SSL certificate - https://godaddy.com/
- <b>Twilio</b> SMS messaging platform - https://www.twilio.com/
- <b>Nexmo</b> SMS messaging platform - https://www.nexmo.com/


Below are tools and utilities being used:

- <b>Jenkins</b> automation for CI/CD - https://jenkins.io/
- <b>Github Desktop</b> Git application - https://desktop.github.com/
- <b>MongoDB Compass</b> GUI for MongoDB - https://www.mongodb.com/products/compass
- <b>RabbitMQ</b> Management web interface - https://www.rabbitmq.com/management.html
- <b>Beyond Compare</b> Code comparison - https://www.scootersoftware.com/
- <b>Putty</b> SSH application to access AWS EC2 - https://www.putty.org/
- <b>WinSCP</b> SSH gui application to access AWS EC2 - https://winscp.net/eng/index.php
- <b>Docker Toolbox</b> Docker installation on Windows - https://docs.docker.com/toolbox/toolbox_install_windows/
- <b>Kitematic</b> Docker GUI - https://kitematic.com/
- <b>Ionic Creator</b> - https://creator.ionic.io
- <b>Android Studio</b> (Building Ionic webapp to Androidapp) - https://developer.android.com/studio
- <b>OpenSSL</b> cryptography (X509 certificates) - https://www.openssl.org/
- <b>Postman</b> (API testing tool) - https://www.getpostman.com/
- <b>LucidChart</b> UML design diagrams - https://www.lucidchart.com/
- <b>ProjectLibre</b> Gantt Chart project management for task estimation/scheduling - https://www.projectlibre.com/
- <b>TeamViewer</b> Remote Desktop for helping team for debugging issues - https://www.teamviewer.com/en/


### High-level architecture diagram:
<img src="./_images/architecture.png" width="1000"/>

15 docker containerized microservices

1. <b>Webserver</b> - Nginx (contains SSL certificate; all requests go to NGINX; forwards HTTP requests to webapp or restapi)
2. <b>Webapp</b> - Ionic (front-end web framework that can also be compiled for Android and iOS)
3. <b>Restapi</b> - Flask with Gunicorn (back-end API called by web app and mobile apps)
4. <b>Messaging</b> - RabbitMQ (device communicates w/RabbitMQ; web/mobile apps communicates to device via RabbitMQ)
5. <b>Database</b> - MongoDB (database for storing device information for registered devices)
6. <b>Cache</b> - Redis (fast key value data store used for caching information / recording temporary information)
7. <b>Notification</b> - handles sending of email, SMS and mobile push notifications
8. <b>Historian</b> - handles saving of device requests and responses for each devices of all users
9. <b>Sensorian</b> - handles saving of sensor readings for each devices of all users
10. <b>Configuration</b> - handles providing of device configuration for each devices during device bootup
11. <b>OTAUpdate</b> - handles OTA firmware update via MQTTS
12. <b>Email</b> - handles sending of email notices
13. <b>Registration</b> - handles processing of sensor registration by device on bootup
14. <b>Heartbeat</b> - handles processing of heartbeat packets
15. <b>Download</b> - handles processing of downloading sensor data



<img src="./_images/architecture_frontend.png" width="1000"/>

<b>Front-end</b>

1. <b>Web</b>: browser -> Ionic web app -> Backend
2. <b>Android Mobile</b>: Ionic mobile app -> Backend
3. <b>IOS Mobile</b>: Ionic mobile app -> Backend
4. <b>Programming Languages:</b> Javascript and AngularJS



<img src="./_images/architecture_backend.png" width="1000"/>

<b>Back-end</b>

1. <b>Programming Languages:</b> Python
2. <b>Nginx</b> -> called by frontend, will call RestAPI or Webapp
3. <b>RestAPI</b> (Flask) -> Cognito, MongoDB, Paypal, BrainTree, RabbitMQ
4. <b>RabbitMQ</b>: accessed by restapi, device, notification service and history service
5. <b>MongoDB</b>: accessed by restapi, history, notification, sensor, configuration, otaupdate
6. <b>Redis</b>: accessed by restapi
7. <b>Notification service</b> -> RabbitMQ, MongoDB, Pinpoint
8. <b>History service</b> -> RabbitMQ, MongoDB
9. <b>Sensor service</b> -> RabbitMQ, MongoDB
10. <b>Configuration service</b> -> RabbitMQ, MongoDB
11. <b>OTAUpdate service</b> -> RabbitMQ, MongoDB
12. <b>Email service</b> -> RabbitMQ, MongoDB
13. <b>Registration service</b> -> RabbitMQ, MongoDB
14. <b>Heartbeat</b> - RabbitMQ, MongoDB
15. <b>Download</b> - RabbitMQ, MongoDB



<img src="./_images/architecture_device.png" width="1000"/>

<b>Device</b>

1. <b>Device</b> -> RabbitMQ
2. <b>Device Simulator</b> -> RabbitMQ
3. <b>Programming Languages:</b> C (for FT900), Python and NodeJS (for device simulators)



### UML Use case diagram:
<img src="./_images/usecase.png" width="800"/>

### UML Sequence diagram (user sign-up/sign-in):
<img src="./_images/sequence1.png" width="800"/>

### UML Sequence diagram (device registration):
<img src="./_images/sequence2.png" width="800"/>

### UML Sequence diagram (device access/control):
<img src="./_images/sequence3.png" width="800"/>

### UML Sequence diagram (sensor live status):
<img src="./_images/architecture_livestatus.png" width="800"/>

### UML Sequence diagram (OTA firmware update):
<img src="./_images/ota_firmware_update_sequence_diagram.png" width="800"/>

### UML Sequence diagram (login via social idp - facebook, google, amazon):
<img src="./_images/login_via_idp_sequence_diagram.png" width="800"/>

### UML Sequence diagram (paypal payment):
<img src="./_images/paypal_sequence_diagram.png" width="800"/>

### UML Sequence diagram (alerting UART):
<img src="./_images/notification_sequence_UART.png" width="1000"/>

### UML Sequence diagram (alerting GPIO):
<img src="./_images/notification_sequence_GPIO.png" width="1000"/>



### Notes:

    1. RabbitMQ supports AMQP and MQTT.
    2. For MQTT to work, MQTT plugin must be installed in RabbitMQ.
    3. Login API will return an access token that will be used for succeeding API calls.
    4. Register device API will return deviceid, rootca, device certificate and device private key.
    5. Device shall use deviceid as MQTT client id and use the rootca, device certificate and device private key.
    6. The webserver has been tested on Linux Ubuntu 16.04 using GUnicorn and Nginx.
    7. Web app: browser->nginx->ionic->gunicorn->flask ...
    8. Mobile apps: app->nginx->gunicorn->flask ...
    9. HTTPs requests from web and mobile apps goes thru NGINX which forwards requests to either Ionic web app or Gunicorn-Flask REST APIs.
    10. SSL certificate bought from GoDaddy goes to NGINX.
    11. SSL certificates are tied up with the website domain and/or subdomain.
    12. DNS A record must be modified in GoDaddy to match the public IP address of the AWS EC2 instance.
    13. Customers can directly use the (Flask) REST APIs. They can create their own front-end web/mobile apps that calls our REST APIs.



# Design

### User Interface

User signup and login
<img src="./_images/ui_loginsignup.png" width="800"/>

Device registration
<img src="./_images/ui_deviceregistration.png" width="800"/>

Device access and control
<img src="./_images/ui_deviceaccess.png" width="800"/>

Menu, account, history
<img src="./_images/ui_menuaccounthistory.png" width="800"/>

Device-sensor hierarchy charts
<img src="./_images/dashboard_charts_hierarchy.png" width="800"/>

Dashboard line charts
<img src="./_images/dashboard_charts_linechart.png" width="800"/>

Dashboard pie charts
<img src="./_images/dashboard_charts_pie.png" width="800"/>

Dashboard doughnut charts
<img src="./_images/dashboard_charts_dougnutchart.png" width="800"/>

Paypal payment redirection
<img src="./_images/paypal_payment.png" width="800"/>

Paypal payment redirection
<img src="./_images/paypal_payment_2.png" width="800"/>

Paypal payment execution and verification
<img src="./_images/paypal_payment_3.png" width="800"/>

Paypal payment email notification
<img src="./_images/paypal_payment_4.png" width="800"/>

Paypal payment buyer account
<img src="./_images/paypal_payment_5.png" width="800"/>

Paypal payment merchant account
<img src="./_images/paypal_payment_6.png" width="800"/>

MongoDB sensor data optimization -  GB datasets
<img src="./_images/benchmarking.png" width="800"/>

MongoDB sensor data optimization - indexing
<img src="./_images/benchmarking2.png" width="800"/>


### REST APIs

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
        //
        // login via social idp (facebook, google, amazon)
        O. LOGIN IDP STORE CODE           - POST   /user/login/idp/code/ID
        P. LOGIN IDP QUERY CODE           - GET    /user/login/idp/code/ID
        //
        // mfa (multi-factor authentication)
        Q. ENABLE MFA                     - POST   /user/mfa
        R. LOGIN MFA                      - POST   /user/login/mfa
        //
        // organization (member)
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
        M. GET POLICY                      - POST   organization/policies/policy/POLICYNAME
        N. CREATE/UPDATE POLICY            - POST   organization/policies/policy/POLICYNAME
        O. DELETE POLICY                   - DELETE organization/policies/policy/POLICYNAME
        P. GET POLICY SETTINGS             - GET    organization/policies/settings
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
        N. UPDATE FIRMWARE                - POST   /devices/device/DEVICENAME/firmware
        O. UPDATE FIRMWARES               - POST   /devices/firmware
        P. GET OTA STATUS                 - GET    /devices/device/DEVICENAME/ota
        Q. GET OTA STATUSES               - GET    /devices/ota
        //
        // device-sensor hierarchy tree
        R. GET DEVICE HIERARCHY TREE               - GET    /devices/device/DEVICENAME/hierarchy
        S. GET DEVICE HIERARCHY TREE (WITH STATUS) - POST   /devices/device/DEVICENAME/hierarchy

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
        B. GET LDS BUS LDSUS              - GET    /devices/device/DEVICENAME/ldsbus/PORT/ldsus
        C. GET LDS BUS SENSORS            - GET    /devices/device/DEVICENAME/ldsbus/PORT/sensors
        D. GET LDS BUS ACTUATORS          - GET    /devices/device/DEVICENAME/ldsbus/PORT/actuators
        E. SCAN LDS BUS                   - POST   /devices/device/DEVICENAME/ldsbus/PORT
        F. CHANGE LDSU NAME               - POST   /devices/device/DEVICENAME/ldsu/LDSUUUID/name
        G. IDENTIFY LDSU                  - POST   /devices/device/DEVICENAME/ldsu/LDSUUUID/identify
        H. GET LDSU                       - GET    /devices/device/DEVICENAME/ldsu/LDSUUUID
        I. DELETE LDSU                    - DELETE /devices/device/DEVICENAME/ldsu/LDSUUUID
        //
        // LDSU DEVICE refers to SENSOR or ACTUATOR
        J. SET LDSU DEVICE PROPERTIES     - POST   /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
        K. GET LDSU DEVICE PROPERTIES     - GET    /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/properties
        L. ENABLE/DISABLE LDSU DEVICE     - POST   /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/enable
        M. CHANGE LDSU DEVICE NAME        - POST   /devices/device/DEVICENAME/LDSUUUID/NUMBER/sensors/sensor/SENSORNAME/name

    6. Device access and control APIs (STATUS, UART, GPIO)
        // status
        A. GET STATUS                     - GET    /devices/device/DEVICENAME/status
        B. SET STATUS                     - POST   /devices/device/DEVICENAME/status
        // settings
        C. GET SETTINGS                   - GET    /devices/device/DEVICENAME/settings
        D. SET SETTINGS                   - POST   /devices/device/DEVICENAME/settings
        // uart
        E. GET UARTS                      - GET    /devices/device/DEVICENAME/uarts
        F. GET UART PROPERTIES            - GET    /devices/device/DEVICENAME/uart/properties
        G. SET UART PROPERTIES            - POST   /devices/device/DEVICENAME/uart/properties
        H. ENABLE/DISABLE UART            - POST   /devices/device/DEVICENAME/uart/enable
        // gpio
        I. GET GPIOS                      - GET    /devices/device/DEVICENAME/gpios
        J. GET GPIO PROPERTIES            - GET    /devices/device/DEVICENAME/gpio/NUMBER/properties
        K. SET GPIO PROPERTIES            - POST   /devices/device/DEVICENAME/gpio/NUMBER/properties
        L. ENABLE/DISABLE GPIO            - POST   /devices/device/DEVICENAME/gpio/NUMBER/enable
        M. GET GPIO VOLTAGE               - GET    /devices/device/DEVICENAME/gpio/voltage
        N. SET GPIO VOLTAGE               - POST   /devices/device/DEVICENAME/gpio/voltage
           (NUMBER can be 1-4 only and corresponds to GPIO1,GPIO2,GPIO3,GPIO4)
        // sensor readings (for dashboard)
        O. GET PERIPHERAL SENSOR READINGS                  - GET    /devices/device/DEVICENAME/sensors/readings
        P. GET PERIPHERAL SENSOR READINGS DATASET          - GET    /devices/device/DEVICENAME/sensors/readings/dataset
        Q. GET PERIPHERAL SENSOR READINGS DATASET FILTERED - POST   /devices/sensors/readings/dataset
        R. DELETE PERIPHERAL SENSOR READINGS               - DELETE /devices/device/DEVICENAME/sensors/readings
        S. DELETE PERIPHERAL SENSOR READINGS DATASET       - DELETE /devices/sensors/readings/dataset
        // sensor properties
        T. DELETE PERIPHERAL SENSOR PROPERTIES             - DELETE /devices/device/DEVICENAME/sensors/properties

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
        N. DELETE I2C DEVICES READINGS    - DELETE /devices/device/DEVICENAME/i2c/NUMBER/sensors/readings
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
        L. DELETE ADC DEVICES READINGS    - DELETE /devices/device/DEVICENAME/adc/NUMBER/sensors/readings
           (NUMBER can be 1-2 only and corresponds to ADC1,ADC2)
        M. GET ADC VOLTAGE                - GET    /devices/device/DEVICENAME/adc/voltage
        N. SET ADC VOLTAGE                - POST   /devices/device/DEVICENAME/adc/voltage

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
        L. DELETE 1WIRE DEVICES READINGS  - DELETE /devices/device/DEVICENAME/1wire/NUMBER/sensors/readings
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
        L. DELETE TPROBE DEVICES READINGS - DELETE /devices/device/DEVICENAME/tprobe/NUMBER/sensors/readings
           (NUMBER will always be 1 since there is only 1 tprobe)

    11. Device transaction recording APIs
        A. GET HISTORIES                  - GET    /devices/histories
        B. GET HISTORIES FILTERED         - POST   /devices/histories
           (filter by device name, direction, topic, date start, date end)
        C. GET MENOS HISTORIES            - GET    /devices/menos
        D. GET MENOS HISTORIES FILTERED   - POST   /devices/menos

    12. Account subscription and payment APIs
        A. GET SUBSCRIPTION               - GET    /account/subscription
        B. SET SUBSCRIPTION               - POST   /account/subscription
        C. PAYPAL SETUP                   - POST   /account/payment/paypalsetup
        D. PAYPAL EXECUTE                 - POST   /account/payment/paypalexecute
        E. PAYPAL VERIFY                  - POST   /account/payment/paypalverify

    13. Mobile services
        A. REGISTER DEVICE TOKEN          - POST   /mobile/devicetoken

    14. Supported devices and firmware updates
        A. GET SUPPORTED I2C DEVICES      - GET    /others/i2cdevices [OBSOLETED, use GET SUPPORTED SENSOR DEVICES instead]
        B. GET SUPPORTED SENSOR DEVICES   - GET    /others/sensordevices
        C. GET DEVICE FIRMWARE UPDATES    - GET    /others/firmwareupdates

    15. Others
        A. SEND FEEDBACK                  - POST   /others/feedback
        B. GET FAQS                       - GET    /others/faqs
        C. GET ABOUT                      - GET    /others/about

    16. HTTP error codes
        A. HTTP_400_BAD_REQUEST           - Invalid input
        B. HTTP_401_UNAUTHORIZED          - Invalid password or invalid/expired token
        C. HTTP_404_NOT_FOUND             - User or device not found
        D. HTTP_409_CONFLICT              - User or device already exist
        E. HTTP_500_INTERNAL_SERVER_ERROR - Internal processing error or 3rd-party API failure
        F. HTTP_503_SERVICE_UNAVAILABLE   - Device is offline/unreachable


### Device settings for MQTT/AMQP Connectivity

    User must first register a device in the portal. Registering a device will return deviceid, rootca, cert and pkey.
    1. HOST: ip address of RabbitMQ broker
    2. PORT: 8883 (MQTT) or 5671 (AMQP)
    3. USERNAME: NULL
    4. PASSWORD: NULL
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

### Email/SMS Notifications (NEW)
    1. STAND-ALONE use-case:
       User can trigger SMS/Email/Device notification via UART or GPIO
    2. APP-RELATED use-case:
       User can update the device notification recipient and message from the web/mobile apps
       
### Email/SMS Notifications (OLD)
    1. Device can trigger Notification Manager to send email/SMS via Amazon Pinpoint
       device -> messagebroker -> notificationmanager -> pinpoint
    2. Notification manager subscribes to topic "server/deviceid/trigger_notifications"
       Once it receives a message on this topic, it will trigger Amazon Pinpoint to send the email or SMS.
    3. Web client application can also trigger device to send email/SMS notifications via the trigger_notification REST API.
       webclient -> webserver(rest api) -> messagebroker -> device -> messagebroker -> notificationmanager -> pinpoint

### Push Notifications
    1. The IOS/ANDROID mobile app credentials are saved in Amazon Pinpoint UI console page.
       A. [IOS] Apple Push Notification service ("APNS"): 2 options
          Key credentials
          - Key ID - required
          - Bundle identifier - required
          - Team identifier - required
          - Authentication key (.p8 file) - required
          Certificate credentials
          - SSL certificate (.p12 file) - required
          - Certificate password (optional)
       B. [ANDROID] Google Firebase Cloud Messaging ("FCM" aka "GCM"): 1 option
          - API key - required
    2. The IOS/ANDROID mobile app generates/regenerates a unique device token whenever the app is installed/reinstalled.
       When devicetoken expires while user is loggedin, then the notification will fail. User has to relogin.
    3. The device token is used to send a push notification to that specific device.
       A. The app shall generate a unique device token for that specific mobile phone whenever the app is installed/reinstalled/expired.
       B. The app shall register the device token for that user via a new API which will be called everytime user logins.
          The backends shall store the device token on the database for that user.
          If user uses multiple Androids/IOS, and logins simulataneously, then there will be more than 1 device token for that user.
          All those mobile phone shall receive the push notifications.
       C. The app shall not display the device token on the mobile app for MENOS-related UIs.
          It shall only display **************** and not allow user to modify it.
          This is to maintain the device token to be secure. 
       D. The backend will read the device token in the database.
          If user is currently login on multiple phones, then all phones will receive push notifications.
       E. The backend shall remove all registered device token/s from the database when user logouts.  
          So no notifications will be sent to logged out user.
    4. That device token will be used for the MENOS recipient for N-otifications
       MENOS
       A. Mobile recipient: phone number
       B. Email recipient: email address
       C. Notification (push notification) recipient: device token of mobile phone (unique for every mobile phone, generated by mobile app every install/reinstall)
       D. mOdem recipient: device id of ft900 (unique for every device) 
       E. Storage recipient: TODO
   
    
# Continuous Integration/Continuous Delivery (CI/CD)

CI/CD via Jenkins has been setuped.

This continuous delivery process automates deployment, minimizes downtime and reduces maintenance cost.

- <b>Old method:</b> copy new code to EC2 => stop docker images via docker-compose down => build new docker images => run docker images

- <b>New method:</b> Fully automated with Jenkins (github => jenkins => aws ec2)


### Status

- <b>Continuous delivery</b> = OK (Jenkins SERVER on AWS EC2)

- <b>Continuous integration</b> = NG (Jenkins SERVER on local machine, TODO add automated testing)


### Features

Every commit to main branch of https://github.com/richmondu/libpyiotcloud triggers Jenkins to fetch latest code, build it, deploy to AWS EC2 and send email notifications.

- This automated triggering is done via <b>Github Webhook</b> which calls a Jenkins webhook URL. 

- <b>Email notification</b> is sent to the BRTCHIP team


### Limitations

Jenkins master is currently on the same AWS EC2 instance as the webapp

- <b>Pros:</b> cost-effective - only 1 ec2 instance for now

- <b>Cons:</b> scalable, share resources

Note: Using Kubernetes will also change the infrastracture.



# Instructions (Docker)

    0. Install Docker
    1. Set AWS credentials + cognito/pinpoint IDs as environment variables
       export AWS_ACCESS_KEY_ID=""
       export AWS_SECRET_ACCESS_KEY=""
       export AWS_COGNITO_CLIENT_ID=""
       export AWS_COGNITO_USERPOOL_ID=""
       export AWS_COGNITO_USERPOOL_REGION=""     
       export AWS_PINPOINT_ID=""
       export AWS_PINPOINT_REGION=""
       export AWS_PINPOINT_EMAIL=""
       export CONFIG_USE_ECC=1 or 0
       export PAYPAL_CLIENT_ID=""
       export PAYPAL_CLIENT_SECRET=""
       
    2. Build and execute Docker-compose file
       docker-compose build // To rebuild from scratch, add "--no-cache"
       docker-compose up // To run asynchronously as daemon, add "-d"
    3. Test by browsing https://192.168.99.100 or https://<aws_ec2_hostname> or https://<aws_ec2_ip>
    

# Manual Instructions (non-Docker)

### Install Python 3.6.6 and Python libraries

       sudo apt-get install build-essential checkinstall
       sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
       cd /usr/src
       sudo wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
       sudo tar xzf Python-3.6.6.tgz
       cd Python-3.6.6
       sudo ./configure --enable-optimizations
       sudo make altinstall
       python3.6 -V
       
       pip install -r requirements.txt


### Install Gunicorn and Nginx

       // GUNICORN
       sudo pip install gunicorn
       copy web_server.service to /etc/systemd/system
       sudo systemctl start web_server
       sudo systemctl status web_server
       sudo nano /etc/systemd/system/web_server.service
       gunicorn --bind ip:port wsgi:app // test
       
       // NGINX
       sudo apt-get install nginx
       copy web_server to /etc/nginx/sites-available
       sudo ln -s /etc/nginx/sites-available/web_server /etc/nginx/sites-enabled
       sudo nginx -t
       sudo systemctl start nginx
       sudo systemctl status nginx
       sudo nano /etc/nginx/sites-available/web_server
       
       [https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04]
       [https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-16-04]
   

### Setup and run RabbitMQ broker

        LINUX:
        
        // Installation
        A. Install Erlang
           wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
           sudo dpkg -i erlang-solutions_1.0_all.deb
           sudo apt-get update
           sudo apt-get install erlang
        B. Install RabbitMQ
           curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | sudo bash
           sudo apt-get install rabbitmq-server=3.7.16-1
        C. Install RabbitMQ MQTT plugin
           sudo rabbitmq-plugins enable rabbitmq_mqtt
        
        // Configuration
        D. Update port firewall
           sudo ufw allow 8883
           sudo ufw allow 5671
           sudo ufw deny 1883
           sudo ufw deny 5672
        E. Configure RabbitMQ
           cd /etc/rabbitmq
           sudo chmod 777 .
           copy rabbitmq.config
           copy rootca.pem
           copy server_cert.pem
           copy server_pkey.pem
        F. Check RabbitMQ 
           sudo service rabbitmq-server start
           sudo service rabbitmq-server stop
           sudo service rabbitmq-server status
           sudo service rabbitmq-server restart


        WINDOWS:
        
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
                          {ciphers,  ["RSA-AES128-SHA", "RSA-AES256-SHA"]}  ]} // RSA
                          {ciphers,  ["ECDHE-ECDSA-AES128-SHA256", "ECDHE-ECDSA-AES128-GCM-SHA256"]}  ]} // ECC
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
 
        // Ciphersuites
        I. On RabbitMQ (server)
           "RSA-AES128-SHA", "RSA-AES256-SHA" - for RSA
           "ECDHE-ECDSA-AES128-SHA256", "ECDHE-ECDSA-AES128-GCM-SHA256" - for ECC
        J. On Device (client)
           MBEDTLS_TLS_RSA_WITH_AES_128_CBC_SHA,MBEDTLS_TLS_RSA_WITH_AES_256_CBC_SHA - for RSA
           MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 - for ECC

        // RabbitMQ Clustering 
        K. Copy .erlang.cookie from C:\Windows\System32\config\systemprofile of rabbit@pc1
        L. On pc2, do the following:
            Copy .erlang.cookie of pc1 to p2 at C:\Windows\System32\config\systemprofile
            rabbitmq-server -detached
            rabbitmqctl cluster_status
            rabbitmqctl stop_app
            rabbitmqctl reset
            rabbitmqctl join_cluster rabbit@pc1
            rabbitmqctl start_app
            rabbitmqctl cluster_status
            pc2 will now be in the RabbitMQ Cluster of pc1.        
        

### Install MongoDB database.
       
       LINUX: [https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/]
       
       sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
       echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
       sudo apt-get update
       sudo apt-get install -y mongodb-org
       sudo service mongod start
       sudo nano /var/log/mongodb/mongod.log


       WINDOWS: [https://www.mongodb.com/download-center/community?jmp=docs]
       Download and run MSI installer from the link above
       Update C:\Program Files\MongoDB\Server\4.0\bin\mongod.cfg
         security:
           authorization: "enabled"
       Run C:\Program Files\MongoDB\Server\4.0\bin\mongo.exe
         Create a user using db.createUser() as specified in https://docs.mongodb.com/guides/server/auth/
       Restart MongoDB service by opening services.msc


       MONGODB COMPASS:
       Download MongoDB Compass from https://www.mongodb.com/download-center/compass
         and run MongoDBCompass.exe
         Change Authentication to Username/Password and specify both username and password fields

       MongoDB Compass is a desktop application that can connect to AWS EC2 MongoDB container via SSH to 
         This is useful for easily debugging/troubleshooting data-related issues.
         MongoDB Compass access the database via SSH, not the MongoDB port 27017,
         so exposing port 27017 in AWS EC2 security firewall was NOT necessary.
         Settings:
           AWS EC2 MongoDB container microservice
             Hostname: 127.0.0.1
             Port: 27017
             SSH Hostname: <AWS EC2 URL or IP>
             SSH Tunnel Port: <AWS EC2 SSH PORT>
             SSH Username: <AWS EC2 SSH Username>
             SSH Identity File: <AWS EC2 SSH Identity File .ppk>
           MongoDB Atlas
             Hostname: clusterX-XXXXX.mongodb.net
             Authentication: Username/Password
             Username: <username>
             Password: <password>
             More Options:
               Replica Set Name: Cluster-shard-0
               Read Preference: Primary
               SSL: Syatem CA/Atlas Deployment
               SSH Tunnel: None


### Setup Amazon Cognito.
    
       // Amazon Cognito cloud setup
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
   
       // Update environment variables
       A. AWS_COGNITO_USERPOOL_REGION = Region of Cognito User Pool ex. "ap-southeast-1"
       B. AWS_COGNITO_USERPOOL_ID     = Copy from General settings/Pool Id
       C. AWS_COGNITO_CLIENT_ID       = Copy from General settings/App clients/App client id

       // Login via Facebook/Google/Amazon
       A. App integration > App client settings
          Enabled Identity Providers: Facebook, Google, LoginWithAmazon
          Sign in and sign out URLs
            Callback URL(s)
          OAuth 2.0
            Allowed OAuth Flows: Authorization code grant, Implicit grant
            Allowed OAuth Scopes: phone, email, openid, aws.cognito.signin.user.admin
       B. Federation > Identity providers
          Facebook
            Facebook app ID
            App secret
            Authorize scope: public_profile, email
          Google
            Google app ID
            App secret
            Authorize scope: profile email openid
          Login with Amazon
            Amazon app ID
            App secret
            Authorize scope: profile
       C. Federation > Attribute mapping
          Facebook
            id: Username
            email: Email
            first_name: Given Name
            last_name: Family Name
          Google
            sub: Username
            email: Email
            given_name: Given Name
            family_name: Family Name
          Amazon
            user_id: Username
            email: Email
            name: Given Name
            ...: Family Name


### Setup Amazon Pinpoint.
    
       // Amazon Pinpoint cloud setup
       A. Click on "Create a project"
       B. Under Settings, click on "Email". 
          Under Identities tab, click Edit button.
          Select "Verify a new email address" and input "Email address".
          Check email and click on the link. 
          Get back on AWS and click Save.
       C. Under Settings, click on "SMS and voice". 
          Under SMS settings tab, click Edit button.
          Select "Enable the SMS channel for this project" and click "Save changes" button.
       D. Copy the Project ID and region for the environment variables.   
          
       // Update environment variables
       A. AWS_PINPOINT_REGION = Region of Cognito User Pool ex. "ap-southeast-1"
       B. AWS_PINPOINT_ID     = Copy from "All projects"
       C. AWS_PINPOINT_EMAIL  = Email registered to be used for email sender
       

### Others

       A. Run web_server.bat

       B. Run device_simulator.py_mqtt_ft900device1.bat and device_simulator.py_mqtt_ft900device2.bat OR 
          run device_simulator.py_amqp_ft900device1.bat and device_simulator.py_amqp_ft900device2.bat OR 
          run device_simulator.js_mqtt_ft900device1.bat and device_simulator.js_mqtt_ft900device2.bat OR 
          run FT900 MCU with the following details:

          device id: id for ft900device1
          device ca: rootca.pem
          device cert: ft900device1_cert.pem
          device pkey: ft900device1_pkey.pem

       C. Browse https://127.0.0.1 [or run client.bat for API testing]


### Certificates

       // Ciphersuites
       On RabbitMQ (server)
          "RSA-AES128-SHA", "RSA-AES256-SHA" - for RSA
          "ECDHE-ECDSA-AES128-SHA256", "ECDHE-ECDSA-AES128-GCM-SHA256" - for ECC
       On Device (client)
          MBEDTLS_TLS_RSA_WITH_AES_128_CBC_SHA,MBEDTLS_TLS_RSA_WITH_AES_256_CBC_SHA - for RSA
          MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 - for ECC

       // Notes: 
       The rootca certificate stored in RabbitMQ is for MQTT/AMQP device authentication. 
       This is different from the certificate stored in NGINX bought from GoDaddy.
       1. RabbitMQ (self-signed) ca,cert,pkey - for MQTTS/AMQPS
       2. NGINX (signed by trusted authority)cert,pkey - for HTTPS
       The certificate in RabbitMQ can be self-signed.
       But the certificate in NGINX should be signed by trusted authority for production because web browsers issues warning when server certificate is self-signed.


       // Generating self-signed certificates using OpenSSL
       A. RSA
          1. openssl genrsa -out rootCA_pkey.pem 2048
          2. openssl req -new -x509 -days 3650 -key rootCA_pkey.pem -out rootCA.pem
             Example:
             Country Name: SG
             State or Province: Singapore
             Locality: Paya Lebar
             Organization Name: Bridgetek Pte Ltd
             Organizational Unit Name: Engineering
             Common Name: brtchip.com
             Email Address: support.emea@brtchip.com

       B. ECDSA
          1. openssl ecparam -genkey -name prime256v1 -out rootCA_pkey.pem
          2. openssl req -new -sha256 -key rootCA_pkey.pem -out rootCA_csr.csr
             Example:
             Country Name: SG
             State or Province: Singapore
             Locality: Paya Lebar
             Organization Name: Bridgetek Pte Ltd
             Organizational Unit Name: Engineering
             Common Name: brtchip.com
             Email Address: support.emea@brtchip.com
          3. openssl req -x509 -sha256 -days 3650 -key rootCA_pkey.pem -in rootCA_csr.csr -out rootCA_cert.pem


       // Generating device certificates
       A. RSA
          1. openssl genrsa -out ft900device1_pkey.pem 2048
          2. openssl req -new -out ft900device1.csr -key ft900device1_pkey.pem
          3. openssl x509 -req -in ft900device1.csr -CA rootCA.pem -CAkey rootCA_pkey.pem -CAcreateserial -out ft900device1_cert.pem -days 3650

       B. ECDSA
          1. openssl ecparam -genkey -name prime256v1 -out ft900device1_pkey.pem --noout
          2. openssl req -new -out ft900device1.csr -key ft900device1_pkey.pem
          3. openssl x509 -req -in ft900device1.csr -CA rootca_cert.pem -CAkey rootca_pkey.pem -CAcreateserial -out ft900device1_cert.pem -days 3650


       // CA-certificate signed by trusted authority - Comodo, Verisign, etc.
       0. ROOTCA.pem (with a secret ROOTCA_PKEY.pem)
       
       // Customer-facing
       1. NGINX: ROOTCA.pem rootca.pkey
       2. RabbitMQ: ROOTCA.pem, server_cert.pem, server_pkey.pem
       
       // Internal
       3. WebApp: None
       4. RestAPI: server_cert.pem, server_pkey.pem
       5. Notification: ROOTCA.pem, notification_manager_cert.pem, notification_manager_pkey.pem
       
       // Device
       6. Device: ROOTCA.pem, device_X.pem, device_X.pkey


### AWS EC2

       // AWS EC2 setup
       A. Create a t2.micro instance of Amazon Linux (or Ubuntu 16.04 if not using Docker)
       B. Dowload "Private key file for authentication" for SSH access
       C. Copy the "IPv4 Public IP" address
       D. Enable ports: 22 (SSH), 8883 (MQTTS), 443 (HTTPS)

       // PUTTY setup (for SSH console access)
       A. Create PPK file from the PEM file downloaded from EC2 using PuttyGEN
       B. Using Putty, go to Category > Connection > SSH > Auth, then click Browse for "Private key file for authentication"    
       C. Set "hostname (or IP address)" to "ec2-user@IPV4_PUBLIC_IP_ADDRESS" (or "ubuntu@IPV4_PUBLIC_IP_ADDRESS" if using Ubuntu)
       
       // WINSCP setup (for SSH file transfer access)
       A. Create New Site
       B. Set "Host name:" to IPV4_PUBLIC_IP_ADDRESS
       C. Set "User name:" to ec2-user (or ubuntu if using Ubuntu)

       // Docker installation
       sudo yum update -y
       sudo yum install -y docker
       sudo usermod -aG docker ec2-user
       sudo curl -L https://github.com/docker/compose/releases/download/1.24.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
       sudo chmod +x /usr/local/bin/docker-compose
       sudo service docker restart
       restart putty
       
       // Git installation
       sudo yum update -y
       sudo yum install git -y

       // Set the AWS environment variables
       export AWS_ACCESS_KEY_ID=""
       export AWS_SECRET_ACCESS_KEY=""
       export AWS_COGNITO_CLIENT_ID=""
       export AWS_COGNITO_USERPOOL_ID=""
       export AWS_COGNITO_USERPOOL_REGION=""
       export AWS_PINPOINT_ID=""
       export AWS_PINPOINT_REGION=""
       export AWS_PINPOINT_EMAIL=""
       export CONFIG_USE_ECC=1 or 0
       export PAYPAL_CLIENT_ID=""
       export PAYPAL_CLIENT_SECRET=""
       export TWILIO_ACCOUNT_SID=""
       export TWILIO_AUTH_TOKEN=""
       export TWILIO_NUMBER_FROM=""
       export NEXMO_KEY=""
       export NEXMO_SECRET=""
       export CONFIG_USE_EMAIL_MODEL=0
       export CONFIG_USE_SMS_MODEL=0 pinpoint, 1 sns, 2 twilio, 3 nexmo
       export CONFIG_USE_CERTS="src_test/" or "src_prod/"
       export CONFIG_USE_APIURL=""

       // Download the repository
       via WinSCP or git
       
       // Docker run
       docker-compose -f docker-compose.yml config
       docker-compose build OR docker-compose build --no-cache
       docker-compose up OR docker-compose up -d
       
       // Docker stop
       docker-compose down
       docker-compose rm


### AWS Credentials

       1. AWS_ACCESS_KEY_ID
       2. AWS_SECRET_ACCESS_KEY
       3. AWS_COGNITO_CLIENT_ID
       4. AWS_COGNITO_USERPOOL_ID
       5. AWS_COGNITO_USERPOOL_REGION
       6. AWS_PINPOINT_ID
       7. AWS_PINPOINT_REGION
       8. AWS_PINPOINT_EMAIL

       // Non-AWS credentials
       CONFIG_USE_ECC
       PAYPAL_CLIENT_ID
       PAYPAL_CLIENT_SECRET
       TWILIO_ACCOUNT_SID
       TWILIO_AUTH_TOKEN
       TWILIO_NUMBER_FROM
       NEXMO_KEY
       NEXMO_SECRET
       CONFIG_USE_EMAIL_MODEL
       CONFIG_USE_SMS_MODEL
       CONFIG_USE_CERTS
       CONFIG_USE_APIURL


### Docker

        Overheads:
        1. Networking: 100 microseconds slower which is neglible. 
           [Not ideal for time-sensitive forex or stock trading market]
        2. Size: Dockers is lightweight.
        3. CPU/RAM: Virtually none on Linux.
        4. Learning: its easier than i thought, many documentations available 
           [Linux familiarity is the overhead]

        Advantages:
        1. Automates installation and deployment 
           [abstracts Linux knowledge requirements for installations/running]
        2. Automates developer/QA testing 
           [anyone can reproduce and on their own Windows 7 machine using Docker Toolbox]
        3. Simplifies maintenance and upgrade
           Dockerfile and Docker-compose file are basically Linux bash scripts
           But Dockerfile and Docker-compose file are very readable
           Easy to add/replace microservices in case needed
   
### Dockerfiles

1. The platform has been divided into 7 microservices: rabbitmq, mongodb, restapi, webapp, nginx, notification_manager, history_manager
2. Each microservice is contained in a separate docker container
3. Each docker container has a dockerfile

        // RABBITMQ Dockerfile
        FROM rabbitmq:3.7
        RUN rabbitmq-plugins enable --offline rabbitmq_management
        RUN rabbitmq-plugins enable --offline rabbitmq_mqtt
        COPY src/ /etc/rabbitmq/
        EXPOSE 5671
        EXPOSE 8883

        // MONGODB Dockerfile
        FROM mongo:latest
        VOLUME ["/data/db"]
        WORKDIR /data
        EXPOSE 27017

        // RESTAPI Flask Dockerfile
        FROM python:3.6.6
        RUN mkdir -p /usr/src/app/libpyiotcloud
        WORKDIR /usr/src/app/libpyiotcloud
        COPY libpyiotcloud/ /usr/src/app/libpyiotcloud/
        RUN pip install --no-cache-dir -r requirements.txt
        CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:8000", "--forwarded-allow-ips='*'", "wsgi:app"]
        EXPOSE 8000
        
        // WEBAPP Ionic Dockerfile
        FROM node:10.6-alpine
        RUN npm install -g ionic gulp
        RUN mkdir -p /usr/src/app/ionicapp
        WORKDIR /usr/src/app/ionicapp
        COPY src/ionicapp/ /usr/src/app/ionicapp/
        RUN npm install -D -E @ionic/v1-toolkit
        RUN npm rebuild node-sass
        CMD ["ionic", "serve", "--address=172.18.0.5", "--port=8100", "--no-open", "--no-livereload", "--consolelogs", "--no-proxy"]
        EXPOSE 8100        
        
        // NGINX Dockerfile
        FROM nginx:latest
        RUN rm /etc/nginx/conf.d/default.conf
        COPY src/ /etc/nginx/conf.d/
        EXPOSE 443

        // NOTIFICATION Dockerfile
        FROM python:3.6.6
        RUN mkdir -p /usr/src/app/notification_manager
        WORKDIR /usr/src/app/notification_manager
        COPY src/ /usr/src/app/notification_manager/
        WORKDIR /usr/src/app/notification_manager/notification_manager
        RUN pip install --no-cache-dir -r requirements.txt
        CMD ["python", "-u", "notification_manager.py", "--USE_HOST", "172.18.0.2"]

        // HISTORIAN Dockerfile
        FROM python:3.6.6
        RUN mkdir -p /usr/src/app/history_manager
        WORKDIR /usr/src/app/history_manager
        COPY src/ /usr/src/app/history_manager/
        WORKDIR /usr/src/app/history_manager/history_manager
        RUN pip install --no-cache-dir -r requirements.txt
        CMD ["python", "-u", "history_manager.py", "--USE_HOST", "172.18.0.2"]

        // CREATE and RUN
        docker network create --subnet=172.18.0.0/16 mydockernet
        docker build -t rmq .
        docker run --net mydockernet --ip 172.18.0.2 -d -p 8883:8883 -p 5671:5671 -p 15672:15672 --name rmq rmq
        docker build -t mdb .
        docker run --net mydockernet --ip 172.18.0.3 -d -p 27017:27017 -v /data:/data/db --name mdb mdb
        docker build -t api .
        docker run --net mydockernet --ip 172.18.0.4 -d -p 8000:8000 --name api api
        docker build -t app .
        docker run --net mydockernet --ip 172.18.0.5 -d -p 8100:8100 --name app app
        docker build -t ngx .
        docker run --net mydockernet --ip 172.18.0.6 -d -p 443:443 --name ngx ngx
        docker build -t nmg .
        docker run --net mydockernet --ip 172.18.0.7 -d --name nmg nmg
        docker build -t hst .
        docker run --net mydockernet --ip 172.18.0.8 -d --name hst hst

        // STOP and REMOVE
        docker ps
        docker ps -a
        docker stop rmq
        docker stop mdb
        docker stop api
        docker stop app
        docker stop ngx
        docker stop nmg
        docker stop hst
        docker rm rmq
        docker rm mdb
        docker rm api
        docker rm app
        docker rm ngx
        docker rm nmg
        docker rm hst
        docker network prune OR docker network rm mydockernet


### Dockercompose

1. Internal network created for the docker containers

        sudo docker network ls
        sudo docker network inspect mydockernet
        
        sudo docker network prune
    
2. Persistent volume for mongodb database created

        sudo docker volume ls
        sudo docker volume inspect mydockervol // get the mountpoint
        sudo ls <mountpoint>

        sudo docker volume rm $(docker volume ls -qf dangling=true)
        sudo docker volume ls -qf dangling=true

3. AWS credentials + cognito/pinpoint IDs are environment variables [no longer hardcoded in code]

        Prerequisite: set the following environment variables
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - AWS_COGNITO_CLIENT_ID
        - AWS_COGNITO_USERPOOL_ID
        - AWS_COGNITO_USERPOOL_REGION
        - AWS_PINPOINT_ID
        - AWS_PINPOINT_REGION
        - AWS_PINPOINT_EMAIL
        - CONFIG_USE_ECC=1 or 0
        - PAYPAL_CLIENT_ID
        - PAYPAL_CLIENT_SECRET
        - TWILIO_ACCOUNT_SID
        - TWILIO_AUTH_TOKEN
        - TWILIO_NUMBER_FROM
        - NEXMO_KEY
        - NEXMO_SECRET
        - CONFIG_USE_EMAIL_MODEL=0
        - CONFIG_USE_SMS_MODEL=0 pinpoint, 1 sns, 2 twilio, 3 nexmo
        - CONFIG_USE_CERTS="src_test/"
        - CONFIG_USE_APIURL

4. Docker-compose file

        // docker-compose.yml
        version: '3.7'
        services:
          rabbitmq:
            build: ./rabbitmq
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.2
            ports:
              - "8883:8883"
              - "5671:5671"
            expose:
              - "8883"
              - "5671"
            environment:
              - CONFIG_USE_ECC
          mongodb:
            build: ./mongodb
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.3
            ports:
              - "27017:27017"
            volumes:
              - "mydockervol:/data/db"
          restapi:
            build: ./restapi
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.4
            ports:
              - "8000:8000"
            depends_on:
              - rabbitmq
              - mongodb
            environment:
              - AWS_ACCESS_KEY_ID
              - AWS_SECRET_ACCESS_KEY
              - AWS_COGNITO_CLIENT_ID
              - AWS_COGNITO_USERPOOL_ID
              - AWS_COGNITO_USERPOOL_REGION
              - CONFIG_USE_ECC  
              - PAYPAL_CLIENT_ID
              - PAYPAL_CLIENT_SECRET
          webapp:
            build:
              context: ./webapp
              args:
                config_use_apiurl: ${CONFIG_USE_APIURL}
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.5
            ports:
              - "8100:8100"
            depends_on:
              - restapi
            environment:
              - CONFIG_USE_APIURL
          nginx:
            build:
              context: ./nginx
              args:
                config_use_certs: ${CONFIG_USE_CERTS}
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.6
            ports:
              - "443:443"
            expose:
              - "443"
            depends_on:
              - restapi
              - webapp
            environment:
              - CONFIG_USE_CERTS
          notification:
            build: ./notification
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.7
            depends_on:
              - nginx
            environment:
              - AWS_ACCESS_KEY_ID
              - AWS_SECRET_ACCESS_KEY
              - AWS_PINPOINT_ID
              - AWS_PINPOINT_REGION
              - AWS_PINPOINT_EMAIL
              - CONFIG_USE_ECC
              - TWILIO_ACCOUNT_SID
              - TWILIO_AUTH_TOKEN
              - TWILIO_NUMBER_FROM
              - NEXMO_KEY
              - NEXMO_SECRET
              - CONFIG_USE_EMAIL_MODEL
              - CONFIG_USE_SMS_MODEL
              - CONFIG_USE_MQTT_DEFAULT_USER
              - CONFIG_USE_MQTT_DEFAULT_PASS
          history:
            build: ./history
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.8
            depends_on:
              - rabbitmq
              - mongodb
            environment:
              - CONFIG_USE_ECC
              - CONFIG_USE_MQTT_DEFAULT_USER
              - CONFIG_USE_MQTT_DEFAULT_PASS
          sensor:
            build: ./sensor
            restart: always
            networks:
              mydockernet:
                ipv4_address: 172.18.0.9
            depends_on:
              - rabbitmq
              - mongodb
            environment:
              - CONFIG_USE_ECC
              - CONFIG_USE_MQTT_DEFAULT_USER
              - CONFIG_USE_MQTT_DEFAULT_PASS
        networks:
          mydockernet:
            driver: bridge
            ipam:
              config:
              - subnet: 172.18.0.0/16
        volumes:
          mydockervol:
            driver: local 
    
        // test
        https:// 192.168.99.100
        mqtts:// 192.168.99.100:8883
        amqps:// 192.168.99.100:5671


5. Docker-compose commands

        docker-compose -f docker-compose.yml config
        docker-compose build
        docker-compose build --no-cache // build from scratch, note: takes too long
        docker-compose up
        docker-compose up -d // run as daemon
        docker-compose ps
        docker-compose down
        docker-compose rm

        docker image ls
        docker image rm libpyiotcloud_rabbitmq // remove the rabbitmq image
        docker-compose build rabbitmq // build the rabbitmq container only


### Ionic Web/Mobile apps

        // Web app
        I utilized Ionic Creator in building the web app (that can be built as Android or iOS mobile application).

        // Android app
        To build Android mobile app using the Ionic web app requires the following:
        - Installation of [Java SE Development Kit 8](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
        - Installation of Android Studio (with Android SDK)
        - Accepting of Android SDK license
          cd %LOCALAPPDATA%\Android\sdk\tools\bin
          sdkmanager.bat --licenses
        - Build using 
          'ionic cordova build android'
        - Run on an Android emulator, 
          'ionic cordova emulate android --target=Nexus_5X_API_29_x86'
          target can be checked using %LOCALAPPDATA%\Android\sdk\tools\bin\avdmanager list avd
        - Run on an Android device
          Copy platforms\android\app\build\outputs\apk\debug\app-debug.apk
          
        // iOS app
        To build iOS mobile app using the Ionic web app requires the following:
        - MacOS
        - xcode
        - TODO


### Setup Twilio and Nexmo

#### Twilio

        // Environment Variables
        - TWILIO_ACCOUNT_SID
        - TWILIO_AUTH_TOKEN
        - TWILIO_NUMBER_FROM
        
        // Sending SMS
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(from_='xxxx', body='hello world', to='+639175900612')

#### Nexmo

        // Environment Variables
        - NEXMO_KEY
        - NEXMO_SECRET

        // Sending SMS
        import nexmo
        client = nexmo.Client(key=NEXMO_KEY, secret=NEXMO_SECRET)
        client.send_message({'from': 'Nexmo', 'to': '639175900612', 'text': 'hello world',})


### Setup Paypal

        // Setup Paypal Sandbox accounts
        - Login to https://developer.paypal.com
        - Create a Sandbox Business account (for seller) and a Sandbox Personal account (for test buyer).
        - Create a Sandbox App linked to a Sandbox business account. Copy the credentials: Client ID and Secret, to be used in the Paypal Python SDK.

        // Code flow
        - Initialize Paypal library by providing the App account credentials: Client ID and Secret.
        - Setup payment information to Paypal including a Return URL and Cancel URL callbacks. 
          A URL link will be returned pointing to Paypal page that buyer must approve transaction. 
          Once customer cancels or approves the payment, the Return URL or Cancel URL will be called. 
          If successful, the Return URL is called with the information of PayerID and PaymentID.
          Make sure that browser is allowed to open popup windows.
        - Execute payment with the specified PayerID and PaymentID.
        - Login to https://sandbox.paypal.com/ Check Sandbox Business account (for seller) to confirm the transaction and amount is credited. Check Sandbox Personal account (for test buyer) to confirm the transaction and amount is debited.

        // Moving from Sandbox to Live:
        - Developer account needs to be upgraded from personal account to business account.
        - Similar as above but replace Sandbox to Live

        // Retrieving transaction details:
        - All the transaction payments received can be retrieved in the Paypal (Business) account.
        - Each transaction contains the following:
            1. Transaction ID.
            2. Name, address and number of buyer.
            3. Date and time of transaction.
            4. Amount paid, including currency and item details.
            5. Net amount credited to paypal account (including breakdown of gross amount and paypal fee)        
        - For more details, you can access the Paypal BUSINESS test account here: https://www.sandbox.paypal.com/
            username: richmond.umagat@gmail.com
            password: xxx

        // Paypal recurring payments
        - To support monthly payment subscription, Paypal billing plans and billing agreement are used.
        - Steps:
          1. Create a billing plan.
             First month of the recurring payment: prorated based on the remaining days of the month
             - setup_fee is used instead of TRIAL period in order for Paypal charge the customer immediately.
             - if TRIAL period is used instead of setup_fee, the customer will only be charge at 10am the next day US timezone.
             Succeeding months of the recurring payment: regular amount
             - REGULAR type is used indicating Month frequency and 6-1/12-1 cycles (if 6 months or 12 months recurring)
          2. Activate the billing plan
          3. Creating a billing agreement
             - The start_date is set to the start of the next month.
          4. Execute the billing agreement.
             - The states of the billing agreement are Active, Expired, Cancelled
        - Refer to https://github.com/richmondu/libpypaypal for the demonstration of this feature.


### Setup BrainTree


### Install Jenkins (on local and on AWS EC2)
    
       // Install Jenkins using Docker
       Go to _jenkins/server
       docker-compose -f docker-compose.yml config
       docker-compose build --no-cache
       docker-compose up -d
       docker-machine ip
       browse http://DOCKERMACHINEIP:8080
       docker ps
       docker logs DOCKERJENKINSNAME // to get the password
       docker exec -it CONTAINERID /bin/bash
       cat /var/jenkins_home/secrets/initialAdminPassword // to get the password
       exit
       Set password
       Install suggested plugins


       // Install Jenkins on AWS EC2 without Docker
       sudo yum update –y
       
       A. Install Java 8
       sudo yum install -y java-1.8.0-openjdk.x86_64
       sudo /usr/sbin/alternatives --set java /usr/lib/jvm/jre-1.8.0-openjdk.x86_64/bin/java
       sudo /usr/sbin/alternatives --set javac /usr/lib/jvm/jre-1.8.0-openjdk.x86_64/bin/javac
       sudo yum remove java-1.7.0
       
       B. Install Jenkins
       sudo wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo
       sudo rpm --import https://pkg.jenkins.io/redhat/jenkins.io.key
       sudo yum install jenkins -y
       sudo service jenkins start
       
       C. Update Jenkins configuration file
       sudo vi /etc/sysconfig/jenkins
       i
       Update value of JENKINS_USER to "ec2-user"
       Update value of JENKINS_ARGS to "-Dmail.smtp.starttls.enable=true"
       Add JENKINS_JAVA_OPTIONS with "-Dmail.smtp.starttls.enable=true"
       ESC
       :x
       sudo chown -R ec2-user:ec2-user /var/lib/jenkins
       sudo chown -R ec2-user:ec2-user /var/cache/jenkins
       sudo chown -R ec2-user:ec2-user /var/log/jenkins
       sudo service jenkins restart
       
       Access http://<ec2-hostname-or-ipaddress>:<port>
       cat /var/lib/jenkins/secrets/initialAdminPassword
       
       D. Create the Jenkinsfile and commit in the repository
       https://github.com/richmondu/libpyiotcloud/blob/master/Jenkinsfile
       
       E. Create a Jenkins Pipeline
       New Item > Pipeline
       Pipeline definition: Pipeline script from SCM
       SCM: Git
       Repository URL: https://github.com/richmondu/libpyiotcloud
       Script Path: Jenkinsfile
       
       F. Set Jenkins email notification
       System Admin e-mail address: JENKINS_ADMIN@brtchip.com
       Enable Use SMTP Authentication
       SMTP server: smtp.office365.com
       Username: JENKINS_ADMIN@brtchip.com
       Password: PASSWORD OF JENKINS_ADMIN@brtchip.com
       SMTP Port: 587
       Reply-To Address: JENKINS_ADMIN@brtchip.com
       Charset UTF-8
       Set environment variables in Global Properties/environment variables       

       G. Set Github Webhook
       Go to Github project repository > Settings >  Webhooks > Edit
       Set Payload URL to the Jenkins server: http://JENKINS_URL:8080/github-webhook/
       Go to Jenkins pipeline > Build Triggers > GitHub hook trigger for GITScm polling


### Setup Amazon EKS (Kubernetes)

       // Amazon EKS (Elastic Kubernetes Services)
       - managed services to run Kubernetes on AWS without maintaining own Kubernetes server/control plane.
       - Kubernetes automates the deployment, scaling, and management of containerized applications.
       - EKS costs 0.20 USD/hour (144 USD/month) and is FREE on GCP

       // Kubernetes tools
       A. eksctl.exe is an Amazon EKS command line utility for creating and managing Kubernetes clusters on AWS.
       B. kubectl.exe is a Kubernetes command-line tool for controlling and managing Kubernetes clusters. 
       C. kompose.exe is a tool to convert Docker Compose YML file to Kubernetes orchestration YAML files.

       // How EKS works?
       A. Install AWS CLI (1.16.x), eksctl (0.7.0) and kubectl (1.14.7) tools.
       B. Create an Amazon EKS cluster and worker nodes using eksctl tool.
       C. Connect to the EKS cluster then deploy and manage apps via kubectl.

       // Setup
       A. Install and configure AWS CLI
          pip install awscli --upgrade //or https://s3.amazonaws.com/aws-cli/AWSCLI64PY3.msi
          aws configure
          -  access key id: ABC...
          -  secret access key: XYZ... 
          -  region: us-east-1
          -  output: json

       B. Install eksctl using chocolatey on admin-elevated shell
          powershell
          Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
          exit
          chocolatey install -y eksctl aws-iam-authenticator
          eksctl version

       C. Install kubectl
          powershell
          curl -o kubectl.exe https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/windows/amd64/kubectl.exe
          exit
          Copy kubectl.exe to C:\Program Files (x86)\Kubernetes
          Add C:\Program Files (x86)\Kubernetes to environment Path variable
          Reopen cmd and type "kubectl version --short --client"

       D. Install kompose
          curl -L https://github.com/kubernetes/kompose/releases/download/v1.16.0/kompose-windows-amd64.exe -o kompose.exe
          kompose.exe convert // convert docker-compose.yml to Kubernetes yaml files
        
       // Instructions:
       A. Create cluster and worker nodes via eksctl
          eksctl create cluster --help
          eksctl create cluster --name <CLUSTERNAME> --nodegroup-name <CLUSTERGRPNAME> --node-type t3.micro --nodes 2 --nodes-min 1 --nodes-max 3 --node-ami-family "AmazonLinux2"
          kubectl get svc

       B. Deploy and manage app via kubectl (using sample app)
          kubectl apply -f *.yaml
          kubectl get services
          
       C. To delete all services, deployments, volumes and replication controllers
          kubectl get svc
          kubectl get deployment
          kubectl get persistentvolumeclaim
          kubectl get rc

          kubectl delete svc/*
          kubectl delete deployment/*
          kubectl delete persistentvolumeclaim/*
          kubectl delete rc/*
          
       D. To delete the cluster and its associated worker nodes
          eksctl delete cluster --name <CLUSTERNAME>


### Setup Prometheus and Grafana for backend monitoring

       A. Download from https://github.com/stefanprodan/dockprom
          cAdvisor is for Docker container monitoring
          NodeExporter is for AWS EC2 host monitoring
       B. Change Prometheus configuration and Docker compose configuration
          Change default port for cAdvisor (conflicts with Jenkins)
          Remove settings related to alerting
       C. Run docker-compose up -d


# Production environment

### CONFIG_USE_APIURL

Dev/test: 192.168.99.100 or docker-machine ip or localhost

Production: richmondu.com or equivalent

Notes:

- This is used in webapp container, specifically in webapp\src\ionicapp\www\js\env.js


### CONFIG_USE_CERTS

Dev/test: "src_test/"

Production: "src_prod/"

Notes:

- This is used in nginx container.
- src_prod certificates are not committed for security purposes.
- src_prod must contain the cert.pem and pkey.pem must be signed by trusted certificates bought from GoDaddy.com or etc
- cert.pem and pkey.pem are usually linked to a specific domain (iotportal.brtchip.com)



# Testing and Troubleshooting

### Using FT900 (Currently tested with an FT900 RevC board-MM900EV1B only)

        1. Download the FT900 code from https://github.com/richmondu/FT900/tree/master/IoT/ft90x_iot_brtcloud
        2. Update USE_DEVICE_ID in Includes/iot_config.h to match the generated ID of the registered device in the portal
        3. Build and run FT900 code 
        4. Access/control the device via the portal

### Using device simulators

        1. Download the device simulators from https://github.com/richmondu/libpyiotcloud/tree/master/_device_simulator
           Choose from any of the 3: 
           Python-MQTT device simulator
           Python-AMQP device simulator
           Javascript-MQTT device simulator
        2. Update DEVICE_ID in the corresponding batch script to match the generated ID of the registered device in the portal
        3. Run the updated batch script
        4. Access/control the device via the portal

### Test utilities

        web_server_database_viewer.bat 
        - view registered devices (MongoDB) and registered users (Amazon Cognito)

### Testing on Windows

        Note: RabbitMQ and MongoDB should have already been installed.
        1. Run restapi\src\web_server.bat
        2. Update rest_api to 'https://localhost' in webapp\src\ionicapp\www\js\server.js
        3. Run "ionic serve" in webapp\src\ionicapp

### Troubleshooting CPU usage

        Issues:
        One of the CPU usage issues is caused by beam.smp

        Tools:
        1. AWS Cloudwatch
        2. Putty SSH
        3. MongoDB Compass
        4. RabbitMQ Management interface

        When there is CPU usage issue, AWS Cloudwatch will send email notification.
        1. Open Putty SSH and type "top" to verify CPU usage is high.
           Based on previous incidents, "beam.smp" process of RabbitMQ is causing the high CPU usage. 
        2. User RabbitMQ management tool and find the device causing issue.
        3. Open MongoDB Compass to check owner of the suspected device.
        4. Open the device in RabbitMQ.
           Delete/clear the permission of the device.
           Delete/clear the topic permission of the device.
           Change the password.
        5. Observe if the CPU goes down.
        6. Revert the changes in #4.
           Revert the permission of the device.
           Revert the topic permission of the device.
           Revert the password.

### Troubleshooting Disk usage

        df
        sudo du -x -h / | sort -h | tail -40

### Troubleshooting Docker logs

        docker ps // to get container_name
        docker logs [container_name]

        docker ps // to get container_name
        docker inspect --format="{{.Id}}" container_name // to get container_id
        cd /var/lib/docker
        sudo ls containers/container_id
        sudo cat containers/container_id/container_id-json.log

### Troubleshooting

        After restart AWS EC2 instance in AWS console:
        df
        docker ps
        sudo service docker start

        Cant stop a container?
        - docker stop container_name
        - docker rm container_name
        - docker kill container_name
        - sudo service docker stop
        - sudo service docker start

        Restart a container?
        - docker image ls
        - docker image rm libpyiotcloud_rabbitmq // remove the rabbitmq image
        - docker-compose build rabbitmq // build the rabbitmq container only

        RabbitMQ message queue
        - Use the Web interface (via HTTP)

        MongoDB database
        - Use the MongoDB Compass desktop app (via SSH)

        IP:
        - docker-machine ip
        
        Dockerized:
        - docker-compose ps
        - docker-compose down
        - docker-compose rm
        - docker ps
        - docker stop <container ID>
        - docker rm <container ID>

        https://towardsdatascience.com/slimming-down-your-docker-images-275f0ca9337e
        - docker container ls -s
        - docker image ls

        https://stackoverflow.com/questions/31909979/docker-machine-no-space-left-on-device
        - docker ps --size
        - docker system df --verbose
        - docker network ls
        - docker network prune
        - docker volume ls
        - docker volume rm $(docker volume ls -qf dangling=true)
        - docker volume ls -qf dangling=true
        - docker system prune
        
        Manual:
        - sudo service mongod status 
        - sudo systemctl status web_server
        - sudo systemctl status nginx

        Jenkins: // if jenkins URL is not accessible
        - sudo service jenkins start

        https://stackoverflow.com/questions/51493978/how-to-migrate-a-mongodb-database-between-docker-containers
        https://forums.docker.com/t/mongodb-migrating-container-to-a-different-server/72328
        - migrating mongodb database


# Performance


### Sensor Data Visualization

Querying datasets for sensor data visualization has been optimized significantly.
Performance of Sensor Dashboard API for querying a device with 1GB data (5min timerange) is now 300-1000 times faster.

Issue:

	- As the total number of sensor data collected by backend from device increases,
	  the performance of querying sensor data becomes significantly slow...
	  ...even when just querying for 5-minute timerange. 

Solution:

	- Instead of using MongoDB aggregate() framework,
	  use MongoDB's find() with combo indexing on 'sid' and 'timestamp' parameters.
	  Aggregation is supposed to be faster than find() because MongoDB performs the optimization itself.
	  However, it will be only so if usage is proper and correct.

	- https://www.stackchief.com/blog/%24lookup%20in%20MongoDB
	- https://www.stackchief.com/tutorials/$lookup%20Examples%20%7C%20MongoDB

Benchmarking:

	- Environment: 
	  local setup, Windows 7, MongoDB 4.2.8 (latest), PyMongo 3.10.1 (latest)

	- using MongoDB aggregate() - even with 'sid' indexing
	  1 enabled sensor only, 5 minute timerange
	  50MB  -   150ms
	  100MB -   250ms
	  200MB -   470ms
	  500MB -  1200ms
	  1GB   -  2300ms // 1 sensor
	  1GB   -  9700ms // 4 sensors (1 gateway)
	  1GB   - 42000ms // 8 sensors (2 gateways have 1GB each, sensor chart has sensors for 2 devices)
	  1GB   - 65000ms // 12 sensors (3 gateways have 1GB each, sensor chart has sensors for 3 devices)

	- using MongoDB find() with 'sid' & 'timestamp' combo indexing
	  1GB   -   7ms   // 1 sensor
	  1GB   -  28ms   // 4 sensors (1 gateway)
	  1GB   -  43ms   // 8 sensors (2 gateways have 1GB each, sensor chart has sensors for 2 devices)
	  1GB   -  50ms   // 12 sensors (3 gateways have 1GB each, sensor chart has sensors for 3 devices)

Other factors to consider and test:

	1. 80 max LDSUs for 1 gateway => 80x4=320 sensors (OMG!)
	2. Other timeranges
	3. 3GB, 10GB
	4. Multiple devices with 3GB/10GB (where sensor dashboard chart has sensors for all devices)
	5. Live EC2 instance (T2.SMALL)

Tradeoff:

	- The tradeoff for adding indexing is that memory increases.
	  For 1GB of data, an additional 100MB-300MB was needed by MongoDB for indexing.
	- Currently only the actual size of data is billed to customer 
	  But because the size of indexes affects size significantly, we should pass this to customer.
	  That is for 1GB Basic Plan, user will only be able to use about 700-900MB 
	  as 100-300MB will be used for indexes optmization.


### Collection metrics

	- https://docs.mongodb.com/manual/reference/command/collStats/#dbcmd.collStats
	- collStats.count
	- collStats.size
	- collStats.totalIndexSize


### Device communication

#### Windows 

The total round trip time for setting or getting the MCU GPIO is 2.01 seconds from the client application. But round trip time for the web server for sending MQTT publish and receiving MQTT response to/from MCU is only 1 second.

    client <-> webserver <-> messagebroker <-> MCU: 2.01 seconds
               webserver <-> messagebroker <-> MCU: 1.00 second
    Note: the webserver is still on my local PC, not yet on Linode or AWS EC2.

The client call to HTTP getresponse() is causing the additional 1 second delay. https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection.getresponse For mobile client application, this 1 second delay maybe less or more. This will depend on the equivalent function HTTP client getresponse() in Java for Android or Swift for iOS..

#### Linux

In Linux, the total round trip time is only 1 second.



# Security

Security has been the most challenging and controversial issues of IoT devices and smart devices.
As such this IoT platform was designed so that security is built-in from the design - Security by Design principle.
Below are security features by backend for device connectivity and frontend connectivity.

### Device connectivity

    1. MQTT connectivity over secured TLS connection
    2. ECC-based (Elliptic Curve Cryptography ECC) PKI and X.509 certificates
    3. Enforcement of mutual authentication on both MQTT broker and MQTT client configurations
    4. Unique MQTT credentials (username and password) per device where password is JWT-encoded with shared secret key
    5. Strict restrictions for MQTT topic permission (subscribe and publish) per device
    6. ECC certificates stored in 3rd-party ATECC hardware chip 
    7. Secure boot with 256-bit AES key stored in an eFuse block to prevent tampered firmware
    8. Flash encryption to prevent copying SPI Flash contents (bootloader, partition table, app partitions) via eFuses

### Frontend connectivity

    1. HTTP connectivity over secured TLS connection
    2. Cognito OAuth2 authorization with OTP and MFA/2FA via email and SMS
    3. HTTP authentication header with JWT encoding and secret key
    4. User lockout after 5 consecutive failed attempts



# Youtube screen recordings

1.  IoT Portal EW2020 demo stress test with device simulators
    https://www.youtube.com/watch?v=xkrd0WblCaI
2.  IoT Portal demo google maps
    https://www.youtube.com/watch?v=QCfKW3920vI
3.  IoT Portal demo login with facebook, google, amazon
    https://www.youtube.com/watch?v=RC_CiUj8W5s
4.  IoT Portal demo google maps move device markers
    https://www.youtube.com/watch?v=PngyKmgQ7Cs
5.  IoT Portal demo ota firmware update with device simulator
    https://www.youtube.com/watch?v=pWtfvcHW0Ho
6.  IoT Portal demo paypal payment
    https://www.youtube.com/watch?v=IGGst_aGHfw
7.  IoT Portal demo ota firmware update offlinedevices and devicefleet
    https://www.youtube.com/watch?v=ZZNlmFEPPTg
8.  IoT Portal demo storage for menos
    https://www.youtube.com/watch?v=ObWsEfADTi0
9.  IoT Portal demo dashboard
    https://www.youtube.com/watch?v=cx_AiyG4aDM
10. IoT Portal demo dashboard with time range
    https://www.youtube.com/watch?v=xg88WW7UkAo
11. IoT Portal demo device groups
    https://www.youtube.com/watch?v=NMFiBhFnmCc
12. IoT Portal demo login with multi-factor authentication (MFA)
    https://www.youtube.com/watch?v=_bSppoJqgdc
13. IoT Portal demo dashboard with dougnut charts
    https://www.youtube.com/watch?v=1VNFLBg30-w
14. IoT Portal demo device hierarchy charts using D3.js
    https://www.youtube.com/watch?v=-SxLFtULwOc
15. IoT Portal demo organizations users
    https://www.youtube.com/watch?v=Hk1-3qi2Ok8
16. IoT Portal demo organizations groups
    https://www.youtube.com/watch?v=vFWb-CcLJOI
17. IoT Portal demo multiple organizations
    https://www.youtube.com/watch?v=YId8GmpC1dk&t=7s
18. IoT Portal demo organization policies
    https://www.youtube.com/watch?v=cJG0VGHoLug
19. IoT Portal demo multiple organizations resources
    https://www.youtube.com/watch?v=k35sWhx6SL4



# Reminders

    1. When using self-signed certificate on NGINX,
       The Ionic iOS/Android mobile simulators can be viewed online at https://creator.ionic.io/share/xxxASKMExxx but requires the following
       - "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --ignore-certificate-errors
       - OR type in browser chrome://flags/#allow-insecure-localhost
    2. The certificate bought from GoDaddy is different from the self-signed certificate for RabbitMQ.
       - RABBITMQ: Uses the self-signed rootca; for MQTTS/AMQPS device connectivity
       - NGINX: Uses the trusted certificate bought from GoDaddy; for HTTPS web/mobile connectivity; currently tied up to richmondu.com



# Action Items

Below are the Post EW2020 Demo and new requirements:

    1.  [DONE] API for changing devicename 
    2.  [DONE] Optimized output format for sensor charting APIs ( x[], y[] arrays instead of [(x,y), ...] )
    2.  [DONE] OTA firmware update (HTTPS or MQTTS, CRC32)
    3.  [DONE] Google Maps Platform location (drag and drop markers to change device location)
    4.  [DONE] Login via social accounts (Facebook, Google, Amazon)
    5.  [DONE] Record Paypal transactions, Paypal API cleanup
    6.  [DONE] Login via (an OTP-verified) phone number
    7.  [DONE] OTA firmware update for an OFFLINE device
    8.  [DONE] OTA firmware update for a FLEET of devices
    9.  [DONE] "S"torage for MENOS messaging using Amazon S3
    10. [DONE] Utilize REDIS for key value store, caching and message passing
    11. [DONE] Custom filtering of sensors in dashboard (filter by devicename, peripheral, class, status)
    12. [DONE] Dedicated database for BIG DATA (days, weeks, months, years) sensor data dashboards using MongDB Atlas 
    13. [DONE] Sensor dashboarding for days, weeks, months, years (with aggregation like financial stocks)
    14. [DONE] User lockdown security for consecutive failed login attempts (prevent brute force hacking)
    15. [DONE] Email confirmation for payment receipt/invoice
    16. [DONE] Automated sensor registration on device bootup (for sensor scanning feature)
    17. [DONE] Email confirmation for payment receipt/invoice
    18. [DONE] Modem/device groups
    19. [DONE] Login with Multi-Factor Authentication (MFA)
    20. [DONE] Dashboard pie, doughnut and bar charts 
    21. [DONE] Dashboard tables for device and sensor configurations
    22. [DONE] Device-sensor hierarychy/tree charts (using D3.js)
    23. [DONE] Users management for Organization feature
    24. [DONE] File logging in device simulator (as requested by QA for easy bug reporting) 
    25. [DONE] Groups/Roles management for Organization feature
    26. [DONE] Device authentication with JWT-encoded password for enhanced security
    27. [DONE] Backend monitoring solution using Prometheus and Grafana for better maintainability
    28. [DONE] Backend logging solution using custom Python script (sufficient for now)
    29. [DONE] Multiple organizations
    30. [DONE] Policies management for Organization feature
    31. [DONE] Enforcement of organization membership in all APIs
    32. [DONE] Paypal payment recurring payments for 3/6/12 months monthly subscription

    33. GET/SET PROPERTIES cache
    34. New payment model (monthly, add-on)
    35. Highly-customizable dashboard
    36. Dashboard usage-related info
    37. Dashboard overlay charts from different sensors from same or other devices
    38. Business Intelligence integration with Microsoft PowerBI (or Tableau, Qlik)
    39. Write regression tester
    40. Microservices documentation
    41. Databases documentation
    42. Swagger REST API documentation
    43. Optimize MongoDB calls (utilize Redis, query by username or deviceid instead of by sensors if possible)
    44. Apache Hadoop integration using Amazon EMR for legit BigData database (instead of MongoDB Atlas)
    45. "L"ambda function integration for MENLOS for custom messaging/notifications (support both Python 3, NodeJS)
    46. IFTTT integration. (requires OAuth2 server and APIs implemented for triggers "if this" and actions "then-that" )
    47. Clustering of RabbitMQ and REST APIs... (study federation/shovel, clustering is for LAN, federation/shovel is for WAN)
    48. Update the Kubernetes support (a number of microservices has been added since then).

