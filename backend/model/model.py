from db.abc.db import DBInterface
from model.category import CategoryModel
from model.special import SpecialModel
from model.tags import TagModel
from model.token import TokenModel
from model.types.core import POINTER_CORE, Core, BRANCH_PROD
from model.types.tags import StateTreeRootNode, Commit


class MyModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend

        # init submodules
        self.tags = TagModel(backend)
        self.tokens = TokenModel(backend)
        self.categories = CategoryModel(backend)
        self.specials = SpecialModel(backend)

    def migrate(self):
        if not self.backend.has_key(POINTER_CORE):
            # create first prod commit
            first_commit = Commit(
                author="System",
                description="Initial commit",
                head=StateTreeRootNode(categories=[], tokens=[]),
                parent_commit_hash=None,
            )
            first_commit_hash = first_commit.write(self.backend)
            # create core object
            new_core = Core(
                version=1,
                branches={BRANCH_PROD: first_commit_hash},
            )
            new_core.write(self.backend)
