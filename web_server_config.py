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
    CONFIG_HTTP_TLS_CA          = "cert/rootca.pem"
    CONFIG_HTTP_TLS_CERT        = "cert/server_cert.pem"
    CONFIG_HTTP_TLS_PKEY        = "cert/server_pkey.pem"

    # Message broker credentials
    CONFIG_USERNAME             = "guest"
    CONFIG_PASSWORD             = "guest"
    CONFIG_TLS_CA               = "cert/rootca.pem"
    CONFIG_TLS_CERT             = "cert/server_cert.pem"
    CONFIG_TLS_PKEY             = "cert/server_pkey.pem"

    # Message broker settings
    CONFIG_USE_AMQP             = True
    CONFIG_HOST                 = "localhost"
    CONFIG_MQTT_TLS_PORT        = 8883
    CONFIG_AMQP_TLS_PORT        = 5671

    # Database settings
    CONFIG_DB_HOST              = "localhost"
    CONFIG_DB_PORT              = 27017
