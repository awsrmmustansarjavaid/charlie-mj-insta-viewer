"""Provider contract and demo implementation.

Real providers should use official, authorised interfaces and must preserve
pagination/completeness metadata. Never bypass platform access controls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass(slots=True)
class RetrievalStatus:
    """Describes exactly how much data a provider returned."""

    source: str
    retrieved_at: str
    returned_count: int
    expected_count: int | None
    complete: bool
    message: str


@dataclass(slots=True)
class Account:
    """A public/account-list record with conservative, non-sensitive fields."""

    username: str
    display_name: str
    account_type: str = "Personal"
    visibility: str = "Public"
    verified: bool = False
    profile_url: str = ""
    gender: str = "Unknown"


@dataclass(slots=True)
class Comment:
    """A comment and its provider-exposed replies."""

    username: str
    text: str
    likes: int = 0
    replies: list[Comment] = field(default_factory=list)


class InstagramDataProvider(Protocol):
    """Interface implemented by a permitted Instagram data provider."""

    def get_followers(self, profile: str) -> tuple[list[Account], RetrievalStatus]:
        """Return follower records and explicit completeness metadata."""
        ...

    def get_following(self, profile: str) -> tuple[list[Account], RetrievalStatus]:
        """Return following records and explicit completeness metadata."""
        ...


class DemoProvider:
    """Deterministic local sample provider; does not contact Instagram."""

    def _accounts(self, prefix: str, count: int) -> list[Account]:
        """Create sample records for UI demonstrations."""
        records: list[Account] = []
        types = ["Personal", "Creator", "Business", "Brand", "Media"]
        for index in range(1, count + 1):
            records.append(
                Account(
                    username=f"{prefix}_{index:03d}",
                    display_name=f"{prefix.title()} Account {index}",
                    account_type=types[(index - 1) % len(types)],
                    visibility="Public" if index % 4 else "Private",
                    verified=index % 29 == 0,
                    profile_url=f"https://www.instagram.com/{prefix}_{index:03d}/",
                )
            )
        return records

    def _status(self, count: int) -> RetrievalStatus:
        """Build a truthful status for the complete local sample dataset."""
        return RetrievalStatus(
            source="Local demo dataset",
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            returned_count=count,
            expected_count=count,
            complete=True,
            message="Complete demo dataset. These are fictional sample accounts.",
        )

    def get_followers(self, profile: str) -> tuple[list[Account], RetrievalStatus]:
        """Return 587 fictional follower records to demonstrate pagination."""
        records = self._accounts("follower", 587)
        return records, self._status(len(records))

    def get_following(self, profile: str) -> tuple[list[Account], RetrievalStatus]:
        """Return 587 fictional following records to demonstrate pagination."""
        records = self._accounts("following", 587)
        return records, self._status(len(records))
