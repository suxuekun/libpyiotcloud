import os


class config:

    CONFIG_ACCOUNT_SID            = os.environ["TWILIO_ACCOUNT_SID"]
    CONFIG_AUTH_TOKEN             = os.environ["TWILIO_AUTH_TOKEN"]
    CONFIG_NUMBER_FROM            = os.environ["TWILIO_NUMBER_FROM"]
