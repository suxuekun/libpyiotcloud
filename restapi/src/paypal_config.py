import os


class config:

    CONFIG_MODE                   = os.environ["PAYPAL_MODE"] # sandbox or live
    CONFIG_CLIENT_ID              = os.environ["PAYPAL_CLIENT_ID"]
    CONFIG_CLIENT_SECRET          = os.environ["PAYPAL_CLIENT_SECRET"]
