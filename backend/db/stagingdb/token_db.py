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

    def add_token(self, auth: AuthUser, token: str, mut_tok: MutableToken) -> Token:
        temp_id = str(uuid.uuid4())
        token_data = asdict(mut_tok)
        token_data.update({
            'id': temp_id,
            'token': token,
        })

        # Create a staged change
        staged_change = StagedChange(
            type=StagedChangeAction.ADD,
            table=StagedChangeTable.TOKEN,
            auth=auth,
            id=temp_id,
            data=token_data,
        )
        # Add the staged change to the staging DB
        self._staged.add(staged_change)

        # Create a Token object to return
        new_token = Token(**token_data)
        return new_token

    def get_token(self, token_id: str) -> Optional[Token]:
        # If not in staged tokens, get it from the database
        token: Token | StagedChange = self._db.tokens.get_token(token_id)

        if token is None:
            # no filter in DB, so check if we have an "add" filter
            token = self._staged.first_or_none(
                StageFilter.fac_filter_table_id(StagedChangeTable.TOKEN, token_id),
                StageFilter.filter_add,
            )

        # overload any staged changes
        for staged_change in self._staged.iter_filter(
                StageFilter.fac_filter_table_id(StagedChangeTable.TOKEN, token_id),
        ):
            if staged_change.data.get('is_deleted', 0) != 0:
                return None

            tmp = asdict(token)
            tmp.update(staged_change.data)
            token = Token(**tmp)

        return token

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

    def roll_token(self, auth: AuthUser, token_id: str, new_uuid: str) -> Token:
        update_data = {'token': new_uuid}

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
        raw_db_tokens: List[Token | StagedChange] = self._db.tokens.get_all_tokens()

        # append all "added" tokens from cache
        raw_db_tokens.extend(
            self._staged.iter_filter(
                StageFilter.filter_add,
                StageFilter.fac_filter_table(StagedChangeTable.TOKEN),
            )
        )

        staged_tokens: List[Token] = []

        for raw_token in raw_db_tokens:
            token = raw_token

            # overload any staged changes
            for staged_change in self._staged.iter():
                if staged_change.table != StagedChangeTable.TOKEN:
                    continue
                if staged_change.id != token.id:
                    continue

                tmp = asdict(token)
                tmp.update(staged_change.data)
                token = Token(**tmp)

            if token.is_deleted == 0:
                staged_tokens.append(token)

        return staged_tokens

    def commit(self, change: StagedChange) -> None:
        # TODO: implement
        pass
