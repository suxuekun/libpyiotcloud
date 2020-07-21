import os


class config:

    CONFIG_ACCESS_KEY                           = os.environ["AWS_ACCESS_KEY_ID"]
    CONFIG_SECRET_KEY                           = os.environ["AWS_SECRET_ACCESS_KEY"]

    CONFIG_PINPOINT_ID                          = os.environ["AWS_PINPOINT_ID"]
    CONFIG_PINPOINT_REGION                      = os.environ["AWS_PINPOINT_REGION"]
    CONFIG_PINPOINT_EMAIL                       = os.environ["AWS_PINPOINT_EMAIL"]
    CONFIG_USE_APIURL                           = os.environ["CONFIG_USE_APIURL"]

    CONFIG_PINPOINT_EMAIL_SUBJECT_RECEIPT              = "Bridgetek IoT Portal receipt"
    CONFIG_PINPOINT_EMAIL_SUBJECT_ORGANIZATION         = "Bridgetek IoT Portal organization"
    CONFIG_PINPOINT_EMAIL_SUBJECT_USAGENOTICE          = "Bridgetek IoT Portal usage notice"
    CONFIG_PINPOINT_EMAIL_SUBJECT_SENSORDATADL         = "Bridgetek IoT Portal sensor data download"
    CONFIG_PINPOINT_EMAIL_SUBJECT_DEVICEREGISTRATION   = "Bridgetek IoT Portal device registration"
    CONFIG_PINPOINT_EMAIL_SUBJECT_DEVICEUNREGISTRATION = "Bridgetek IoT Portal device unregistration"
    CONFIG_PINPOINT_EMAIL_SUBJECT_ACCOUNTCREATION      = "Bridgetek IoT Portal account creation"
    CONFIG_PINPOINT_EMAIL_SUBJECT_ACCOUNTDELETION      = "Bridgetek IoT Portal account deletion"

