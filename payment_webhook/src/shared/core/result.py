
from typing import TypeVar, Generic
Model = TypeVar('Model')
U = TypeVar('U')

class Result(Generic[Model]):
    def __init__(self,  is_success: bool, error: Model | str, value: Model):
        self.is_success = is_success
        self.is_failure = not is_success
        self.error = error
        self.value = value

    def get_value(self) -> Model:
        if not self.is_success :
            print(self.error)
            raise Exception("Can't get the value of an error result")

        return self.value
    
    @staticmethod
    def ok(value: U) -> Result[U]:
        return Result[U](True, None, value)  

    @staticmethod
    def fail(error: str) -> Result[str]:
        return Result[str](False, error, None)

