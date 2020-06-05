


class CreatedExeception(Exception):
    """ Create failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)