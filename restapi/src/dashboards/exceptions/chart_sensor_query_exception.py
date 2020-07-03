


class ChartSensorQueryException(Exception):
    """ ChartSensorQueryException failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)