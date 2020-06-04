


class LoggerService:
    
    __instance = None
    
    @staticmethod
    def get_instance():
        if LoggerService.__instance == None:
            LoggerService()
        return LoggerService.__instance


    def __init__(self):
        if LoggerService.__instance == None:
            LoggerService.__instance = self

    
    def error(self, message:str):
        print(message)
        # Add more tracings error
        
    def debug(self, message: str):
        print(message)
        # Just for debug mode
        
    def log(self, message: str):
        print(message)
        # Show for all mode