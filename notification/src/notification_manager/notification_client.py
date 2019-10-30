import boto3
from aws_config import config as aws_config
from twilio_config import config as twilio_config
from nexmo_config import config as nexmo_config
from twilio.rest import Client as twilio_client
from nexmo import Client as nexmo_client



class notification_models:

    PINPOINT = 0
    SNS      = 1
    TWILIO   = 2
    NEXMO    = 3


class notification_types:

    UNKNOWN  = 0
    EMAIL    = 1
    SMS      = 2
    DEVICE   = 3


class notification_client:

    def __init__(self, model_email, model_sms):
        self.model_email = model_email
        self.model_sms = model_sms

        if self.model_email==notification_models.PINPOINT:
            self._base_email = notification_client_pinpoint()
        elif self.model_email==notification_models.SNS:
            self._base_email = notification_client_sns()

        if self.model_sms != self.model_email:
            if self.model_sms==notification_models.PINPOINT:
                self._base_sms = notification_client_pinpoint()
            elif self.model_sms==notification_models.SNS:
                self._base_sms = notification_client_sns()
            elif self.model_sms==notification_models.TWILIO:
                self._base_sms = notification_client_twilio()
            elif self.model_sms==notification_models.NEXMO:
                self._base_sms = notification_client_nexmo()
        else:
            self._base_sms = self._base_email

    def initialize(self):
        self._base_email.initialize()
        if self.model_sms != self.model_email:
            self._base_sms.initialize()

    def send_message(self, recipient, message, subject=None, type=notification_types.UNKNOWN):
        if type == notification_types.SMS:
            print('SMS')
            return self._base_sms.send_message(recipient, message, subject, type)
        elif type == notification_types.EMAIL:
            print('EMAIL')
            return self._base_email.send_message(recipient, message, subject, type)
        else:
            print('UNKNOWN')


##################################################################################################
# Amazon PINPOINT
##################################################################################################
class notification_client_pinpoint:

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
        print("PINPOINT")
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


##################################################################################################
# Amazon SNS
##################################################################################################
class notification_client_sns:

    def __init__(self):
        self.aws_access_key_id     = aws_config.CONFIG_ACCESS_KEY
        self.aws_secret_access_key = aws_config.CONFIG_SECRET_KEY
        self.region_name           = aws_config.CONFIG_SNS_REGION
        self.sns_topic_arn         = aws_config.CONFIG_SNS_TOPIC_ARN

    def initialize(self):
        self.client = boto3.Session(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            region_name = self.region_name).client('sns')

    def send_message(self, recipient, message, subject, type):
        print("SNS")
        if type == notification_types.SMS:
            response = self.send_email(message)
        elif type == notification_types.EMAIL:
            response = self.send_sms(recipient, message)
        return response

    def send_email(self, email_message):
        return self.client.publish(Message=email_message, TopicArn=self.sns_topic_arn)

    def send_sms(self, sms_recipient, sms_message):
        return self.client.publish(Message=sms_message, PhoneNumber=sms_recipient)


##################################################################################################
# Twilio
##################################################################################################
class notification_client_twilio:

    def __init__(self):
        self.account_sid = twilio_config.CONFIG_ACCOUNT_SID
        self.auth_token  = twilio_config.CONFIG_AUTH_TOKEN
        self.number_from = twilio_config.CONFIG_NUMBER_FROM

    def initialize(self):
        self.client = twilio_client(self.account_sid, self.auth_token)

    def send_message(self, recipient, message, subject, type):
        print("TWILIO")
        return self.send_sms(recipient, message)

    def send_sms(self, sms_recipient, sms_message):
        return self.client.messages.create(from_=self.number_from, to=sms_recipient, body=sms_message)


##################################################################################################
# Nexmo
##################################################################################################
class notification_client_nexmo:

    def __init__(self):
        self.key = nexmo_config.CONFIG_KEY
        self.secret = nexmo_config.CONFIG_SECRET
        self.number_from = 'Nexmo'

    def initialize(self):
        self.client = nexmo_client(key=self.key, secret=self.secret)

    def send_message(self, recipient, message, subject, type):
        print("NEXMO")
        return self.send_sms(recipient, message)

    def send_sms(self, sms_recipient, sms_message):
        if sms_recipient[0] == '+':
            sms_recipient = sms_recipient[1:]
        return self.client.send_message({'from':self.number_from, 'to':sms_recipient, 'text':sms_message})

