import boto3
from notification_config import config



class notification_models:

    PINPOINT = 0
    SNS      = 1

class notification_types:

    UNKNOWN  = 0
    EMAIL    = 1
    SMS      = 2
    DEVICE   = 3


class notification_client:

    def __init__(self, model=notification_models.PINPOINT):
        if model==notification_models.PINPOINT:
            self._base = notification_client_pinpoint()
        elif model==notification_models.SNS:
            self._base = notification_client_sns()

    def initialize(self):
        self._base.initialize()

    def send_message(self, recipient, message, subject=None, type=notification_types.UNKNOWN):
        return self._base.send_message(recipient, message, subject, type)


class notification_client_pinpoint:

    def __init__(self):
        self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
        self.aws_secret_access_key = config.CONFIG_SECRET_KEY
        self.region_name           = config.CONFIG_PINPOINT_REGION
        self.pinpoint_project_id   = config.CONFIG_PINPOINT_ID
        self.email_from            = config.CONFIG_PINPOINT_EMAIL

    def initialize(self):
        self.client = boto3.Session(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            region_name = self.region_name).client('pinpoint')
        self.messaging_client = None

    def send_message(self, recipient, message, subject, type):
        if type == notification_types.SMS:
            response = self.send_sms(recipient, message)
        elif type == notification_types.EMAIL:
            response = self.send_email(recipient, message, subject)
        else:
            return None
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


class notification_client_sns:

    def __init__(self):
        self.aws_access_key_id     = config.CONFIG_ACCESS_KEY
        self.aws_secret_access_key = config.CONFIG_SECRET_KEY
        self.region_name           = config.CONFIG_SNS_REGION
        self.sns_topic_arn         = config.CONFIG_SNS_TOPIC_ARN

    def initialize(self):
        self.client = boto3.Session(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            region_name = self.region_name).client('sns')

    def send_message(self, recipient, message, subject=None):
        if subject is None:
            response = self.client.publish(Message=message, PhoneNumber=recipient)
        else:
            response = self.client.publish(Message=message, TopicArn=self.sns_topic_arn)
        return response


