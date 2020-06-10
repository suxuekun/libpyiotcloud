from flask import Response

from shared.middlewares.response import http2xx,http3xx,http4xx
from shared.utils.json_util import to_json

DEFAULT_MIMETYPE = "application/json"

responses = {}
responses.update(http2xx.responses)
responses.update(http3xx.responses)
responses.update(http4xx.responses)

def register_error_responses(resposes):
    global responses
    responses.update(resposes)

def make_custom_error_response(response, status):
    res = {
        'response':response,
        'status':status
    }
    response = make_response(res)
    return response

def make_error_response(code):
    res = responses.get(code)
    response = make_response(res)
    return response

def make_response(res):
    global DEFAULT_MIMETYPE
    if isinstance(res.get('response'),dict):
        res['response'] = to_json(res.get('response'))
    if not res.get('mimetype'):
        res['mimetype'] = DEFAULT_MIMETYPE
    response = Response(**res)
    return response

if __name__ == "__main__":
    register_error_responses({
        'custom':({'status':'NG','message':'wtf custom message'},404),
    })
    print(responses)
    make_error_response(http4xx.INVALID_AUTHORIZATION_HEADER)
