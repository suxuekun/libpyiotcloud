class S3Exception(Exception):
    pass

class CreatedExeception(Exception):
    """ Create failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class DeletedException(Exception):
    """ Delete failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdatedException(Exception):
    """ Update failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class QueriedByIdException(Exception):
    """ Get detail failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class QueriedManyException(Exception):
    """ Gets failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)