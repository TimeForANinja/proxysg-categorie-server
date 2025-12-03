from typing import List, Mapping, Any, Optional
from pymongo.synchronous.database import Database

from db.backend.abc.token_category import TokenCategoryDBInterface
from db.backend.abc.util.types import MyTransactionType
from db.backend.mongodb.base_category_db import MongoDBBaseCategory


class MongoDBTokenCategory(TokenCategoryDBInterface, MongoDBBaseCategory):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        super().__init__(db, 'tokens', 'Token')

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        return self.get_categories_by_item(token_id)

    def add_token_category(self, token_id: str, category_id: str, session: Optional[MyTransactionType] = None):
        self.add_item_category(token_id, category_id, session=session)

    def delete_token_category(self, token_id: str, category_id: str, del_timestamp: int, session: Optional[MyTransactionType] = None):
        self.delete_item_category(token_id, category_id, del_timestamp, session=session)
