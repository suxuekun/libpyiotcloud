import os

from rest_api import app
from rest_api_config import config

if __name__ == "__main__":
    debug = os.environ['DEBUG_MODE']
    print('debug',debug)
    app.run(host=config.CONFIG_HTTP_HOST, port=config.CONFIG_HTTP_PORT, threaded=True, debug=debug)
