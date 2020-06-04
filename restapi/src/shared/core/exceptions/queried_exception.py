



class QueriedByIdException(Exception):
    """ Get detail failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class QueriedManyException(Exception):
    """ Gets failed """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)