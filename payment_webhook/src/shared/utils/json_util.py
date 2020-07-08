import datetime
import decimal
import json


def datetime_json_encoder(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    return None


def date_json_encoder(x):
    if isinstance(x, datetime.date):
        return x.isoformat()
    return None


def time_json_encoder(x):
    if isinstance(x, datetime.time):
        return x.isoformat()
    return None


def decimal_json_encoder(x):
    if isinstance(x, decimal.Decimal):
        value = str(x)
        return value
    return None


def combined_json_encoder(x):
    encoders = [datetime_json_encoder, date_json_encoder, time_json_encoder, decimal_json_encoder]
    encoders_length = len(encoders)
    i = 0;
    while i < encoders_length:

        current_encoder = encoders[i]
        i += 1
        res = current_encoder(x)
        if res != None:
            return res
    return 'unknown value type'


def to_json(res):
    return json.dumps(res, default=combined_json_encoder)