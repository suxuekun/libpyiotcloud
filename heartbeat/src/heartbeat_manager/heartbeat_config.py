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
    CONFIG_MONGODB_SENSOR_DB         = "iotcloud-sensordata-database"
    CONFIG_MONGODB_HEARTBEAT_DB      = "iotcloud-heartbeat-database"
    CONFIG_MONGODB_TB_PROFILES       = "profiles"

    CONFIG_MONGODB_TB_DEVICES        = "devices"
    CONFIG_MONGODB_TB_HISTORY        = "devices_history"
    CONFIG_MONGODB_TB_HEARTBEAT      = "devices_heartbeat"

    CONFIG_MONGODB_TB_CONFIGURATIONS = "sensors_configurations"
    CONFIG_MONGODB_TB_NOTIFICATIONS  = "sensors_notifications"
    CONFIG_MONGODB_TB_SENSORREADINGS = "sensors_readings_latest"

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER         = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS         = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]

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
