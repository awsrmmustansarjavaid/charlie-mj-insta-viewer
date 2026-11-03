"""Small, deterministic analytics helpers."""

from __future__ import annotations

from collections import Counter
import re

from app.services.provider import Account, Comment


EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "]\uFE0F?"
)


def classify_accounts(accounts: list[Account]) -> dict[str, int]:
    """Count provider-supplied account categories without inferring gender."""
    result: Counter[str] = Counter()
    for account in accounts:
        result[account.account_type or "Unknown"] += 1
    return dict(result)


def emoji_counts(comments: list[Comment]) -> dict[str, int]:
    """Count emoji characters in retrieved comment text and visible replies."""
    counts: Counter[str] = Counter()

    def visit(comment: Comment) -> None:
        """Visit one comment and its nested replies."""
        counts.update(EMOJI_PATTERN.findall(comment.text))
        for reply in comment.replies:
            visit(reply)

    for item in comments:
        visit(item)
    return dict(counts.most_common())


def compare_usernames(
    older: list[str], newer: list[str]
) -> tuple[list[str], list[str]]:
    """Return newly observed and no-longer-observed usernames."""
    old_set, new_set = set(older), set(newer)
    return sorted(new_set - old_set), sorted(old_set - new_set)
