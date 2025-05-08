from typing import List, Mapping, Any
from pymongo.synchronous.database import Database

from db.abc.token_category import TokenCategoryDBInterface
from db.mongodb.base_category_db import MongoDBBaseCategory


class MongoDBTokenCategory(TokenCategoryDBInterface, MongoDBBaseCategory):
    def __init__(self, db: Database[Mapping[str, Any] | Any]):
        super().__init__(db, 'tokens', 'Token')

    def get_token_categories_by_token(self, token_id: str) -> List[str]:
        return self.get_categories_by_item(token_id)

    def add_token_category(self, token_id: str, category_id: str) -> None:
        self.add_item_category(token_id, category_id)

    def delete_token_category(self, token_id: str, category_id: str) -> None:
        self.delete_item_category(token_id, category_id)
