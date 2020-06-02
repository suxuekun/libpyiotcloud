
from typing import TypeVar, Generic
import asyncio
from restapi.src.shared.core.entity import Entity

TypeEntity = TypeVar('TypeEntity')

class BaseRepository(Generic[TypeEntity]):

    def create(self, input: Input) -> bool:
        pass

    def update(self, id: str, input: Input) -> bool:
        pass

    def getById(self, id: str) -> TypeEntity:
        pass

    def gets(self, query, projection) -> List[TypeEntity]:
        pass
    
    def delete(self, id: str) -> bool:
        pass
