import os


class config:

    # General settings
    CONFIG_DEBUG_SENSOR_READING   = False

    CONFIG_ENABLE_DATASET         = True
    CONFIG_MAX_DATASET            = 20

    # Database settings
    CONFIG_MONGODB_HOST              = "mongodb"
    CONFIG_MONGODB_PORT              = 27017
    CONFIG_MONGODB_DB                = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES       = "profiles"
    CONFIG_MONGODB_TB_DEVICES        = "devices"
    CONFIG_MONGODB_TB_HISTORY        = "history"
    CONFIG_MONGODB_TB_NOTIFICATIONS  = "notifications"
    CONFIG_MONGODB_TB_I2CSENSORS     = "i2csensors"
    CONFIG_MONGODB_TB_CONFIGURATIONS = "configurations"
    CONFIG_MONGODB_TB_SENSORREADINGS = "sensorreadings"
    CONFIG_MONGODB_TB_SENSORREADINGS_DATASET = "sensorreadingsdataset"

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER         = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS         = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]

