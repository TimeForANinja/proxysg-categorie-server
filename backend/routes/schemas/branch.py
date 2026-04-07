from apiflask import Schema
from apiflask.fields import String
from model.types.core import BRANCH_PROD

class BranchQuery(Schema):
    branch: str = String(
        required=False,
        load_default=BRANCH_PROD,
        metadata={'description': 'Branch to use for the operation'}
    )
