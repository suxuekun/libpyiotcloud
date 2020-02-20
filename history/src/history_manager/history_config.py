import os


class config:

    # General settings
    CONFIG_DEBUG_HISTORY          = False
    CONFIG_ENABLE_MAX_HISTORY     = True
    CONFIG_MAX_HISTORY_PER_DEVICE = 50

    # Database settings
    CONFIG_MONGODB_HOST           = "mongodb"
    CONFIG_MONGODB_PORT           = 27017
    CONFIG_MONGODB_DB             = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES    = "profiles"
    CONFIG_MONGODB_TB_DEVICES     = "devices"
    CONFIG_MONGODB_TB_HISTORY     = "history"
    CONFIG_MONGODB_TB_NOTIFICATIONS  = "notifications"
    CONFIG_MONGODB_TB_SENSORREADINGS = "sensorreadings"

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER      = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS      = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]
