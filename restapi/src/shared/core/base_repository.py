
from typing import TypeVar, Generic
import asyncio


class BaseRepository():

    def create(self, input) -> str:
        pass

    def update(self, id: str, input) -> bool:
        pass

    def getById(self, id: str):
        pass

    def delete(self, id: str) -> bool:
        pass
