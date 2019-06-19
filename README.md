# libpyiotcloud

libpyiotcloud demonstrates remotely accessing FT900 microcontroller (MCU) from a web client application via iot cloud web server serving HTTPS REST APIs.


### Features:

    1. Dynamically generate unique ca-signed device certificates for FT900 
    2. Access FT900 remotely via REST APIs
       A. get/set GPIOs
       B. get/set RTC
       C. reset device


### Architecture

Instead of using 'serverless' IoT solutions like AWS IoT Core, GCP IoT Core or Azure IoT Hub, 
we can create our own 'server-based' IoT solutions using Flask webserver, RabbitMQ message broker and Paho-MQTT client.
This server-based IoT solution architecture can be deployed in local PC or in the cloud - AWS EC2, Linode or etc.


### Instructions:

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
  
    4. Run FT900 microcontroller

       device id: ft900device1
       device ca: rootca.pem
       device cert: ft900device1_cert.pem
       device pkey: ft900device1_pkey.pem

    5. Run client.bat

