import time
from dataclasses import asdict
from typing import Optional, List
import uuid

from auth.auth_user import AuthUser
from db.backend.abc.db import DBInterface
from db.dbmodel.history import Atomic
from db.dbmodel.staging import ActionType, ActionTable
from db.dbmodel.token import MutableToken, Token
from db.middleware.abc.token_db import MiddlewareDBToken
from db.middleware.stagingdb.cache import StagedChange, StagedCollection
from db.middleware.stagingdb.utils.add_uid import add_uid_to_object
from db.middleware.stagingdb.utils.overloading import add_staged_change, get_and_overload_object, get_and_overload_all_objects
from db.middleware.stagingdb.utils.update_cats import set_categories


class StagingDBToken(MiddlewareDBToken):
    def __init__(self, db: DBInterface, staged: StagedCollection):
        self._db = db
        self._staged = staged

    def add_token(self, auth: AuthUser, mut_tok: MutableToken) -> Token:
        # Generate a UUID for the token ID and get the data
        token_id, token_data = add_uid_to_object(mut_tok)

        # Generate a UUID for the token value
        token_data.update({
            'token': str(uuid.uuid4()),
        })

        add_staged_change(
            action_type=ActionType.ADD,
            action_table=ActionTable.TOKEN,
            auth=auth,
            obj_id=token_id,
            update_data=token_data,
            staged=self._staged,
        )

        # Create a Token object to return
        return Token(**token_data)

    def get_token(self, token_id: str) -> Optional[Token]:
        return get_and_overload_object(
            db_getter=self._db.tokens.get_token,
            staged=self._staged,
            action_table=ActionTable.TOKEN,
            obj_id=token_id,
            obj_class=Token
        )

    def get_token_by_uuid(self, token_uuid: str) -> Optional[Token]:
        # fetching by UUID goes straight to DB
        return self._db.tokens.get_token_by_uuid(token_uuid)

    def update_token(self, auth: AuthUser, token_id: str, mut_tok: MutableToken) -> Token:
        add_staged_change(
            action_type=ActionType.UPDATE,
            action_table=ActionTable.TOKEN,
            auth=auth,
            obj_id=token_id,
            update_data=asdict(mut_tok),
            staged=self._staged,
        )
        return self.get_token(token_id)

    def update_usage(self, token_id: str) -> None:
        # Usage updates go straight to DB
        self._db.tokens.update_usage(token_id)

    def roll_token(self, auth: AuthUser, token_id: str) -> Token:
        add_staged_change(
            action_type=ActionType.UPDATE,
            action_table=ActionTable.TOKEN,
            auth=auth,
            obj_id=token_id,
            update_data={'token': str(uuid.uuid4())},
            staged=self._staged,
        )
        return self.get_token(token_id)

    def delete_token(self, auth: AuthUser, token_id: str) -> None:
        add_staged_change(
            action_type=ActionType.DELETE,
            action_table=ActionTable.TOKEN,
            auth=auth,
            obj_id=token_id,
            update_data={'is_deleted': int(time.time())},
            staged=self._staged,
        )

    def get_all_tokens(self) -> List[Token]:
        return get_and_overload_all_objects(
            db_getter=self._db.tokens.get_all_tokens,
            staged=self._staged,
            action_table=ActionTable.TOKEN,
            obj_class=Token
        )

    def commit(self, change: StagedChange, dry_run: bool) -> Optional[Atomic]:
        """
        Apply the staged change to the persistent database.

        :param change: The staged change to apply.
        :param dry_run: Whether to perform a dry run (no changes are made to the database). Default is False.
        :return: The atomic operation that was applied to the database.
        """
        if change.action_table != ActionTable.TOKEN:
            return None

        # Apply the change to the persistent database based on the action type
        if change.action_type == ActionType.ADD:
            # Create a MutableToken from the data
            token_data = change.data.copy()
            token_id = token_data.pop('id')
            token_value = token_data.pop('token')
            mutable_token = MutableToken(**token_data)

            if not dry_run:
                # Add the token to the persistent database
                self._db.tokens.add_token(token_id, mutable_token, token_value)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Add",
                description=f"Added token {token_data.get('name')}",
                ref_token=[token_id],
            )
        elif change.action_type == ActionType.UPDATE:
            # Create a MutableToken from the data
            token_data = change.data.copy()

            # Check if this is a token roll update (only contains the 'token' field)
            if 'token' in token_data and len(token_data) == 1:
                if not dry_run:
                    # Roll the token in the persistent database
                    self._db.tokens.roll_token(change.uid, token_data['token'])

                # Create atomic to append to the history event
                return Atomic.new(
                    user=change.auth,
                    action="Update",
                    description=f"Rolled token {token_data.get('name')}",
                    ref_token=[change.uid],
                )
            else:
                # Create a MutableToken from the data
                mutable_token = MutableToken(**token_data)

                if not dry_run:
                    # Update the token in the persistent database
                    self._db.tokens.update_token(change.uid, mutable_token)

                # Create atomic to append to the history event
                return Atomic.new(
                    user=change.auth,
                    action="Update",
                    description=f"Updated token {token_data.get('name')}",
                    ref_token=[change.uid],
                )
        elif change.action_type == ActionType.SET_CATS:
            token_data = change.data.copy()

            current_cats = self._db.tokens.get_token(change.uid)

            # Update the token in the persistent database
            added, removed = set_categories(
                current_cats.categories,
                token_data['categories'],
                lambda cid: self._db.token_categories.add_token_category(change.uid, cid),
                lambda cid: self._db.token_categories.delete_token_category(change.uid, cid),
                dry_run,
            )

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Set Categories",
                description=f"Updated Categories for Token {token_data.get('name')}, added {added}, removed {removed}",
                ref_token=[change.uid],
            )
        elif change.action_type == ActionType.DELETE:
            if not dry_run:
                # Delete the token from the persistent database
                self._db.tokens.delete_token(change.uid)

            # Create atomic to append to the history event
            return Atomic.new(
                user=change.auth,
                action="Delete",
                description=f"Deleted token {change.data.get('name')}",
                ref_token=[change.uid],
            )

        # Unknown action_type
        return None
