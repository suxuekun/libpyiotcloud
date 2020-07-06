import os


class config:

    # General settings
    CONFIG_DEBUG                     = False

    # Database settings
    CONFIG_MONGODB_USERNAME          = os.environ["CONFIG_USE_MONGODB_USER"]
    CONFIG_MONGODB_PASSWORD          = os.environ["CONFIG_USE_MONGODB_PASS"]
    CONFIG_MONGODB_HOST              = "mongodb"
    CONFIG_MONGODB_PORT              = 27017
    CONFIG_MONGODB_DB                = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES       = "profiles"

    CONFIG_MONGODB_TB_DEVICES        = "devices"
    CONFIG_MONGODB_TB_HISTORY        = "devices_history"

    CONFIG_MONGODB_TB_CONFIGURATIONS = "sensors_configurations"
    CONFIG_MONGODB_TB_NOTIFICATIONS  = "sensors_notifications"
    CONFIG_MONGODB_TB_SENSORREADINGS = "sensors_readings_latest"

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER         = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS         = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]

