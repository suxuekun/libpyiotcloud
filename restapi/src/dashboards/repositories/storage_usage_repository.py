from database import database_client
from dashboards.utils.percent_util import get_percent_by
from dashboards.models.gateway_attribute import *

class IStorageUsageRepositoy:

    def gets_by_gatewaysId(self, gatewaysUUID: []):
        pass

class StorageUsageRepository(IStorageUsageRepositoy):

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

            _bytes, _kb, _mb, _gb, alloc_storage = self.database_client.get_menos_num_sensordata_by_deviceid_by_currmonth(
                gatewayUUID)

            calculateUsage = get_percent_by(_gb, alloc_storage)
            newReport[USED_STORAGE_VALUE] = calculateUsage
            newReport[FREE_STORAGE_VALUE] = 100 - calculateUsage
            
            reports.append(newReport)

        return reports
