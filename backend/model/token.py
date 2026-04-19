from typing import Optional, Dict, List
from uuid import uuid4

from db.abc.db import DBInterface
from model.util.error import CanError, ModelError
from model.types.mappings import TokenCategoryMapping
from model.types.token import Token
from model.types.core import Commit
from model.util.find import find_in_lists, find_all_in_lists
from routes.types.token import RestTokenDetail


class TokenModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def fetch_tokens(self, branch: str) -> List[RestTokenDetail]:
        """Fetch a list of all Tokens"""
        head_commit = Commit.read_branch(self.backend, branch)

        # Fetch LUTs
        token_lut = head_commit.head.token_lut(self.backend)
        category_lut = head_commit.head.category_lut(self.backend)

        # create base-objects for every Token
        data: Dict[str, RestTokenDetail] = {
            token_id: RestTokenDetail(
                token=token_lut[token_id],
                categories=[],
            )
            for token_id in token_lut
        }

        # fill our category properties based on our mappings
        mappings = TokenCategoryMapping.batch_read(self.backend, head_commit.head.token_category_mappings)
        for mapping in mappings:
            data[mapping.token_id].categories.append(
                category_lut[mapping.category_id]
            )

        return list(data.values())

    def create_token(self, branch: str, description: str) -> Token:
        """Create a new Token"""
        commit = Commit.read_branch(self.backend, branch)

        # create token
        new_token = Token.new(description)
        new_token_hash = Token.batch_write(self.backend, [new_token])[0]

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

        token, token_hash = find_in_lists(
            Token.batch_read(self.backend, commit.head.tokens),
            commit.head.tokens,
            lambda u: u.id == token_id
        )
        if not token:
            return None, ModelError("Token not found")

        # update token
        if description is not None:
            token.description = description
        new_token_hash = Token.batch_write(self.backend, [token])[0]

        # update commit with new token
        commit.head.tokens.remove(token_hash)
        commit.head.tokens.append(new_token_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return token, None

    def roll_token(self, branch: str, token_id: str) -> CanError[Token]:
        """Roll the value of a Token"""
        commit = Commit.read_branch(self.backend, branch)

        token, token_hash = find_in_lists(
            Token.batch_read(self.backend, commit.head.tokens),
            commit.head.tokens,
            lambda u: u.id == token_id
        )
        if not token:
            return None, ModelError("Token not found")

        # update token
        token.token_value = str(uuid4())
        new_token_hash = Token.batch_write(self.backend, [token])[0]

        # update commit with new token
        commit.head.tokens.remove(token_hash)
        commit.head.tokens.append(new_token_hash)

        # update branch with new commit
        commit.write_branch(self.backend, branch)

        return token, None

    def delete_token(self, branch: str, token_id: str) -> Optional[ModelError]:
        """Delete a Token by ID"""
        commit = Commit.read_branch(self.backend, branch)

        token, token_hash = find_in_lists(
            Token.batch_read(self.backend, commit.head.tokens),
            commit.head.tokens,
            lambda u: u.id == token_id
        )
        if not token:
            return ModelError("Token not found")

        # update commit, removing the token
        commit.head.tokens.remove(token_hash)
        self._remove_token_related(commit, token_id)

        # update branch with new commit
        commit.write_branch(self.backend, branch)
        return None

    def _remove_token_related(self, commit: Commit, token_id: str) -> None:
        mappings = TokenCategoryMapping.batch_read(self.backend, commit.head.token_category_mappings)
        # filter out all hashes that use this token
        _, keep_hashes = find_all_in_lists(
            mappings,
            commit.head.token_category_mappings,
            lambda m: m.token_id != token_id
        )
        commit.head.token_category_mappings = keep_hashes
