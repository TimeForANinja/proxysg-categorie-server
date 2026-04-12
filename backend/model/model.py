import uuid
from datetime import datetime

from db.abc.db import DBInterface
from model.category import CategoryModel
from model.mappings import MappingModel
from model.special import SpecialModel
from model.core import CoreModel
from model.token import TokenModel
from model.types.core import POINTER_CORE, Core, Commit, StateTreeRootNode
from model.url import URLModel
from util.branch_names import BRANCH_PROD


class MyModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend

        # init submodules
        self.categories = CategoryModel(backend)
        self.core = CoreModel(backend)
        self.mappings = MappingModel(backend)
        self.specials = SpecialModel(backend)
        self.tokens = TokenModel(backend)
        self.urls = URLModel(backend)

    def migrate(self):
        if not self.backend.has_key(POINTER_CORE):
            # create first prod commit
            first_commit = Commit(
                uuid=str(uuid.uuid4()),
                author="System",
                description="Initial commit",
                created_at=int(datetime.now().timestamp()),
                head=StateTreeRootNode(
                    categories=[],
                    tokens=[],
                    urls=[],
                    url_category_mappings=[],
                    token_category_mappings=[],
                ),
                parent_commit_hash=None,
            )
            first_commit_hash = first_commit.write(self.backend)
            # create core object
            new_core = Core(
                version=1,
                branches={BRANCH_PROD: first_commit_hash},
            )
            new_core.write(self.backend)
