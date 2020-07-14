import boto3
from aws_config import config as aws_config



class email_models:

    PINPOINT = 0


class email_types:

    UNKNOWN           = 0
    EMAIL             = 1


class email_client:

    def __init__(self, model_email=email_models.PINPOINT):
        self._base_email = email_client_pinpoint()

    def initialize(self):
        self._base_email.initialize()

    def send_message(self, recipient, message, subject=None, type=email_types.EMAIL):
        return self._base_email.send_message(recipient, message, subject, type)


##################################################################################################
# Amazon PINPOINT
##################################################################################################
class email_client_pinpoint:

    def __init__(self):
        self.aws_access_key_id     = aws_config.CONFIG_ACCESS_KEY
        self.aws_secret_access_key = aws_config.CONFIG_SECRET_KEY
        self.region_name           = aws_config.CONFIG_PINPOINT_REGION
        self.pinpoint_project_id   = aws_config.CONFIG_PINPOINT_ID
        self.email_from            = aws_config.CONFIG_PINPOINT_EMAIL

    def initialize(self):
        self.client = boto3.Session(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            region_name = self.region_name).client('pinpoint')
        self.messaging_client = None

    def send_message(self, recipient, message, subject, type):
        return self.send_email(recipient, message, subject)

    def send_email(self, recipient, message, subject):
        #print("EMAIL {} {} {}".format(recipient, message, subject))
        response = self.client.send_messages(
            ApplicationId = self.pinpoint_project_id,
            MessageRequest = {
                'Addresses': {recipient: { 'ChannelType': 'EMAIL'}},
                'MessageConfiguration': {
                    'EmailMessage': {
                        'FromAddress': self.email_from,
                        'SimpleEmail':  {
                            'Subject':  {'Charset': 'UTF-8', 'Data': subject},
                            'TextPart': {'Charset': 'UTF-8', 'Data': message}
                        }
                    }
                }
            }
        )
        return response
