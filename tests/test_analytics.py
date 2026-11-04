from app.providers.base import Account, Comment, Post
from app.services import analytics as an


def C(text, replies=()):
    return Comment("1", "u", text, replies=list(replies))


def test_emoji_counts_include_replies_and_normalise_variation_selector():
    comments = [C("love ❤️ ❤ 🔥", [C("😂 ❤️")])]
    counts = an.emoji_counts(comments)
    assert counts["❤"] == 3 and counts["🔥"] == 1 and counts["😂"] == 1


def test_emoji_groups_hearts_and_thumbs():
    counts = an.emoji_counts([C("❤️😍💕👍👍")])
    groups = an.emoji_group_counts(counts)
    assert groups["Hearts & love"] == 3 and groups["Thumbs up"] == 2


def test_sentiment_is_indicative():
    s = an.sentiment([C("Amazing 😍"), C("overrated"), C("ok")])
    assert s == {"Positive": 1, "Neutral": 1, "Negative": 1}


def test_mentions_and_hashtags():
    assert an.extract_mentions("hi @Bob and @a.b_c, email x@y.com") == ["bob", "a.b_c"]
    assert an.extract_hashtags("#Bali #travel") == ["bali", "travel"]


def test_relationships_and_classification_never_infer_gender():
    f = [Account("a"), Account("b"), Account("c")]
    g = [Account("b"), Account("c"), Account("d")]
    r = an.relationships(f, g)
    assert [a.username for a in r["Mutuals"]] == ["b", "c"]
    assert [a.username for a in r["Not Following Back"]] == ["d"]
    assert [a.username for a in r["You Don't Follow Back"]] == ["a"]
    assert "Female" not in an.classify_accounts(f)


def test_engagement_rate_handles_missing():
    assert an.engagement_rate(Post("1", "o", likes=90, comments_count=10), 1000) == 10.0
    assert an.engagement_rate(Post("1", "o", likes=None), 1000) is None
    assert an.engagement_rate(Post("1", "o", likes=5), None) is None


def test_posting_patterns():
    posts = [Post("1", "o", timestamp="2026-11-02T10:00:00+00:00")]  # Monday
    by_day, by_hour = an.posting_patterns(posts)
    assert by_day["Mon"] == 1 and by_hour[10] == 1


def test_parse_username():
    from app.utils import parse_username
    assert parse_username("https://www.instagram.com/Travel.Diary/?hl=en") == "travel.diary"
    assert parse_username("@Bob ") == "bob"
    assert parse_username("instagram.com/_u/x_y") == "x_y"
