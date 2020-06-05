
from shared.utils.singleton_util import Singleton

class LoggerService(metaclass=Singleton):
    
    # TODO: Setup some tool support logging error here
    
    def error(self, message:str, tag=""):
        print(tag + " " + message)
        # Add more tracings error
        
    def debug(self, message: str, tag=""):
        print(tag + " " + message)
        # Just for debug mode
        
    def log(self, message: str, tag=""):
        print(tag + " " + message)
        # Show for all mode