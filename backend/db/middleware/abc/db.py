from abc import ABC, abstractmethod

from db.middleware.stagingdb.category_db import StagingDBCategory
from db.middleware.stagingdb.history_db import StagingDBHistory
from db.middleware.stagingdb.sub_category_db import StagingDBSubCategory
from db.middleware.stagingdb.task_db import StagingDBTask
from db.middleware.stagingdb.token_category_db import StagingDBTokenCategory
from db.middleware.stagingdb.token_db import StagingDBToken
from db.middleware.stagingdb.url_category_db import StagingDBURLCategory
from db.middleware.stagingdb.url_db import StagingDBURL


class MiddlewareDB(ABC):
    categories: StagingDBCategory
    sub_categories: StagingDBSubCategory
    history: StagingDBHistory
    tokens: StagingDBToken
    token_categories: StagingDBTokenCategory
    urls: StagingDBURL
    url_categories: StagingDBURLCategory
    tasks: StagingDBTask

    @abstractmethod
    def close(self):
        """Method to trigger any cleanup actions."""
        pass
