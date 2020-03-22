import os


class config:

    # The value should correspond to notification_models in notification_client.py
    # notification_models
    # PINPOINT = 0
    # SNS      = 1
    # TWILIO   = 2
    # NEXMO    = 3
    CONFIG_USE_EMAIL_MODEL             = os.environ["CONFIG_USE_EMAIL_MODEL"]

    CONFIG_DEBUG_INVOICE               = False

    # RabbitMQ settings
    CONFIG_MQTT_DEFAULT_USER           = os.environ["CONFIG_USE_MQTT_DEFAULT_USER"]
    CONFIG_MQTT_DEFAULT_PASS           = os.environ["CONFIG_USE_MQTT_DEFAULT_PASS"]

    # Database settings
    CONFIG_MONGODB_USERNAME            = os.environ["CONFIG_USE_MONGODB_USER"]
    CONFIG_MONGODB_PASSWORD            = os.environ["CONFIG_USE_MONGODB_PASS"]
    CONFIG_MONGODB_HOST                = "mongodb"
    CONFIG_MONGODB_PORT                = 27017
    CONFIG_MONGODB_DB                  = "iotcloud-database"
    CONFIG_MONGODB_TB_PROFILES         = "profiles"
    CONFIG_MONGODB_TB_DEVICES          = "devices"
    CONFIG_MONGODB_TB_HISTORY          = "history"
    CONFIG_MONGODB_TB_NOTIFICATIONS    = "notifications"
    CONFIG_MONGODB_TB_DEVICETOKENS     = "devicetokens"
    CONFIG_MONGODB_TB_I2CSENSORS       = "i2csensors"
    CONFIG_MONGODB_TB_MENOS            = "menos"
    CONFIG_MONGODB_TB_PAYMENTTRANSACTIONS = "paymenttransactions"
    CONFIG_MONGODB_TB_PAYMENTPAYERIDS     = "paymentpayerids"