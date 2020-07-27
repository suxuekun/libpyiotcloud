from schematics.types import StringType, IntType

from shared.core.model import BaseModel, MongoIdMixin


class WebhookStatus():
    PENDING = 'pending'
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    FAIL = 'fail'
    IGNORE = 'ignore'

class AbstractWebhook(BaseModel,MongoIdMixin):
    kind = StringType()
    timestamp = IntType()
    bt_signature = StringType()
    bt_payload = StringType()

class Webhook(AbstractWebhook):
    status = StringType(default = WebhookStatus.PENDING)
    pass