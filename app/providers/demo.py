"""Demo provider: fictional, deterministic, fully offline.

``epoch`` simulates the passage of time so that snapshots, diffs, monitoring
events and notifications can be demonstrated: every epoch removes a few old
accounts, adds new ones, publishes a new post and story, and (from epoch 2)
changes the bio. Nothing here touches Instagram.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.providers.base import (
    AVAILABLE,
    Account,
    Audience,
    Capability,
    Comment,
    Highlight,
    MediaItem,
    Mention,
    Post,
    ProfileInfo,
    ProgressFn,
    Provider,
    RetrievalStatus,
    Story,
    utcnow,
)

DEMO_USER = "travel.diary"
FIRST = ["sarah", "mike", "emma", "jack", "laura", "chris", "nina", "omar", "lena",
         "ravi", "zoe", "ben", "mia", "leo", "ana", "tom", "ivy", "sam", "eva", "dan",
         "kai", "ella", "noah", "ayla", "hugo", "rosa", "luca", "maya", "finn", "tara"]
LAST = ["jones", "smith", "wilson", "lee", "brown", "green", "stone", "khan", "park",
        "diaz", "moore", "hall", "fox", "wood", "shah", "king", "reed", "cole", "ford"]
BRANDS = ["foodie.life", "nature_lovers", "urban.vibes", "fitness.daily", "minimal.style",
          "bali.guide", "japan.today", "europe.trips", "daily.coffee", "photo.weekly",
          "wander.mag", "sunset.club", "peak.gear", "city.eats", "trail.notes"]
TYPES = ["Personal"] * 12 + ["Business"] * 3 + ["Creator"] * 2 + ["Brand", "Media"]
EMOJIS_POS = ["❤️", "😍", "🔥", "👏", "🙌", "😂", "💕", "👍", "✨", "🥰"]
COMMENT_TEXT = [
    "Amazing shot", "This place is unreal", "Take me with you next time",
    "Adding this to my bucket list", "The colors are incredible", "Wow, stunning view",
    "Love this", "Which month did you go?", "Best trip ever", "Goals", "So peaceful",
    "How much was the flight?", "Pure magic", "Need this vacation right now",
    "Not a fan of the crowds there tbh", "Overrated if you ask me",
]
PLACES = [("Bali, Indonesia", "bali"), ("Kyoto, Japan", "japan"), ("Santorini, Greece", "europe"),
          ("Yosemite, USA", "us"), ("Tokyo, Japan", "food"), ("Lofoten, Norway", "nature")]
HIGHLIGHTS = ["Bali", "Japan", "Europe", "US", "Food", "Nature"]


def _usernames(count: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    seen: set[str] = set()
    out: list[str] = []
    while len(out) < count:
        name = f"{rng.choice(FIRST)}{rng.choice(['.', '_', ''])}{rng.choice(LAST)}"
        if rng.random() < 0.5:
            name += str(rng.randint(1, 99))
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _account(name: str, rng: random.Random, followed_at: datetime) -> Account:
    kind = rng.choice(TYPES)
    return Account(
        username=name,
        display_name=name.replace(".", " ").replace("_", " ").title(),
        account_type=kind,
        visibility="Private" if kind == "Personal" and rng.random() < 0.3 else "Public",
        verified=rng.random() < 0.03,
        followed_at=followed_at.isoformat(timespec="seconds"),
    )


class DemoProvider(Provider):
    """Fictional sample data; deterministic for a given epoch."""

    name = "demo"
    label = "Demo data (offline)"
    description = "Fictional accounts for exploring every screen. No Instagram access."

    def __init__(self, epoch: int = 0):
        self.epoch = epoch
        self._my_replies: dict[str, list[Comment]] = {}
        self._pool = _usernames(1100, 7)

    # -- capability matrix ----------------------------------------------------
    def capabilities(self) -> list[Capability]:
        keys = ["Profile", "Followers", "Following", "Posts / Reels", "Comments",
                "Comment replies", "Stories", "Highlights", "Mentions",
                "Audience demographics"]
        return [Capability(k.lower(), k, AVAILABLE, "Fictional demo data") for k in keys]

    # -- profile --------------------------------------------------------------
    def get_profile(self, username: str) -> ProfileInfo:
        bio = "Exploring the world one place at a time 🌍\n📷 Photography | Lifestyle"
        if self.epoch >= 2:
            bio += "\n✈️ Booking trips for 2027"
        known = {DEMO_USER, *BRANDS}
        if username not in known:
            rng = random.Random(username)
            return ProfileInfo(
                username=username,
                display_name=username.replace(".", " ").title(),
                bio="Demo profile",
                followers_count=rng.randint(80, 9000),
                following_count=rng.randint(50, 900),
                posts_count=rng.randint(5, 300),
                account_type=rng.choice(TYPES),
                visibility="Public",
                avatar=f"seed:{username}",
            )
        if username != DEMO_USER:
            return ProfileInfo(username=username, display_name=username.title(),
                               bio="Demo page", followers_count=random.Random(username).randint(5000, 90000),
                               following_count=120, posts_count=400, account_type="Business",
                               visibility="Public", avatar=f"seed:{username}")
        followers, _ = self.get_followers(username)
        following, _ = self.get_following(username)
        return ProfileInfo(
            username=DEMO_USER, display_name="Travel Diary", bio=bio,
            followers_count=len(followers), following_count=len(following),
            posts_count=len(self.get_posts(username, 500)), verified=False,
            account_type="Creator", visibility="Public",
            external_url="linktr.ee/traveldiary", avatar=f"seed:{DEMO_USER}",
            category="Travel",
        )

    # -- lists ----------------------------------------------------------------
    def _lists(self) -> tuple[list[str], list[str]]:
        base_followers = self._pool[:587]
        base_following = self._pool[250:837]  # overlaps followers 250..586
        removed = 3 * self.epoch
        added = [f"newfan_{e}_{i}" for e in range(1, self.epoch + 1) for i in range(5)]
        followers = base_followers[removed:] + added
        following = base_following[2 * self.epoch:] + [f"{BRANDS[e % 15]}" for e in range(self.epoch)
                                                       if BRANDS[e % 15] not in base_following]
        return followers, following

    def _build(self, names: list[str], salt: int, progress: ProgressFn | None) -> list[Account]:
        rng = random.Random(salt)
        now = datetime.now(timezone.utc)
        out: list[Account] = []
        for i, name in enumerate(names):
            out.append(_account(name, random.Random(name), now - timedelta(days=rng.randint(1, 900))))
            if progress and (i % 50 == 0 or i == len(names) - 1):
                progress(i + 1, len(names))
        return out

    def _status(self, n: int, what: str) -> RetrievalStatus:
        return RetrievalStatus(
            source=self.label, retrieved_at=utcnow(), returned_count=n, expected_count=n,
            complete=True, message=f"Complete demo {what} list ({n} of {n}). Fictional accounts.")

    def get_followers(self, username, progress=None):
        followers, _ = self._lists()
        rows = self._build(followers, 1, progress)
        return rows, self._status(len(rows), "followers")

    def get_following(self, username, progress=None):
        _, following = self._lists()
        rows = self._build(following, 2, progress)
        return rows, self._status(len(rows), "following")

    # -- posts ----------------------------------------------------------------
    def get_posts(self, username: str, limit: int = 30) -> list[Post]:
        rng = random.Random(f"posts-{username}")
        total = 18 + self.epoch
        base = datetime.now(timezone.utc) - timedelta(hours=3)
        posts: list[Post] = []
        for i in range(total):
            place, tag = PLACES[i % len(PLACES)]
            kind = ["IMAGE", "IMAGE", "CAROUSEL", "REEL", "IMAGE", "VIDEO"][i % 6]
            n_media = 3 if kind == "CAROUSEL" else 1
            is_video = kind in ("REEL", "VIDEO")
            mentions = ""
            tagged: list[str] = []
            if i % 3 == 0:
                tagged = [rng.choice(BRANDS)]
                mentions = f" with @{tagged[0]}"
            posts.append(Post(
                id=f"{username}-p{total - i}", owner=username, kind=kind,
                caption=f"Sunset vibes 🌅 in {place}{mentions} #{tag} #travel #nature",
                timestamp=(base - timedelta(days=i * 2 + rng.randint(0, 1))).isoformat(timespec="seconds"),
                likes=rng.randint(15, 60), comments_count=rng.randint(20, 26),
                media=[MediaItem(seed=f"{username}-{total - i}-{m}", is_video=is_video, duration=12.0)
                       for m in range(n_media)],
                permalink=f"https://www.instagram.com/p/DEMO{total - i:04d}/",
                location=place, tagged=tagged,
            ))
        return posts[:limit]

    def get_comments(self, post: Post) -> list[Comment]:
        rng = random.Random(f"c-{post.id}")
        out: list[Comment] = []
        base = datetime.fromisoformat(post.timestamp) if post.timestamp else datetime.now(timezone.utc)
        for i in range(12):
            text = rng.choice(COMMENT_TEXT) + " " + " ".join(rng.choices(EMOJIS_POS, k=rng.randint(0, 3)))
            if rng.random() < 0.15:
                text += f" @{rng.choice(self._pool)}"
            c = Comment(id=f"{post.id}-c{i}", username=rng.choice(self._pool[:300]), text=text.strip(),
                        timestamp=(base + timedelta(minutes=10 + i * 37)).isoformat(timespec="seconds"),
                        likes=rng.randint(0, 60))
            for j in range(rng.choice([0, 0, 1, 2])):
                c.replies.append(Comment(
                    id=f"{c.id}-r{j}", username=rng.choice(self._pool[:300]),
                    text=rng.choice(COMMENT_TEXT[:8]) + " " + rng.choice(EMOJIS_POS),
                    timestamp=(base + timedelta(minutes=50 + i * 37 + j)).isoformat(timespec="seconds"),
                    likes=rng.randint(0, 20)))
            out.append(c)
        for c in out:
            c.replies.extend(self._my_replies.get(c.id, []))
        return out

    supports_write = True

    def reply_to_comment(self, post: Post, comment_id: str, text: str) -> Comment:
        """Store a demo reply locally (nothing is sent anywhere)."""
        reply = Comment(id=f"{comment_id}-mine-{len(self._my_replies.get(comment_id, []))}",
                        username=post.owner, text=text, timestamp=utcnow(), likes=0)
        self._my_replies.setdefault(comment_id, []).append(reply)
        return reply

    # -- stories / highlights ---------------------------------------------------
    def get_stories(self, username: str) -> list[Story]:
        rng = random.Random(f"s-{username}-{self.epoch}")
        now = datetime.now(timezone.utc)
        out = []
        for i in range(3 + self.epoch % 3):
            ment = [rng.choice(BRANDS)] if i % 2 == 0 else []
            out.append(Story(
                id=f"{username}-s{self.epoch}-{i}",
                owner=username,
                media=MediaItem(seed=f"{username}-story-{self.epoch}-{i}", is_video=i == 2, duration=6.0),
                timestamp=(now - timedelta(hours=i + 1)).isoformat(timespec="seconds"),
                mentions=ment, location=PLACES[i % len(PLACES)][0] if i == 1 else "",
                music="Ambient Waves — Demo Artist" if i == 2 else ""))
        return out

    def get_highlights(self, username: str) -> list[Highlight]:
        out = []
        now = datetime.now(timezone.utc)
        for i, title in enumerate(HIGHLIGHTS):
            stories = [Story(id=f"{username}-h{i}-{k}", owner=username,
                             media=MediaItem(seed=f"{username}-hl-{i}-{k}", is_video=False),
                             timestamp=(now - timedelta(days=30 * (i + 1))).isoformat(timespec="seconds"))
                       for k in range(4)]
            out.append(Highlight(id=f"{username}-h{i}", owner=username, title=title,
                                 cover=f"seed:{username}-hl-{i}-0", stories=stories))
        return out

    def get_mentions(self, username: str) -> list[Mention]:
        rng = random.Random(f"m-{username}")
        out = []
        for i in range(8 + 2 * self.epoch):
            kind = ["caption", "comment", "story", "tag"][i % 4]
            who = rng.choice(BRANDS + self._pool[:40])
            out.append(Mention(
                source_type=kind, by_user=who, mentioned_user=username,
                ref=f"demo-m{i}", preview={"caption": "Great trip with @travel.diary 🌍",
                                           "comment": "@travel.diary you have to see this!",
                                           "story": "Story mention", "tag": "Tagged in a photo"}[kind],
                timestamp=(datetime.now(timezone.utc) - timedelta(hours=i * 5)).isoformat(timespec="seconds")))
        return out

    def get_audience(self, username: str) -> Audience:
        return Audience(
            True, "Demo (simulates authorised Instagram Insights)",
            gender={"Female": 42.0, "Male": 34.0, "Unknown": 24.0},
            age={"13-17": 3.0, "18-24": 31.0, "25-34": 38.0, "35-44": 17.0, "45-54": 7.0, "55+": 4.0},
            countries={"United States": 28.0, "United Kingdom": 12.0, "India": 11.0, "Indonesia": 9.0,
                       "Pakistan": 6.0},
            note="Aggregate demographics as reported by Instagram Insights for an authorised account.")

    def suggested_accounts(self) -> list[ProfileInfo]:
        return [self.get_profile(b) for b in BRANDS[:6]]
