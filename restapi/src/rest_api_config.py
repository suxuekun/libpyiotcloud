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
    CONFIG_USERNAME             = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_PASSWORD             = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]
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
    CONFIG_MGMT_TLS_PORT        = 15671
    CONFIG_MGMT_PORT            = 15672
    CONFIG_MGMT_ACCOUNT         = "{}:{}".format(os.environ["CONFIG_USE_MQTT_DEFAULT_USER"], os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"])
    CONFIG_ENABLE_MQ_SECURITY   = True

    # Database settings
    if os.name == 'nt':
        CONFIG_MONGODB_HOST         = "127.0.0.1"
    else:
        CONFIG_MONGODB_HOST         = "mongodb"
    CONFIG_MONGODB_PORT             = 27017
    CONFIG_MONGODB_DB               = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES      = "profiles"
    CONFIG_MONGODB_TB_DEVICES       = "devices"
    CONFIG_MONGODB_TB_HISTORY       = "history"
    CONFIG_MONGODB_TB_NOTIFICATIONS = "notifications"
    CONFIG_MONGODB_TB_RECIPIENTS    = "recipients"
    CONFIG_MONGODB_TB_I2CSENSORS    = "i2csensors"
    CONFIG_MONGODB_TB_SUBSCRIPTIONS = "subscriptions"
    CONFIG_MONGODB_TB_TRANSACTIONS  = "transactions"

    # Subscription/Payment
    CONFIG_SUBSCRIPTION_TYPE       = "Free"
    CONFIG_SUBSCRIPTION_PAID_TYPE  = "Paid"
    CONFIG_SUBSCRIPTION_CREDITS    = "1000"
    CONFIG_TRANSACTION_QUANTITY    = 1
    CONFIG_TRANSACTION_CURRENCY    = "USD"
    CONFIG_TRANSACTION_NAME        = "Bridgetek IoT Portal credits"
    CONFIG_TRANSACTION_DESCRIPTION = "Consumable credits for IoT Portal"

    # JWT Token
    CONFIG_JWT_SECRET_KEY          = os.environ["CONFIG_USE_JWT_SECRET_KEY"]
    CONFIG_JWT_EXPIRATION          = 10
    CONFIG_JWT_ADJUSTMENT          = 60
