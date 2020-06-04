

class UpdatedException(Exception):
    """ Update failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)