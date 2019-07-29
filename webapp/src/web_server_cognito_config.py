import os


class config:

    CONFIG_ACCESS_KEY       = os.environ["AWS_ACCESS_KEY_ID"]
    CONFIG_SECRET_KEY       = os.environ["AWS_SECRET_ACCESS_KEY"]

    CONFIG_CLIENT_ID        = os.environ["AWS_COGNITO_CLIENT_ID"]
    CONFIG_USER_POOL_ID     = os.environ["AWS_COGNITO_USERPOOL_ID"]
    CONFIG_USER_POOL_REGION = os.environ["AWS_COGNITO_USERPOOL_REGION"]

