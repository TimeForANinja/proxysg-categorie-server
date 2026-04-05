from typing import List, Optional
from uuid import uuid4

from db.abc.db import DBInterface
from model.types.tags import Commit
from model.types.token import Token
from model.util.tag_name import build_user_tag


class TokenModel:
    def __init__(self, backend: DBInterface):
        self.backend = backend


    def roll_token(self, author: str, token_id: str) -> Token:
        """Roll the value of a Token"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)

        commit = Commit.read(self.backend, commit_hash)
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
            new_commit_hash = commit.write(self.backend)

            # update user's tag with new commit
            self.backend.insert_kv(author_tag, new_commit_hash)

            return token

        raise Exception("Token not found")

    def create_token(self, author: str, description: str, categories: List[str]) -> Token:
        """Create a new Token with the given description and categories"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)
        commit = Commit.read(self.backend, commit_hash)

        new_token = Token(
            id=str(uuid4()),
            token_value=str(uuid4()),
            description=description,
            categories=categories,
        )

        new_token_hash = new_token.write(self.backend)

        # update commit with new token
        commit.head.tokens.append(new_token_hash)
        new_commit_hash = commit.write(self.backend)

        # update user's tag with new commit
        self.backend.insert_kv(author_tag, new_commit_hash)

        return new_token

    def update_token(
            self,
            author: str, token_id: str,
            description: Optional[str], categories: Optional[List[str]]
    ) -> Token:
        """Update the description and categories of an existing Token"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)
        commit = Commit.read(self.backend, commit_hash)

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
            new_commit_hash = commit.write(self.backend)

            # update user's tag with new commit
            self.backend.insert_kv(author_tag, new_commit_hash)

            return token

        raise Exception("Token not found")

    def delete_token(self, author: str, token_id: str):
        """Delete a Token by ID"""
        author_tag = build_user_tag(author)
        commit_hash = self.backend.fetch_kv(author_tag)
        commit = Commit.read(self.backend, commit_hash)

        for token_hash in commit.head.tokens:
            token = Token.read(self.backend, token_hash)
            if token.id != token_id:
                continue

            # update commit, removing the token
            commit.head.tokens.remove(token_hash)
            new_commit_hash = commit.write(self.backend)

            # update user's tag with new commit
            self.backend.insert_kv(author_tag, new_commit_hash)

            return
        raise Exception("Token not found")
