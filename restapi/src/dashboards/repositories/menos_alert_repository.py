from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from database import database_client
from dashboards.utils.percent_util import get_percent_by
from dashboards.models.gateway_attribute import *

class IMenosAlertRepository:

    def gets_by_gatewaysId(self, gatewaysUUID: []):
        pass

class MenosAlertRepository(IMenosAlertRepository):

    def __init__(self, database_client: database_client):
        self.database_client = database_client

    def gets_by_gatewaysId(self, gatewaysUUID: []):

        if len(gatewaysUUID) is 0:
            return []

        reports = []
        for gatewayUUID in gatewaysUUID:
            newReport = {
                "gatewayUUID": gatewayUUID
            }

            usage_sms, alloc_sms = self.database_client.get_menos_num_sms_by_deviceid_by_currmonth(
                gatewayUUID)
            usage_email, alloc_email = self.database_client.get_menos_num_email_by_deviceid_by_currmonth(
                gatewayUUID)
            usage_notification, alloc_notification = self.database_client.get_menos_num_notification_by_deviceid_by_currmonth(
                gatewayUUID)

           
            calculateSMSSent = get_percent_by(usage_sms, alloc_sms)
            calculateEmailSent = get_percent_by(usage_email, alloc_email)
            calculateNotificationSent = get_percent_by(
                usage_notification, alloc_notification)

            newReport[SMS_VALUE] = {
                SENT_VALUE: calculateSMSSent,
                REMAINING_VALUE: 100 - calculateSMSSent
            }
            newReport[EMAILS_VALUE] = {
                SENT_VALUE: calculateEmailSent,
                REMAINING_VALUE: 100 - calculateEmailSent
            }
            newReport[NOTIFICATIONS_VALUE] = {
                SENT_VALUE: calculateNotificationSent,
                REMAINING_VALUE: 100 - calculateNotificationSent
            }

            reports.append(newReport)

        return reports
