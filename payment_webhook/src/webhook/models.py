from schematics.types import StringType
from shared.core.model import BaseModel, MongoIdMixin

class WebhookStatus():
    PENDING = 'pending'
    PROCESSING = 'processing'
    PROCESSED = 'processed'

class AbstractWebhook(BaseModel,MongoIdMixin):
    kind = StringType()
    timestamp = StringType()
    bt_signature = StringType()
    bt_payload = StringType()

class Webhook(AbstractWebhook):
    status = StringType(default = WebhookStatus.PENDING)
    pass