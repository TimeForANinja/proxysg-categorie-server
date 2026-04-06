from typing import List, Optional
from uuid import uuid4

from db.abc.db import DBInterface
from model.types.tags import Commit
from model.types.token import Token


class TokenModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def roll_token(self, branch: str, token_id: str) -> Token:
        """Roll the value of a Token"""
        commit = Commit.read_branch(self.backend, branch)

        for token_hash in commit.head.tokens:
            token = Token.read(self.backend, token_hash)
            if token.id != token_id:
                continue

            # update token
            token.token_value = str(uuid4())
            new_token_hash = token.write(self.backend)

            # update commit with new token
            commit.head.tokens.remove(token_hash)
            commit.head.tokens.append(new_token_hash)

            # update user's tag with new commit
            commit.write_branch(self.backend, branch)

            return token
        raise Exception("Token not found")

    def create_token(self, branch: str, description: str, categories: List[str]) -> Token:
        """Create a new Token with the given description and categories"""
        commit = Commit.read_branch(self.backend, branch)

        new_token = Token(
            id=str(uuid4()),
            token_value=str(uuid4()),
            description=description,
            categories=categories,
        )

        new_token_hash = new_token.write(self.backend)

        # update commit with new token
        commit.head.tokens.append(new_token_hash)

        # update user's tag with new commit
        commit.write_branch(self.backend, branch)

        return new_token

    def update_token(
            self,
            branch: str, token_id: str,
            description: Optional[str], categories: Optional[List[str]]
    ) -> Token:
        """Update the description and categories of an existing Token"""
        commit = Commit.read_branch(self.backend, branch)

        for token_hash in commit.head.tokens:
            token = Token.read(self.backend, token_hash)
            if token.id != token_id:
                continue

            # update token
            if description is not None:
                token.description = description
            if categories is not None:
                token.categories = categories
            new_token_hash = token.write(self.backend)

            # update commit with new token
            commit.head.tokens.remove(token_hash)
            commit.head.tokens.append(new_token_hash)

            # update user's tag with new commit
            commit.write_branch(self.backend, branch)

            return token
        raise Exception("Token not found")

    def delete_token(self, branch: str, token_id: str):
        """Delete a Token by ID"""
        commit = Commit.read_branch(self.backend, branch)

        for token_hash in commit.head.tokens:
            token = Token.read(self.backend, token_hash)
            if token.id != token_id:
                continue

            # update commit, removing the token
            commit.head.tokens.remove(token_hash)

            # update user's tag with new commit
            commit.write_branch(self.backend, branch)

            return
        raise Exception("Token not found")
