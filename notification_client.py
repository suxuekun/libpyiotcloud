import boto3
from notification_config import config



class notification_models:

    PINPOINT = 0
    SNS      = 1


class notification_client:

    def __init__(self, model=notification_models.PINPOINT):
        if model==notification_models.PINPOINT:
            self._base = notification_client_pinpoint()
        elif model==notification_models.SNS:
            self._base = notification_client_sns()

    def initialize(self):
        self._base.initialize()

    def send_message(self, recipient, message, subject=None):
        return self._base.send_message(recipient, message, subject)


class notification_client_pinpoint:

    def __init__(self, model=notification_models.PINPOINT):
        self.aws_access_key_id     = config.ACCESS_KEY
        self.aws_secret_access_key = config.SECRET_KEY
        self.pinpoint_project_id   = config.PINPOINT_ID
        self.region_name           = config.PINPOINT_REGION
        self.email_from            = config.PINPOINT_EMAIL

    def initialize(self):
        self.client = boto3.Session(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            region_name = self.region_name).client('pinpoint')

    def send_message(self, recipient, message, subject=None):
        if subject is None:
            response = self.send_sms(recipient, message)
        else:
            response = self.send_email(recipient, message, subject)
        return response

    def send_email(self, email_recipient, email_message, email_subject):
        response = self.client.send_messages(
            ApplicationId = self.pinpoint_project_id,
            MessageRequest = {
                'Addresses': {email_recipient: { 'ChannelType': 'EMAIL'}},
                'MessageConfiguration': {
                    'EmailMessage': {
                        'FromAddress': self.email_from,
                        'SimpleEmail':  {
                            'Subject':  {'Charset': 'UTF-8', 'Data': email_subject},
                            'TextPart': {'Charset': 'UTF-8', 'Data': email_message}
                        }
                    }
                }
            }
        )
        return response

    def send_sms(self, sms_recipient, sms_message):
        response = self.client.send_messages(
            ApplicationId = self.pinpoint_project_id,
            MessageRequest = {
                'Addresses': {sms_recipient: {'ChannelType': 'SMS'}},
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': sms_message
                    }
                }
            }
        )
        return response





