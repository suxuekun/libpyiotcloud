import os

CONFIG_MODE = os.environ.get('BRAINTREE_MODE')
CONFIG_MERCHANT_ID = os.environ.get('BRAINTREE_MERCHANT_ID')
CONFIG_PUBLIC_KEY = os.environ.get('BRAINTREE_PUBLIC_KEY')
CONFIG_PRIVATE_KEY = os.environ.get('BRAINTREE_PRIVATE_KEY')
debugging = int(os.environ['CONFIG_USE_DEBUG_MODE'])
if debugging:
    CONFIG_HTTP_USE_TLS     = True
else:
    CONFIG_HTTP_USE_TLS     = False # Set to False when using GUnicorn (only in Linux)
CONFIG_HTTP_HOST            = "localhost"
CONFIG_HTTP_PORT            = 8003
CONFIG_HTTP_TLS_PORT        = 443

CONFIG_MONGODB_USERNAME          = os.environ["CONFIG_USE_MONGODB_USER"]
CONFIG_MONGODB_PASSWORD          = os.environ["CONFIG_USE_MONGODB_PASS"]
if debugging:
    CONFIG_MONGODB_HOST          = "127.0.0.1"
    # MongoDB Atlas is used for sensor-data database
    # to revert to containerized MongoDB, just set this to 127.0.0.1
    CONFIG_MONGODB_HOST2         = os.environ["CONFIG_USE_MONGODB_ATLAS"]
else:
    CONFIG_MONGODB_HOST          = "mongodb"
    # MongoDB Atlas is used for sensor-data database
    # to revert to containerized MongoDB, just set this to mongodb
    CONFIG_MONGODB_HOST2         = os.environ["CONFIG_USE_MONGODB_ATLAS"]
CONFIG_MONGODB_PORT              = 27017

# Database records
CONFIG_MONGODB_DB                        = "iotcloud-database"