
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from dashboards.utils.percent_util import get_percent_by
from database import database_client
from dashboards.models.gateway_attribute import *
import time

class IHeartBeatRepository:

    def gets_by_gatewaysId(self, gatewaysUUID: [], timestamp: int):
        pass

class HeartBeatRepository(IHeartBeatRepository):

    def __init__(self, database_client: database_client):
        self.database_client = database_client

    def gets_by_gatewaysId(self, gatewaysUUID:[], timestamp: int):
        
        if len(gatewaysUUID) is 0:
            return []

        reports = []
        for gatewayUUID in gatewaysUUID:
            newReport = {
                "gatewayUUID": gatewayUUID
            }

            hbeat_day, hbeatmax_day = self.database_client.get_num_device_heartbeats_by_timestamp_by_day(gatewayUUID, timestamp)
            hbeat_week, hbeatmax_week = self.database_client.get_num_device_heartbeats_by_timestamp_by_week(gatewayUUID, timestamp)
            hbeat_month, hbeatmax_month = self.database_client.get_num_device_heartbeats_by_timestamp_by_month(gatewayUUID, timestamp)
            
            calculateOnlineByDay = get_percent_by(hbeat_day, hbeatmax_day)
            calculateOnlineByWeek = get_percent_by(hbeat_week, hbeatmax_week)
            calculateOnlineByMonth = get_percent_by(hbeat_month, hbeatmax_month)

            newReport[ONE_DAY_VALUE] = {
                ONLINE_VALUE: calculateOnlineByDay,
                OFFLINE_VALUE: 100 - calculateOnlineByDay
            }

            newReport[ONE_WEEK_VALUE] = {
                ONLINE_VALUE: calculateOnlineByWeek,
                OFFLINE_VALUE: 100 - calculateOnlineByWeek
            }

            newReport[ONE_MONTH_VALUE] = {
                ONLINE_VALUE: calculateOnlineByMonth,
                OFFLINE_VALUE: 100 - calculateOnlineByMonth
            }

            reports.append(newReport)

        return reports