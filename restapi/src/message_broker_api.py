import json
import base64
from rest_api_config import config
from flask_api import status
import http.client



class message_broker_api:

    def __init__(self):
        pass

    def mq_adduser(self, auth64, deviceuser, devicepass):
        conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
        header = { "Authorization": auth64, "Content-Type": "application/json" }

        api = "/api/users/{}".format(deviceuser)
        params = { "password": devicepass, "tags": "" }

        conn.request("PUT", api, json.dumps(params), header)
        response = conn.getresponse()
        if response.status != 201:
            print(response.status)
            return False
        #else:
        #    print(response)

        return True

    def mq_removeuser(self, auth64, deviceuser):
        conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
        header = { "Authorization": auth64 }

        api = "/api/users/{}".format(deviceuser)

        conn.request("DELETE", api, None, header)
        response = conn.getresponse()
        if (response.status != 204):
            print(response.status)
            return False

        return True

    def mq_setpermission(self, auth64, deviceuser):
        conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
        header = { "Authorization": auth64, "Content-Type": "application/json" }

        api = "/api/permissions/%2F/{}".format(deviceuser)
        params = { "configure": ".*", "write": ".*", "read": ".*" }

        conn.request("PUT", api, json.dumps(params), header)
        response = conn.getresponse()
        if (response.status != 201):
            print(response.status)
            return False

        return True

    def mq_settopicpermission(self, auth64, deviceuser):
        conn = http.client.HTTPConnection(config.CONFIG_HOST, config.CONFIG_MGMT_PORT)
        header = { "Authorization": auth64, "Content-Type": "application/json" }

        api = "/api/topic%2Dpermissions/%2F/{}".format(deviceuser)
        pubtopic = "^server.{}.*".format(deviceuser)
        subtopic = "{}.#".format(deviceuser)
        params = {"exchange": "amq.topic", "write": pubtopic, "read": subtopic }

        conn.request("PUT", api, json.dumps(params), header)
        response = conn.getresponse()
        if (response.status != 201):
            print(response.status)
            return False

        return True


    ######

    def register(self, deviceuser, devicepass, secure=True):
        if config.CONFIG_ENABLE_MQ_SECURITY:
            account = config.CONFIG_MGMT_ACCOUNT
            auth64 = "Basic {}".format(str(base64.urlsafe_b64encode(account.encode("utf-8")), "utf-8"))
            result = self.mq_adduser(auth64, deviceuser, devicepass)
            if not result:
                print("mq_adduser fails")
                return result
            result = self.mq_setpermission(auth64, deviceuser)
            if not result:
                print("mq_setpermission fails")
                return result
            # set topic permission only if secure option is enabled
            if secure:
                result = self.mq_settopicpermission(auth64, deviceuser)
                if not result:
                    print("mq_settopicpermission fails")
                    return result
        return True

    def unregister(self, deviceuser):
        if config.CONFIG_ENABLE_MQ_SECURITY:
            account = config.CONFIG_MGMT_ACCOUNT
            auth64 = "Basic {}".format(str(base64.urlsafe_b64encode(account.encode("utf-8")), "utf-8"))
            return self.mq_removeuser(auth64, deviceuser)
        return True
