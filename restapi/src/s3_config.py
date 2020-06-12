import os


class config:

    CONFIG_ACCESS_KEY            = os.environ["AWS_ACCESS_KEY_ID"]
    CONFIG_SECRET_KEY            = os.environ["AWS_SECRET_ACCESS_KEY"]

    CONFIG_REGION                = os.environ["AWS_S3_REGION"]
    CONFIG_BUCKET                = os.environ["AWS_S3_BUCKET"]
    CONFIG_FILE_I2C_DEVICES      = os.environ["AWS_S3_FILE_I2C_DEVICES"]
    CONFIG_FILE_SENSOR_DEVICES   = os.environ["AWS_S3_FILE_SENSOR_DEVICES"]
    CONFIG_FILE_FIRMWARE_UPDATES = os.environ["AWS_S3_FILE_FIRMWARE_UPDATES"]
    # CONFIG_FILE_SUBSCRIPTION_PLAN = os.environ["AWS_S3_FILE_SUBSCRIPTION_PLAN"]
