from app import app
import config

if __name__ == "__main__":
    app.run(host=config.CONFIG_HTTP_HOST, port=config.CONFIG_HTTP_PORT, threaded=True, debug=(config.debugging==1))
