from web_server import app
from web_server_config import config

if __name__ == "__main__":
    app.run(host=config.CONFIG_HTTP_HOST, port=config.CONFIG_HTTP_PORT, debug=True)
