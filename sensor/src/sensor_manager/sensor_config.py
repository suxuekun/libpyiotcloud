import os


class config:

    # General settings
    CONFIG_DEBUG_SENSOR_READING   = False

    CONFIG_ENABLE_DATASET         = True
    CONFIG_MAX_DATASET            = 17280 # 24 hours = 86400 seconds; 86400/5=17280

    # Database settings
    CONFIG_MONGODB_USERNAME                  = os.environ["CONFIG_USE_MONGODB_USER"]
    CONFIG_MONGODB_PASSWORD                  = os.environ["CONFIG_USE_MONGODB_PASS"]
    CONFIG_MONGODB_HOST                      = "mongodb"
    #CONFIG_MONGODB_HOST2                     = "mongodb"
    CONFIG_MONGODB_HOST2                     = os.environ["CONFIG_USE_MONGODB_ATLAS"]
    CONFIG_MONGODB_PORT                      = 27017
    CONFIG_MONGODB_DB                        = "iotcloud-database"
    CONFIG_MONGODB_SENSOR_DB                 = "iotcloud-sensordata-database"
    CONFIG_MONGODB_HEARTBEAT_DB              = "iotcloud-heartbeat-database"
    CONFIG_MONGODB_MENOSALERT_DB             = "iotcloud-menosalert-database"
    CONFIG_MONGODB_PACKETHISTORY_DB          = "iotcloud-packethistory-database"
    CONFIG_MONGODB_TB_PROFILES               = "profiles"

    CONFIG_MONGODB_TB_DEVICES                = "devices"
    CONFIG_MONGODB_TB_HISTORY                = "devices_history"
    CONFIG_MONGODB_TB_DEVICEGROUPS           = "devices_groups"

    CONFIG_MONGODB_TB_I2CSENSORS             = "sensors"
    CONFIG_MONGODB_TB_CONFIGURATIONS         = "sensors_configurations"
    CONFIG_MONGODB_TB_NOTIFICATIONS          = "sensors_notifications"
    CONFIG_MONGODB_TB_SENSORREADINGS         = "sensors_readings_latest"
    CONFIG_MONGODB_TB_SENSORREADINGS_DATASET = "sensors_readings_dataset"

    CONFIG_MONGODB_TB_PAYMENTSUBSCRIPTION    = "payment_subscription"

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER                 = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS                 = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]

    # Storage size settings
    CONFIG_GIGABYTE_GB               = 1000000000 # 1000*1000*1000
    CONFIG_GIGABYTE_GiB              = 1073741824 # 1024*1024*1024
    CONFIG_MEGABYTE_MB               = 1000000    # 1000*1000
    CONFIG_MEGABYTE_MiB              = 1048576    # 1024*1024
    CONFIG_KILOBYTE_KB               = 1000       # 1000
    CONFIG_KILOBYTE_KiB              = 1024       # 1024
    CONFIG_GIGABYTE_CONVERSION       = CONFIG_GIGABYTE_GB # MongoDB Compass uses GB not GiB
    CONFIG_MEGABYTE_CONVERSION       = CONFIG_MEGABYTE_MB # MongoDB Compass uses MB not MiB
    CONFIG_KILOBYTE_CONVERSION       = CONFIG_KILOBYTE_KB # MongoDB Compass uses KB not KiB

