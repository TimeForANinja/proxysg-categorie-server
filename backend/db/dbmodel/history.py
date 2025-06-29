from dataclasses import field, dataclass
from typing import Optional, List

from auth.auth_user import AuthUser
from routes.restmodel.history import RESTHistory, RESTAtomic


@dataclass
class Atomic:
    """Helper class to represent an atomic change within a history event."""
    id: str
    user: AuthUser
    action: str
    description: str
    timestamp: int
    ref_token: List[str] = field(default_factory=list)
    ref_url: List[str] = field(default_factory=list)
    ref_category: List[str] = field(default_factory=list)

    def to_rest(self) -> RESTAtomic:
        return RESTAtomic(
            id=self.id,
            user=self.user.username,
            action=self.action,
            description=self.description,
            timestamp=self.timestamp,
            ref_token=self.ref_token,
            ref_url=self.ref_url,
            ref_category=self.ref_category,
        )


@dataclass
class History:
    """Helper class to represent a category."""
    id: str
    time: int
    user: AuthUser
    description: Optional[str]
    ref_token: List[str]
    ref_url: List[str]
    ref_category: List[str]
    atomics: List[Atomic]

    def to_rest(self) -> RESTHistory:
        return RESTHistory(
            id=self.id,
            time=self.time,
            user=self.user.username,
            description=self.description,
            ref_token=self.ref_token,
            ref_url=self.ref_url,
            ref_category=self.ref_category,
            atomics=[x.to_rest() for x in self.atomics],
        )
