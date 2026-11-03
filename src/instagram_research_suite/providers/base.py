"""Provider contract used by official integrations and user-supplied data imports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class FetchResult:
    """A result that reports its completeness instead of implying total coverage."""

    records: list[dict[str, Any]] = field(default_factory=list)
    expected_count: int | None = None
    completeness: str = "unknown"
    message: str = ""


class DataProvider(ABC):
    """Abstract interface for providers that comply with platform permissions."""

    name = "Unnamed provider"

    @abstractmethod
    def fetch_relationships(self, handle: str, list_type: str) -> FetchResult:
        """Fetch a permitted follower/following dataset for an authorised context."""
        raise NotImplementedError
