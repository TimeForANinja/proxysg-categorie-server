from db.abc.db import DBInterface
from model.category import CategoryModel
from model.tags import TagModel
from model.token import TokenModel


class MyModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend

        # init submodules
        self.tags = TagModel(backend)
        self.tokens = TokenModel(backend)
        self.categories = CategoryModel(backend)
