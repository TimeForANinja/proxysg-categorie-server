from enum import Enum
from typing import List, Optional, Iterator, Dict, Any, Callable

from auth.auth_user import AuthUser

class StagedChangeAction(Enum):
    ADD = 1
    REMOVE = 2
    UPDATE = 3
    DELETE = 4

class StagedChangeTable(Enum):
    CATEGORY = 1
    TOKEN = 2
    URL = 3


class StagedChange:
    type: StagedChangeAction
    table: StagedChangeTable
    auth: AuthUser
    id: str
    data: Optional[Dict[str, Any]]

    def __init__(
            self,
            type: StagedChangeAction,
            table: StagedChangeTable,
            auth: AuthUser,
            id: str,
            data: Optional[Dict[str, Any]],
    ):
        self.type = type
        self.table = table
        self.auth = auth
        self.id = id
        self.data = data


items: List[StagedChange] = []
class StagedCollection:
    # for now a simple array, later a redis cache

    def add(self, change: StagedChange):
        items.append(change)
        self.simplify_stack()

    def iter(self) -> Iterator[StagedChange]:
        return iter(items)

    def iter_filter(self, *conditions: Callable[[StagedChange], bool]) -> Iterator[StagedChange]:
        iterator = self.iter()
        for c in conditions:
            iterator = filter(c, iterator)
        return iterator

    def first_or_none(self, *conditions: Callable[[StagedChange], bool]) -> Optional[StagedChange]:
        return next(self.iter_filter(*conditions), None)

    def remove(self, change: StagedChange):
        items.remove(change)

    def clear(self):
        items.clear()

    def simplify_stack(self):
        # TODO: implement
        pass

class StageFilter:
    @staticmethod
    def filter_add(change: StagedChange) -> bool:
        return change.type == StagedChangeAction.ADD

    @staticmethod
    def fac_filter_table(table: StagedChangeTable) -> Callable[[StagedChange], bool]:
        return lambda change: change.table == table

    @staticmethod
    def fac_filter_id(id: str) -> Callable[[StagedChange], bool]:
        return lambda change: change.id == id

    def fac_filter_table_id(self, table: StagedChangeTable, id: str) -> Callable[[StagedChange], bool]:
        return lambda change: change.table == table and change.id == id
