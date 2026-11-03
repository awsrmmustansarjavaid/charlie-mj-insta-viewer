"""Unit tests for account and engagement analytics."""

from app.services.analytics import classify_accounts, compare_usernames, emoji_counts
from app.services.provider import Account, Comment


def test_classify_accounts_counts_categories():
    """Ensure account category counts are based on supplied provider fields."""
    accounts = [
        Account("one", "One", account_type="Personal"),
        Account("two", "Two", account_type="Business"),
        Account("three", "Three", account_type="Personal"),
    ]
    assert classify_accounts(accounts) == {"Personal": 2, "Business": 1}


def test_compare_usernames_returns_added_and_removed():
    """Ensure snapshot comparison identifies additions and removals."""
    added, removed = compare_usernames(["a", "b"], ["b", "c"])
    assert added == ["c"]
    assert removed == ["a"]


def test_emoji_counts_include_replies():
    """Ensure emoji counts include visible nested replies."""
    comments = [
        Comment("user1", "Love it ❤️😍", replies=[Comment("owner", "Thanks ❤️")])
    ]
    assert emoji_counts(comments) == {"❤️": 2, "😍": 1}
