
import json
from flask import jsonify

class Response:

    def __init__(self, data, message: str, status: str):
        self.data = data
        self.message = message
        self.status = status

    @staticmethod
    def fail(message: str):
        return Response(data = None, message=message, status="Fail").toJson(), 500

    @staticmethod
    def success(data, message: str):
        return Response(data = data, message=message, status="Ok").toJson(), 200
    
    @staticmethod
    def success_without_data(message: str):
        return Response(data = None, message = message, status="OK").toJson(), 200
        
    def toJson(self):
        response = {
            'message': self.message,
            'status': self.status
        }

        if self.data is not None:
            response['data'] = self.data

        return jsonify(response)
