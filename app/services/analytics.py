"""Deterministic analytics helpers. No network, no Qt, fully unit-tested."""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime

from app.providers.base import Account, Comment, Post

_EMOJI_CHAR = "[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\u2764\u2728]"
EMOJI_PATTERN = re.compile(
    rf"{_EMOJI_CHAR}\uFE0F?[\U0001F3FB-\U0001F3FF]?(?:\u200d{_EMOJI_CHAR}\uFE0F?)*")
MENTION_PATTERN = re.compile(r"(?<![\w.])@([A-Za-z0-9._]{1,30})")
HASHTAG_PATTERN = re.compile(r"#([\w]{1,60})")

# "Reaction-style" groups requested by the user. These are counted from the
# emoji found in retrieved comments, NOT from Instagram's like button.
EMOJI_GROUPS: dict[str, str] = {
    "Hearts & love": "❤💕💖💗💓💞💘😍🥰😘🧡💛💚💙💜🖤🤍",
    "Thumbs up": "👍👌🤝",
    "Laughing": "😂🤣😆😹",
    "Fire": "🔥💯",
    "Applause": "👏🙌🙏",
    "Sparkles": "✨⭐🌟",
    "Sad / negative": "😢😭😡👎😠🤮💔",
}
_POSITIVE_WORDS = {"amazing", "love", "stunning", "beautiful", "best", "wow", "incredible", "goals",
                   "magic", "peaceful", "great", "awesome", "perfect", "unreal", "gorgeous"}
_NEGATIVE_WORDS = {"overrated", "not a fan", "boring", "bad", "worst", "fake", "ugly", "hate", "crowded",
                   "disappointing", "scam"}


def norm_emoji(e: str) -> str:
    """Remove variation selectors so ❤ and ❤️ count together."""
    return e.replace("\uFE0F", "")


def classify_accounts(accounts: list[Account]) -> dict[str, int]:
    """Count provider-supplied account categories. Gender is never inferred."""
    return dict(Counter(a.account_type or "Unknown" for a in accounts))


def visibility_counts(accounts: list[Account]) -> dict[str, int]:
    return dict(Counter(a.visibility or "Unknown" for a in accounts))


def verified_counts(accounts: list[Account]) -> dict[str, int]:
    c: Counter[str] = Counter()
    for a in accounts:
        c["Unknown" if a.verified is None else ("Verified" if a.verified else "Not verified")] += 1
    return dict(c)


def flatten_comments(comments: list[Comment]) -> list[Comment]:
    """Return comments and all nested replies as one list."""
    out: list[Comment] = []
    for c in comments:
        out.append(c)
        out.extend(flatten_comments(c.replies))
    return out


def emoji_counts(comments: list[Comment]) -> dict[str, int]:
    """Count emoji characters in retrieved comments and visible replies."""
    counts: Counter[str] = Counter()
    for c in flatten_comments(comments):
        counts.update(norm_emoji(e) for e in EMOJI_PATTERN.findall(c.text))
    return dict(counts.most_common())


def emoji_group_counts(counts: dict[str, int]) -> dict[str, int]:
    """Roll individual emoji counts into the friendly groups above."""
    out = {g: 0 for g in EMOJI_GROUPS}
    out["Other"] = 0
    for emoji, n in counts.items():
        for group, chars in EMOJI_GROUPS.items():
            if emoji and emoji[0] in chars:
                out[group] += n
                break
        else:
            out["Other"] += n
    return {k: v for k, v in out.items() if v}


def sentiment(comments: list[Comment]) -> dict[str, int]:
    """Very rough lexicon sentiment. Indicative only, not a scientific measure."""
    result = {"Positive": 0, "Neutral": 0, "Negative": 0}
    neg_emoji = set(EMOJI_GROUPS["Sad / negative"])
    pos_emoji = set("".join(v for k, v in EMOJI_GROUPS.items() if k != "Sad / negative"))
    for c in flatten_comments(comments):
        t = c.text.lower()
        score = sum(w in t for w in _POSITIVE_WORDS) - sum(w in t for w in _NEGATIVE_WORDS)
        for e in EMOJI_PATTERN.findall(c.text):
            ch = norm_emoji(e)[:1]
            score += 1 if ch in pos_emoji else (-1 if ch in neg_emoji else 0)
        result["Positive" if score > 0 else "Negative" if score < 0 else "Neutral"] += 1
    return result


def top_commenters(comments: list[Comment], n: int = 10) -> list[tuple[str, int]]:
    return Counter(c.username for c in flatten_comments(comments)).most_common(n)


def extract_mentions(text: str) -> list[str]:
    return list(dict.fromkeys(m.lower() for m in MENTION_PATTERN.findall(text or "")))


def extract_hashtags(text: str) -> list[str]:
    return [h.lower() for h in HASHTAG_PATTERN.findall(text or "")]


def hashtag_frequency(posts: list[Post], n: int = 15) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for p in posts:
        c.update(extract_hashtags(p.caption))
    return c.most_common(n)


def engagement_rate(post: Post, followers: int | None) -> float | None:
    """(likes + comments) / followers × 100, or None when inputs are missing."""
    if not followers or post.likes is None:
        return None
    return round(100 * (post.likes + (post.comments_count or 0)) / followers, 2)


def _parse(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def posting_patterns(posts: list[Post]) -> tuple[dict[str, int], dict[int, int]]:
    """Posts per weekday and per hour of day."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    by_day = {d: 0 for d in days}
    by_hour = {h: 0 for h in range(24)}
    for p in posts:
        dt = _parse(p.timestamp)
        if dt:
            by_day[days[dt.weekday()]] += 1
            by_hour[dt.hour] += 1
    return by_day, by_hour


def compare_usernames(older: list[str], newer: list[str]) -> tuple[list[str], list[str]]:
    """Return (newly observed, no longer observed) usernames."""
    o, n = set(older), set(newer)
    return sorted(n - o), sorted(o - n)


def relationships(followers: list[Account], following: list[Account]) -> dict[str, list[Account]]:
    """Mutuals, accounts that don't follow back, and fans you don't follow."""
    fset = {a.username.lower() for a in followers}
    gset = {a.username.lower() for a in following}
    return {
        "Mutuals": [a for a in following if a.username.lower() in fset],
        "Not Following Back": [a for a in following if a.username.lower() not in fset],
        "You Don't Follow Back": [a for a in followers if a.username.lower() not in gset],
    }


def percent(part: int, whole: int) -> float:
    return round(100 * part / whole, 1) if whole else 0.0
