import os



class config:

    debugging = int(os.environ['CONFIG_USE_DEBUG_MODE'])
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
        # CONFIG_HOST             = "192.168.99.100"
        CONFIG_HOST             = "localhost"
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

    CONFIG_MONGODB_TB_LASTLOGIN              = "login_lastlogin"
    CONFIG_MONGODB_TB_IDPTOKENS              = "login_idptokens"
    CONFIG_MONGODB_TB_IDPCODES               = "login_idpcodes"

    CONFIG_MONGODB_TB_DEVICES                = "devices"
    CONFIG_MONGODB_TB_HISTORY                = "devices_history"
    CONFIG_MONGODB_TB_DEVICETOKENS           = "devices_tokens"
    CONFIG_MONGODB_TB_OTAUPDATES             = "devices_otaupdates"
    CONFIG_MONGODB_TB_DEVICEGROUPS           = "devices_groups"
    CONFIG_MONGODB_TB_LDSUS                  = "devices_ldsus"
    CONFIG_MONGODB_TB_HEARTBEAT              = "devices_heartbeat"
    CONFIG_MONGODB_TB_DEVICELOCATION         = "devices_location"

    CONFIG_MONGODB_TB_I2CSENSORS             = "sensors"
    CONFIG_MONGODB_TB_NOTIFICATIONS          = "sensors_notifications"
    CONFIG_MONGODB_TB_CONFIGURATIONS         = "sensors_configurations"
    CONFIG_MONGODB_TB_SENSORREADINGS         = "sensors_readings_latest"
    CONFIG_MONGODB_TB_SENSORREADINGS_DATASET = "sensors_readings_dataset"
    CONFIG_MONGODB_TB_MENOS                  = "sensors_menos"

    CONFIG_MONGODB_TB_ORGANIZATIONS          = "organizations"
    CONFIG_MONGODB_TB_ORGANIZATIONS_USERS    = "organizations_users"
    CONFIG_MONGODB_TB_ORGANIZATIONS_GROUPS   = "organizations_groups"
    CONFIG_MONGODB_TB_ORGANIZATIONS_POLICIES = "organizations_policies"
    CONFIG_MONGODB_TB_DEFAULT_POLICIES       = "organizations_defaultpolicies"

    CONFIG_MONGODB_TB_SUBSCRIPTIONS          = "oldpayment_subscriptions"
    CONFIG_MONGODB_TB_PAYMENTTRANSACTIONS    = "oldpayment_transactions"
    CONFIG_MONGODB_TB_PAYMENTPAYERIDS        = "oldpayment_payerids"


    # Caching settings
    if debugging:
        # CONFIG_REDIS_HOST            = "127.0.0.1"
        # CONFIG_REDIS_HOST            = "192.168.99.100"
        CONFIG_REDIS_HOST            = "localhost"

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

    # Storage size settings
    CONFIG_GIGABYTE_GB               = 1000000000 # 1000*1000*1000
    CONFIG_GIGABYTE_GiB              = 1073741824 # 1024*1024*1024
    CONFIG_MEGABYTE_MB               = 1000000    # 1000*1000
    CONFIG_MEGABYTE_MiB              = 1048576    # 1024*1024
    CONFIG_KILOBYTE_KB               = 1000       # 1000
    CONFIG_KILOBYTE_KiB              = 1024       # 1024
    CONFIG_GIGABYTE_CONVERSION       = CONFIG_GIGABYTE_GB
    CONFIG_MEGABYTE_CONVERSION       = CONFIG_MEGABYTE_MB
    CONFIG_KILOBYTE_CONVERSION       = CONFIG_KILOBYTE_KB
