
from typing import TypeVar, Generic
import asyncio


class BaseRepository():

    def create(self, input) -> bool:
        pass

    def update(self, id: str, input) -> bool:
        pass

    def getById(self, id: str):
        pass

    def gets(self, query, projection) -> []:
        pass
    
    def delete(self, id: str) -> bool:
        pass
