import os


class config:

    # The value should correspond to notification_models in notification_client.py
    # notification_models
    # PINPOINT = 0
    # SNS      = 1
    # TWILIO   = 2
    # NEXMO    = 3
    CONFIG_USE_EMAIL_MODEL        = os.environ["CONFIG_USE_EMAIL_MODEL"]
    CONFIG_USE_SMS_MODEL          = os.environ["CONFIG_USE_SMS_MODEL"]

    CONFIG_DEBUG_NOTIFICATION     = False
