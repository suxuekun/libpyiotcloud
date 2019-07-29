import os


class config:

    CONFIG_ACCESS_KEY             = os.environ["AWS_ACCESS_KEY_ID"]
    CONFIG_SECRET_KEY             = os.environ["AWS_SECRET_ACCESS_KEY"]

    CONFIG_PINPOINT_ID            = os.environ["AWS_PINPOINT_ID"]
    CONFIG_PINPOINT_REGION        = os.environ["AWS_PINPOINT_REGION"]
    CONFIG_PINPOINT_EMAIL         = "richmond.umagat@gmail.com"
    CONFIG_PINPOINT_EMAIL_SUBJECT = "FT900 IoT Cloud Platform Notifications"

    CONFIG_SNS_TOPIC_ARN          = ""
    CONFIG_SNS_REGION             = ""
