from typing import Optional, Union, Tuple
from uuid import uuid4

from db.abc.db import DBInterface
from model.util.error import CanError, ModelError
from model.types.mappings import TokenCategoryMapping
from model.types.token import Token
from model.types.core import Commit


class TokenModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend

    def _find_token(self, commit: Commit, token_id: str) -> Union[Tuple[Token, str], Tuple[None, None]]:
        for token_hash in commit.head.tokens:
            token = Token.read(self.backend, token_hash)
            if token.id == token_id:
                return token, token_hash
        return None, None

    def roll_token(self, branch: str, token_id: str) -> CanError[Token]:
        """Roll the value of a Token"""
        commit = Commit.read_branch(self.backend, branch)

        token, token_hash = self._find_token(commit, token_id)
        if not token:
            return None, ModelError("Token not found")

        # update token
        token.token_value = str(uuid4())
        new_token_hash = token.write(self.backend)

        # update commit with new token
        commit.head.tokens.remove(token_hash)
        commit.head.tokens.append(new_token_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return token, None

    def create_token(self, branch: str, description: str) -> Token:
        """Create a new Token"""
        commit = Commit.read_branch(self.backend, branch)

        # create token
        new_token = Token.new(description)
        new_token_hash = new_token.write(self.backend)

        # update commit with new token
        commit.head.tokens.append(new_token_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return new_token

    def update_token(
            self,
            branch: str, token_id: str,
            description: Optional[str],
    ) -> CanError[Token]:
        """Update the description of an existing Token"""
        commit = Commit.read_branch(self.backend, branch)

        token, token_hash = self._find_token(commit, token_id)
        if not token:
            return None, ModelError("Token not found")

        # update token
        if description is not None:
            token.description = description
        new_token_hash = token.write(self.backend)

        # update commit with new token
        commit.head.tokens.remove(token_hash)
        commit.head.tokens.append(new_token_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return token, None

    def delete_token(self, branch: str, token_id: str) -> Optional[ModelError]:
        """Delete a Token by ID"""
        commit = Commit.read_branch(self.backend, branch)

        token, token_hash = self._find_token(commit, token_id)
        if not token:
            return ModelError("Token not found")

        # update commit, removing the token
        commit.head.tokens.remove(token_hash)
        self._remove_token_related(commit, token_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None

    def _remove_token_related(self, commit: Commit, token_id: str) -> None:
        # all mappings using this token
        category_mappings_to_remove = []
        for map_hash in commit.head.token_category_mappings:
            mapping = TokenCategoryMapping.read(self.backend, map_hash)
            if mapping.token_id == token_id:
                category_mappings_to_remove.append(map_hash)
        for m in category_mappings_to_remove:
            commit.head.token_category_mappings.remove(m)
