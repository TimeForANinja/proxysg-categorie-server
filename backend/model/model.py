from typing import Dict, Any

from db.abc.db import DBInterface
from model.category import CategoryModel
from model.mappings import MappingModel
from model.special import SpecialModel
from model.core import CoreModel
from model.token import TokenModel
from model.types.core import POINTER_CORE, Core, Commit
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
        # try to load "core" object
        core = None
        try:
            core = self.backend.batch_fetch_obj([POINTER_CORE])[0]
        except Exception:
            pass

        if not core:
            # create first prod commit
            first_commit = Commit.new("System", "Initial commit",None)
            first_commit_hash = first_commit.write(self.backend)
            # create core object
            new_core = Core(
                version=1,
                branches={BRANCH_PROD: first_commit_hash},
            )
            new_core.write(self.backend)

    def get_metrics(self) -> Dict[str, Any]:
        prod_commit = Commit.read_branch(self.backend, BRANCH_PROD)
        return {
            **self.backend.get_metrics(),
            "model-categories": len(prod_commit.head.categories),
            "model-tokens": len(prod_commit.head.tokens),
            "model-urls": len(prod_commit.head.urls),
            "model-url-category-mappings": len(prod_commit.head.url_category_mappings),
            "model-token-category-mappings": len(prod_commit.head.token_category_mappings),
        }
