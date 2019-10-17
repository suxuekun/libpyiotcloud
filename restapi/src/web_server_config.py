import os



class config:

    # Web server settings
    if os.name == 'nt':
        CONFIG_HTTP_USE_TLS     = True
    else:
        CONFIG_HTTP_USE_TLS     = False # Set to False when using GUnicorn (only in Linux)
    CONFIG_HTTP_HOST            = "localhost"
    CONFIG_HTTP_PORT            = 8000
    CONFIG_HTTP_TLS_PORT        = 443
    if int(os.environ["CONFIG_USE_ECC"])==1:
        CONFIG_HTTP_TLS_CA      = "cert_ecc/rootca.pem"
        CONFIG_HTTP_TLS_CERT    = "cert_ecc/server_cert.pem"
        CONFIG_HTTP_TLS_PKEY    = "cert_ecc/server_pkey.pem"
    else:
        CONFIG_HTTP_TLS_CA      = "cert/rootca.pem"
        CONFIG_HTTP_TLS_CERT    = "cert/server_cert.pem"
        CONFIG_HTTP_TLS_PKEY    = "cert/server_pkey.pem"

    # Message broker credentials
    CONFIG_USERNAME             = None
    CONFIG_PASSWORD             = None
    if int(os.environ["CONFIG_USE_ECC"])==1:
        CONFIG_TLS_CA           = "cert_ecc/rootca.pem"
        CONFIG_TLS_CERT         = "cert_ecc/server_cert.pem"
        CONFIG_TLS_PKEY         = "cert_ecc/server_pkey.pem"
    else:
        CONFIG_TLS_CA           = "cert/rootca.pem"
        CONFIG_TLS_CERT         = "cert/server_cert.pem"
        CONFIG_TLS_PKEY         = "cert/server_pkey.pem"

    # Message broker settings
    CONFIG_USE_AMQP             = False
    if os.name == 'nt':
        CONFIG_HOST             = "127.0.0.1"
    else:
        CONFIG_HOST             = "rabbitmq"
    CONFIG_MQTT_TLS_PORT        = 8883
    CONFIG_AMQP_TLS_PORT        = 5671

    # Database settings
    if os.name == 'nt':
        CONFIG_MONGODB_HOST     = "127.0.0.1"
    else:
        CONFIG_MONGODB_HOST     = "mongodb"
    CONFIG_MONGODB_PORT         = 27017
    CONFIG_MONGODB_DB           = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES  = "profiles"
    CONFIG_MONGODB_TB_DEVICES   = "devices"
    CONFIG_MONGODB_TB_HISTORY   = "history"
