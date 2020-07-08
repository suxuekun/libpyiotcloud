from flask import Flask

from webhook.app import WebHookApp

app = Flask(__name__)
webhook_app = WebHookApp(app)
