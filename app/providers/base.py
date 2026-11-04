"""Provider contract, shared data model and availability statuses.

Every data source implements :class:`Provider`. A provider that cannot supply
something must say so with an explicit availability status instead of
returning guesses. The UI renders those statuses to the user verbatim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Callable

# ---- availability statuses (shown as chips in the UI) -----------------------
AVAILABLE = "AVAILABLE"
PARTIAL = "PARTIALLY AVAILABLE"
NOT_PUBLIC = "NOT PUBLICLY AVAILABLE"
PERMISSION = "PERMISSION REQUIRED"
UNAVAILABLE = "PROVIDER UNAVAILABLE"
HISTORY = "HISTORICAL DATA REQUIRED"

ProgressFn = Callable[[int, "int | None"], None]


def utcnow() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ProviderError(Exception):
    """Raised when a provider cannot satisfy a request."""

    def __init__(self, message: str, status: str = UNAVAILABLE):
        super().__init__(message)
        self.status = status


@dataclass(slots=True)
class Capability:
    """One feature a provider does (or does not) support."""

    key: str
    label: str
    status: str
    note: str = ""


@dataclass(slots=True)
class RetrievalStatus:
    """Describes exactly how much data a provider returned."""

    source: str
    retrieved_at: str
    returned_count: int
    expected_count: int | None
    complete: bool
    message: str
    availability: str = AVAILABLE


@dataclass(slots=True)
class Account:
    """A follower/following list record. Gender is never inferred."""

    username: str
    display_name: str = ""
    account_type: str = "Unknown"
    visibility: str = "Unknown"
    verified: bool | None = None
    followed_at: str = ""
    profile_url: str = ""

    def __post_init__(self) -> None:
        if not self.profile_url and self.username:
            self.profile_url = f"https://www.instagram.com/{self.username}/"


@dataclass(slots=True)
class ProfileInfo:
    """Public profile details."""

    username: str
    display_name: str = ""
    bio: str = ""
    followers_count: int | None = None
    following_count: int | None = None
    posts_count: int | None = None
    verified: bool | None = None
    account_type: str = "Unknown"
    visibility: str = "Unknown"
    external_url: str = ""
    avatar: str = ""  # URL, file path, or "seed:<text>" for generated art
    category: str = ""


@dataclass(slots=True)
class MediaItem:
    """One image or video."""

    url: str = ""
    seed: str = ""
    is_video: bool = False
    duration: float = 0.0


@dataclass(slots=True)
class Comment:
    """A comment and its provider-exposed replies."""

    id: str
    username: str
    text: str
    timestamp: str = ""
    likes: int | None = None
    replies: list[Comment] = field(default_factory=list)


@dataclass(slots=True)
class Post:
    """A post, reel or carousel."""

    id: str
    owner: str
    kind: str = "IMAGE"  # IMAGE | VIDEO | CAROUSEL | REEL
    caption: str = ""
    timestamp: str = ""
    likes: int | None = None
    comments_count: int | None = None
    media: list[MediaItem] = field(default_factory=list)
    permalink: str = ""
    location: str = ""
    tagged: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Story:
    """A story frame."""

    id: str
    owner: str
    media: MediaItem
    timestamp: str = ""
    mentions: list[str] = field(default_factory=list)
    link: str = ""
    location: str = ""
    music: str = ""


@dataclass(slots=True)
class Highlight:
    """A highlight album."""

    id: str
    owner: str
    title: str
    cover: str = ""
    stories: list[Story] = field(default_factory=list)


@dataclass(slots=True)
class Mention:
    """An observed @mention. ``detected_at`` is when WE first saw it."""

    source_type: str  # caption | comment | story | tag
    by_user: str
    mentioned_user: str
    ref: str = ""
    preview: str = ""
    timestamp: str = ""


@dataclass(slots=True)
class Audience:
    """Aggregate audience demographics. Only from authorised insights."""

    available: bool
    source: str
    gender: dict[str, float] = field(default_factory=dict)
    age: dict[str, float] = field(default_factory=dict)
    countries: dict[str, float] = field(default_factory=dict)
    note: str = ""


def to_dict(obj: object) -> dict:
    """Serialise a dataclass to a plain dict."""
    return asdict(obj)  # type: ignore[call-overload]


class Provider:
    """Base class. Override what the source genuinely supports."""

    name = "base"
    label = "Base provider"
    description = ""
    supports_write = False

    def capabilities(self) -> list[Capability]:
        """Return the capability matrix for the Provider Manager screen."""
        return []

    def health(self) -> tuple[bool, int, str]:
        """Return (ok, response_ms, message)."""
        return True, 0, "OK"

    def _no(self, what: str, status: str = NOT_PUBLIC) -> ProviderError:
        return ProviderError(f"{self.label} cannot provide {what}.", status)

    def get_profile(self, username: str) -> ProfileInfo:
        raise self._no("profile details", UNAVAILABLE)

    def get_followers(
        self, username: str, progress: ProgressFn | None = None
    ) -> tuple[list[Account], RetrievalStatus]:
        raise self._no("follower lists")

    def get_following(
        self, username: str, progress: ProgressFn | None = None
    ) -> tuple[list[Account], RetrievalStatus]:
        raise self._no("following lists")

    def get_posts(self, username: str, limit: int = 30) -> list[Post]:
        raise self._no("posts")

    def get_comments(self, post: Post) -> list[Comment]:
        raise self._no("comments", PERMISSION)

    def reply_to_comment(self, post: Post, comment_id: str, text: str) -> Comment:
        raise self._no("comment replies", PERMISSION)

    def get_stories(self, username: str) -> list[Story]:
        raise self._no("stories", PERMISSION)

    def get_highlights(self, username: str) -> list[Highlight]:
        raise self._no("highlights")

    def get_mentions(self, username: str) -> list[Mention]:
        raise self._no("mentions", PERMISSION)

    def get_audience(self, username: str) -> Audience:
        return Audience(False, self.label, note="Not provided by this source.")

    def suggested_accounts(self) -> list[ProfileInfo]:
        return []
