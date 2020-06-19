import os



class config:
    debugging = True # config for debugging locally or not , not only windows local but mac local
    # Web server settings
    # if os.name == 'nt' or "posix":
    #     debugging = True
    if debugging:
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

    # Social IDP
    CONFIG_HTTP_OAUTH2_DOMAIN   = os.environ["AWS_COGNITO_OAUTH_DOMAIN"]

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
    if debugging:
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
    CONFIG_MONGODB_USERNAME          = os.environ["CONFIG_USE_MONGODB_USER"]
    CONFIG_MONGODB_PASSWORD          = os.environ["CONFIG_USE_MONGODB_PASS"]
    if debugging:
        CONFIG_MONGODB_HOST          = "127.0.0.1"
        # CONFIG_MONGODB_HOST          = "localhost"
        # MongoDB Atlas is used for sensor-data database
        # to revert to containerized MongoDB, just set this to 127.0.0.1
        CONFIG_MONGODB_HOST2         = os.environ["CONFIG_USE_MONGODB_ATLAS"]
    else:
        CONFIG_MONGODB_HOST          = "mongodb"
        # MongoDB Atlas is used for sensor-data database
        # to revert to containerized MongoDB, just set this to mongodb
        CONFIG_MONGODB_HOST2         = os.environ["CONFIG_USE_MONGODB_ATLAS"]
    CONFIG_MONGODB_PORT              = 27017

    # Database records
    CONFIG_MONGODB_DB                        = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES               = "profiles"
    CONFIG_MONGODB_TB_DEVICES                = "devices"
    CONFIG_MONGODB_TB_HISTORY                = "history"
    CONFIG_MONGODB_TB_NOTIFICATIONS          = "notifications"
    CONFIG_MONGODB_TB_RECIPIENTS             = "recipients"
    CONFIG_MONGODB_TB_I2CSENSORS             = "i2csensors"
    CONFIG_MONGODB_TB_SUBSCRIPTIONS          = "subscriptions"
    CONFIG_MONGODB_TB_CONFIGURATIONS         = "configurations"
    CONFIG_MONGODB_TB_SENSORREADINGS         = "sensorreadings"
    CONFIG_MONGODB_TB_SENSORREADINGS_DATASET = "sensorreadingsdataset"
    CONFIG_MONGODB_TB_DEVICETOKENS           = "devicetokens"
    CONFIG_MONGODB_TB_MENOS                  = "menos"
    CONFIG_MONGODB_TB_DEVICELOCATION         = "devicelocation"
    CONFIG_MONGODB_TB_IDPTOKENS              = "idptokens"
    CONFIG_MONGODB_TB_IDPCODES               = "idpcodes"
    CONFIG_MONGODB_TB_PAYMENTTRANSACTIONS    = "paymenttransactions"
    CONFIG_MONGODB_TB_PAYMENTPAYERIDS        = "paymentpayerids"
    CONFIG_MONGODB_TB_OTAUPDATES             = "otaupdates"
    CONFIG_MONGODB_TB_DEVICEGROUPS           = "devicegroups"
    CONFIG_MONGODB_TB_ORGANIZATIONS          = "organizations"
    CONFIG_MONGODB_TB_ORGANIZATIONS_USERS    = "organizationsusers"
    CONFIG_MONGODB_TB_ORGANIZATIONS_GROUPS   = "organizationsgroups"
    CONFIG_MONGODB_TB_ORGANIZATIONS_POLICIES = "organizationspolicies"
    CONFIG_MONGODB_TB_DEFAULT_POLICIES       = "defaultpolicies"
    CONFIG_MONGODB_TB_LASTLOGIN              = "lastlogin"
    CONFIG_MONGODB_TB_LDSUS                  = "ldsus"
    CONFIG_MONGODB_TB_HEARTBEAT              = "heartbeat"

    # Caching settings
    if debugging:
        CONFIG_REDIS_HOST            = "127.0.0.1"
    else:
        CONFIG_REDIS_HOST            = "redis"
    CONFIG_REDIS_PORT                = 6379

    # Subscription/Payment
    CONFIG_SUBSCRIPTION_TYPE         = "Free"
    CONFIG_SUBSCRIPTION_PAID_TYPE    = "Paid"
    CONFIG_SUBSCRIPTION_CREDITS      = 1000
    CONFIG_TRANSACTION_QUANTITY      = 1
    CONFIG_TRANSACTION_CURRENCY      = "USD"
    CONFIG_TRANSACTION_NAME          = "Bridgetek IoT Portal credits"
    CONFIG_TRANSACTION_DESCRIPTION   = "Consumable credits for IoT Portal"

    # JWT Token
    CONFIG_JWT_SECRET_KEY_DEVICE     = os.environ["CONFIG_USE_JWT_SECRET_KEY_DEVICE"]
    CONFIG_JWT_SECRET_KEY            = os.environ["CONFIG_USE_JWT_SECRET_KEY"]
    CONFIG_JWT_EXPIRATION            = 10
    CONFIG_JWT_ADJUSTMENT            = 60

    # Heartbeat settings
    CONFIG_HEARBEAT_RATE             = 60      # 1minute: 60 seconds
    CONFIG_HEARBEAT_DAY_RANGE        = 86400   # 1day   : 60*60*24*1  seconds
    CONFIG_HEARBEAT_WEEK_RANGE       = 604800  # 7days  : 60*60*24*7  seconds
    CONFIG_HEARBEAT_MONTH_RANGE      = 2592000 # 30days : 60*60*24*30 seconds
    CONFIG_HEARBEAT_MIN_RANGE        = CONFIG_HEARBEAT_RATE
    CONFIG_HEARBEAT_MAX_RANGE        = CONFIG_HEARBEAT_MONTH_RANGE
    CONFIG_HEARBEAT_DAY_MAX          = int(CONFIG_HEARBEAT_DAY_RANGE/CONFIG_HEARBEAT_RATE)
    CONFIG_HEARBEAT_WEEK_MAX         = int(CONFIG_HEARBEAT_WEEK_RANGE/CONFIG_HEARBEAT_RATE)
    CONFIG_HEARBEAT_MONTH_MAX        = int(CONFIG_HEARBEAT_MONTH_RANGE/CONFIG_HEARBEAT_RATE)


