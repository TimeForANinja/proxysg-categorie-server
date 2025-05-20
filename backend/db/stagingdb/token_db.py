import time
from dataclasses import asdict
from typing import Optional, List, Dict, Any
import uuid

from auth.auth_user import AuthUser
from db.abc.db import DBInterface
from db.abc.token import MutableToken, Token
from db.stagingdb.cache import StagedChange, StagedChangeAction, StagedCollection, StagedChangeTable, StageFilter


class StagingDBToken:
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_token(self, auth: AuthUser, mut_tok: MutableToken) -> Token:
        token_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        token_data = asdict(mut_tok)
        token_data.update({
            'id': token_id,
            'token': token,
        })

        # Create a staged change
        staged_change = StagedChange(
            type=StagedChangeAction.ADD,
            table=StagedChangeTable.TOKEN,
            auth=auth,
            id=token_id,
            data=token_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        # Create a Token object to return
        return Token(**token_data)

    def get_token(self, token_id: str) -> Optional[Token]:
        # try getting it from the database
        db_token: Token = self._db.tokens.get_token(token_id)
        # convert to dict
        token: Dict[str, Any] = asdict(db_token) if db_token is not None else None

        if token is None:
            # no token in DB, so check if we have an "add" event
            add_token = self._staged.first_or_none(
                StageFilter.fac_filter_table_id(StagedChangeTable.TOKEN, token_id),
                StageFilter.filter_add,
            )
            token = add_token.data if add_token is not None else None

        # overload any staged changes
        for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.TOKEN, token_id),
        ):
            if staged_change.data.get('is_deleted', 0) != 0:
                return None

            token.update(staged_change.data)

        return Token(**token)

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        # fetching by UUID goes straight to DB
        return self._db.tokens.get_token_by_uuid(token_uuid)

    def update_token(self, auth: AuthUser, token_id: str, mut_tok: MutableToken) -> Token:
        update_data = asdict(mut_tok)

        # Create a staged change
        staged_change = StagedChange(
            type=StagedChangeAction.UPDATE,
            table=StagedChangeTable.TOKEN,
            auth=auth,
            id=token_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_token(token_id)

    def update_usage(self, token_id: str) -> None:
        # Usage updates go straight to DB
        self._db.tokens.update_usage(token_id)

    def roll_token(self, auth: AuthUser, token_id: str) -> Token:
        new_token_val = str(uuid.uuid4())
        update_data = {'token': new_token_val}

        # Create a staged change
        staged_change = StagedChange(
            type=StagedChangeAction.UPDATE,
            table=StagedChangeTable.TOKEN,
            auth=auth,
            id=token_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_token(token_id)

    def delete_token(self, auth: AuthUser, token_id: str) -> None:
        update_data = {'is_deleted': int(time.time())}

        # Create a staged change
        staged_change = StagedChange(
            type=StagedChangeAction.DELETE,
            table=StagedChangeTable.TOKEN,
            auth=auth,
            id=token_id,
            data=update_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        return self.get_token(token_id)

    def get_all_tokens(self) -> List[Token]:
        # Get all tokens from the database
        db_tokens: List[Token] = self._db.tokens.get_all_tokens()
        # convert to dict
        tokens: List[Dict[str, Any]] = [asdict(token) for token in db_tokens]

        # append all "added" tokens from cache
        tokens.extend(
            [
                t.data for t in
                self._staged.iter_filter(
                    StageFilter.filter_add,
                    StageFilter.fac_filter_table(StagedChangeTable.TOKEN),
                )
            ]
        )

        staged_tokens: List[Token] = []

        for raw_token in tokens:
            token = raw_token

            # overload any staged changes
            for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.TOKEN, token.get('id'))
            ):
                token.update(staged_change.data)

            if token.get('is_deleted', 0) == 0:
                staged_tokens.append(Token(**token))

        return staged_tokens

    def commit(self, change: StagedChange) -> None:
        # TODO: implement
        pass
