from typing import List, Optional

from db.backend.abc.git_tree import TagsDBInterface, BaseSetDBInterface
from db.backend.sqlite.util.cursor_callable import GetCursorProtocol
from db.backend.sqlite.util.groups import join_str_group, split_opt_str_group


class SQLiteTags(TagsDBInterface):
    def __init__(self, get_cursor: GetCursorProtocol):
        self.get_cursor = get_cursor

    def set_tag_hash(self, label: str, hash: str):
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO tags (label, hash) VALUES (?, ?) ON CONFLICT(label) DO UPDATE SET hash = excluded.hash',
                (label, hash)
            )

    def get_tag_hash(self, label: str) -> Optional[str]:
        with self.get_cursor() as cursor:
            cursor.execute('SELECT hash FROM tags WHERE label = ?', (label,))
            row = cursor.fetchone()
            return row[0] if row else None


class SQLiteBaseSet(BaseSetDBInterface):
    def __init__(self, get_cursor: GetCursorProtocol):
        self.get_cursor = get_cursor

    def insert(self, uuid: str, type: str, entries: List[str]):
        entries_str = join_str_group(entries)
        with self.get_cursor() as cursor:
            cursor.execute(
                'INSERT INTO sets (uuid, type, entries) VALUES (?, ?, ?)',
                (uuid, type, entries_str)
            )

    def get(self, uuid: str, type: str) -> Optional[List[str]]:
        with self.get_cursor() as cursor:
            cursor.execute('SELECT entries FROM sets WHERE uuid = ? AND type = ?', (uuid, type))
            row = cursor.fetchone()
            return split_opt_str_group(row[0])
