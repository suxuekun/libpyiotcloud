
from typing import TypeVar, Generic

Input = TypeVar('Input')
Output = TypeVar('Output')

class UseCase(Generic[Input], Generic[Output]):

    def build_usecase(self, input: Input):
        pass
    
    def execute(self, input: Input):
        try:
           return build_usecase(self, input)
        except Exception as inst:
            print(inst)
            raise Exception("Sorry, there is something wrong")

    
