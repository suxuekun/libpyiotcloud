import os


class config:

    # AWS S3 and P inpoint settings
    CONFIG_ACCESS_KEY                           = os.environ["AWS_ACCESS_KEY_ID"]
    CONFIG_SECRET_KEY                           = os.environ["AWS_SECRET_ACCESS_KEY"]
    CONFIG_REGION                               = os.environ["AWS_S3_REGION"]
    CONFIG_BUCKET                               = os.environ["AWS_S3_BUCKET"]
    CONFIG_PINPOINT_ID                          = os.environ["AWS_PINPOINT_ID"]
    CONFIG_PINPOINT_REGION                      = os.environ["AWS_PINPOINT_REGION"]
    CONFIG_PINPOINT_EMAIL                       = os.environ["AWS_PINPOINT_EMAIL"]
    CONFIG_PINPOINT_EMAIL_SUBJECT_SENSORDATA    = "Bridgetek IoT Modem device sensor data"

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

