from typing import Optional, List

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.token import MutableToken, Token


class StagingDBToken:
    def __init__(self, db: DBInterface):
        self._db = db

    def add_token(self, auth: AuthUser, uuid: str, mut_tok: MutableToken) -> Token:
        new_token = self._db.tokens.add_token(uuid, mut_tok)
        self._db.history.add_history_event(f'Token {new_token.id} created', auth, [new_token.id], [], [])
        return new_token

    def get_token(self, token_id: str) -> Optional[Token]:
        return self._db.tokens.get_token(token_id)

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        return self._db.tokens.get_token_by_uuid(token_uuid)

    def update_token(self, auth: AuthUser, token_id: str, token: MutableToken) -> Token:
        new_token = self._db.tokens.update_token(token_id, token)
        self._db.history.add_history_event(f'Token {token_id} updated', auth, [token_id], [], [])
        return new_token

    def update_usage(self, token_id: str) -> None:
        return self._db.tokens.update_usage(token_id)

    def roll_token(self, auth: AuthUser, token_id: str, uuid: str) -> Token:
        new_token = self._db.tokens.roll_token(token_id, uuid)
        self._db.history.add_history_event(f'Token {token_id} rolled', auth, [token_id], [], [])
        return new_token

    def delete_token(self, auth: AuthUser, token_id: str) -> None:
        self._db.tokens.delete_token(token_id)
        self._db.history.add_history_event(f'Token {token_id} deleted', auth, [token_id], [], [])

    def get_all_tokens(self) -> List[Token]:
        return self._db.tokens.get_all_tokens()
