from typing import Dict, Any

from db.backend.abc.util.types import MyTransactionType


def mongo_transaction_kwargs(session: MyTransactionType | None) -> Dict[str, Any]:
    """
    Provides a utility method to generate transaction-related keyword arguments
    to be passed into database session operations.

    The method takes an optional session parameter and returns a dictionary
    containing the session if it's provided, otherwise it returns an empty
    dictionary.

    :param session: The database session to use.
    :return: A dictionary containing the session if it's provided, otherwise an empty dictionary.
    """
    if not session:
        return {}

    return {
        'session': session
    }
