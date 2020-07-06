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

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER                 = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS                 = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]

