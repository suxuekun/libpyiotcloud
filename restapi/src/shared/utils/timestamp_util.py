
from datetime import datetime

def get_timestamp():
    return str(int(datetime.utcnow().timestamp()))


if __name__ == "__main__":
    timestamp = get_timestamp()
    time = datetime.fromtimestamp(timestamp)

    utc = datetime.utcfromtimestamp(timestamp)

    print (time,utc,timestamp)