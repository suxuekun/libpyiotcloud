# libpyiotcloud

libpyiotcloud demonstrates remote access or control of a microcontroller (MCU) from a web client application via iot cloud web server serving HTTPS REST APIs with backend MQTT connectivity.



### Features

    1. Access MCU remotely via HTTP REST APIs
       A. get/set GPIOs
       B. get/set RTC
       C. reset device
    2. Secure TLS connectivity [client --http over tls--> webserver <--mqtt over tls--> mqttbroker <--mqtt over tls--> MCU]
       A. http over TLS for client app and webserver communication
       B. mqtt over TLS for webserver and MCU communication
    3. Dynamically generate unique ca-signed device certificates for MCU 
       A. register_device API returns a unique device certificate + private key for the registered MCU device
       B. the generated certificates will be used by the MCU to connect to the MQTT broker. 



### Architecture

Instead of using 'serverless' IoT solutions like AWS IoT Core, GCP IoT Core or Azure IoT Hub, 
we can create our own 'server-based' IoT solutions using Flask webserver, RabbitMQ message broker and Paho-MQTT client.
This server-based IoT solution architecture can be deployed in local PC or in the cloud - AWS EC2, Linode or etc.
Note that this is a simple design and will not likely scale to millions of devices.

<img src="https://github.com/richmondu/libpyiotcloud/blob/master/images/architecture.png" width="800"/>



### Instructions

    1. Setup and run RabbitMQ broker

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
           {loopback_users, []},
           {ssl_options, [{cacertfile, "rootca.pem"},
                          {certfile,   "server_cert.pem"},
                          {keyfile,    "server_pkey.pem"},
                          {verify,     verify_peer},
                          {fail_if_no_peer_cert, false},
                          {ciphers,  ["RSA-AES128-SHA", "RSA-AES256-SHA"]} ]}
           {default_user, <<"guest">>},
           {default_pass, <<"guest">>},
           {allow_anonymous, false},
           {tcp_listeners, [1883]},
           {ssl_listeners, [8883]}
        G. Restart RabbitMQ
           >> Open RabbitMQ Command Prompt
           >> rabbitmq-service.bat stop 
           >> rabbitmq-service.bat remove
           >> rabbitmq-service.bat install
           >> rabbitmq-service.bat start
        H. Copy certificates to %APPDATA%\RabbitMQ 
           rootca.pem, server_cert.pem, server_pkey.pem

    2. Install Python and python libraries in requirements.txt

       pip install -r requirements.txt

    3. Run web_server.bat
  
    4. Run FT900 MCU

       device id: ft900device1
       device ca: rootca.pem
       device cert: ft900device1_cert.pem
       device pkey: ft900device1_pkey.pem

    5. Run client.bat



### Performance

The total round trip time for setting or getting the MCU GPIO is 2.01 seconds from the client application. But round trip time for the web server for sending MQTT publish and receiving MQTT response to/from MCU is only 1 second.

    client <-> webserver <-> mqttbroker <-> MCU: 2.01 seconds
    webserver <-> mqttbroker <-> MCU: 1.00 second
    Note: the webserver is still on my local PC, not yet on Linode or AWS EC2

The client call to HTTP getresponse() is causing the additional 1 second delay. https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection.getresponse For mobile client application, this 1 second delay maybe less or more. This will depend on the equivalent function HTTP client getresponse() in Java for Android or Swift for iOS.


