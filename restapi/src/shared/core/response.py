
import json

class Response:

    def __init__(self, data, message: str, status: str):
        self.data = data
        self.message = message
        self.status = status

    @staticmethod
    def fail(message: str):
        return Response(data = None, message=message, status="Fail").toJson()

    @staticmethod
    def success(data, message: str):
        return Response(data = data, message=message, status="Ok").toJson()
    
    def toJson(self):
        response = {
            'message': self.message,
            'status': self.status
        }

        if data != None:
            response['data'] = data

        return json.dumps(response)
