"""Official Meta Instagram Graph API provider.

Works with an Instagram **Business or Creator** account that you own (or that
has authorised your Meta app) using an access token. It uses only documented
endpoints:

* own profile / media / comments / replies / stories / tags / insights
* ``business_discovery`` for *public* data of other Business/Creator accounts
  (profile counts + recent media with like/comment counts)

It deliberately does **not** provide follower/following username lists,
highlights, or other accounts' comments: Meta does not expose those. The
capability matrix says so and the UI shows it. Use the data-export importer for
complete lists of your own account.

The HTTP layer is injectable so the provider is unit-testable offline.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable

from app.providers.base import (
    AVAILABLE,
    NOT_PUBLIC,
    PARTIAL,
    PERMISSION,
    UNAVAILABLE,
    Account,
    Audience,
    Capability,
    Comment,
    MediaItem,
    Mention,
    Post,
    ProfileInfo,
    Provider,
    ProviderError,
    RetrievalStatus,
    Story,
)

HttpFn = Callable[[str, str, dict], dict]

_PROFILE_FIELDS = ("username,name,biography,followers_count,follows_count,media_count,"
                   "profile_picture_url,website")
_MEDIA_FIELDS = ("id,caption,media_type,media_product_type,media_url,thumbnail_url,permalink,"
                 "timestamp,like_count,comments_count,children{media_type,media_url,thumbnail_url}")


def default_http(method: str, url: str, params: dict) -> dict:
    """Perform an HTTPS request and decode the JSON body."""
    if not url.lower().startswith("https://"):
        raise ProviderError("Only HTTPS endpoints are allowed.", UNAVAILABLE)
    data = None
    if method == "GET":
        url = f"{url}?{urllib.parse.urlencode(params)}"
    else:
        data = urllib.parse.urlencode(params).encode()
    request = urllib.request.Request(url, data=data, method=method)  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=25) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            err = json.loads(exc.read().decode("utf-8")).get("error", {})
            msg = err.get("message", str(exc))
            code = err.get("code")
        except Exception:  # noqa: BLE001
            msg, code = str(exc), None
        status = PERMISSION if code in (10, 200, 190, 102) or exc.code in (401, 403) else UNAVAILABLE
        raise ProviderError(f"Meta API error: {msg}", status) from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"Network error: {exc.reason}", UNAVAILABLE) from exc


def _media_items(node: dict) -> list[MediaItem]:
    """Images use ``url``; videos use the thumbnail as ``url`` and keep the
    playable address in ``seed``."""
    children = (node.get("children") or {}).get("data") or []
    items = []
    for child in children or [node]:
        if child.get("media_type") == "VIDEO":
            items.append(MediaItem(url=child.get("thumbnail_url", "") or "",
                                   seed=child.get("media_url", "") or "", is_video=True))
        else:
            items.append(MediaItem(url=child.get("media_url", "") or ""))
    return items


def _post(owner: str, node: dict) -> Post:
    kind = node.get("media_type", "IMAGE")
    if node.get("media_product_type") == "REELS":
        kind = "REEL"
    return Post(id=node["id"], owner=owner, kind=kind, caption=node.get("caption", ""),
                timestamp=node.get("timestamp", ""), likes=node.get("like_count"),
                comments_count=node.get("comments_count"), media=_media_items(node),
                permalink=node.get("permalink", ""))


def _comment(node: dict) -> Comment:
    replies = [_comment(r) for r in ((node.get("replies") or {}).get("data") or [])]
    return Comment(id=node["id"], username=node.get("username", ""), text=node.get("text", ""),
                   timestamp=node.get("timestamp", ""), likes=node.get("like_count"), replies=replies)


class GraphApiProvider(Provider):
    """Official, token-based provider."""

    name = "graph"
    label = "Instagram Graph API (official)"
    description = ("Authorised Business/Creator accounts: your profile, posts, comments, replies, "
                   "stories, tagged media, audience insights; public stats of other Business/Creator "
                   "accounts via business discovery.")
    supports_write = True

    def __init__(self, access_token: str = "", ig_user_id: str = "", username: str = "",
                 api_version: str = "v23.0", host: str = "https://graph.facebook.com",
                 http: HttpFn | None = None):
        self.token = access_token
        self.ig_id = ig_user_id
        self.own_username = username.lstrip("@").lower()
        self.base = f"{host.rstrip('/')}/{api_version}"
        self._http = http or default_http

    # -- plumbing -------------------------------------------------------------
    def configured(self) -> bool:
        return bool(self.token and self.ig_id)

    def _call(self, method: str, path: str, **params: object) -> dict:
        if not self.configured():
            raise ProviderError("Add your access token and Instagram user ID in Provider Manager.",
                                PERMISSION)
        params["access_token"] = self.token
        return self._http(method, f"{self.base}/{path.lstrip('/')}", {k: str(v) for k, v in params.items()})

    def _paged(self, path: str, limit: int, **params: object) -> list[dict]:
        out: list[dict] = []
        body = self._call("GET", path, limit=min(limit, 50), **params)
        while True:
            out.extend(body.get("data", []))
            nxt = (body.get("paging") or {}).get("next")
            if not nxt or len(out) >= limit:
                break
            body = self._http("GET", nxt.split("?")[0], dict(urllib.parse.parse_qsl(nxt.split("?", 1)[1])))
        return out[:limit]

    def _is_own(self, username: str) -> bool:
        return not username or username.lstrip("@").lower() in ("", self.own_username)

    # -- capabilities / health --------------------------------------------------
    def capabilities(self) -> list[Capability]:
        ok = AVAILABLE if self.configured() else PERMISSION
        return [
            Capability("profile", "Profile", ok, "Own account; other Business/Creator accounts via discovery"),
            Capability("followers", "Followers list", NOT_PUBLIC, "Meta provides counts only. Use data-export import."),
            Capability("following", "Following list", NOT_PUBLIC, "Meta provides counts only. Use data-export import."),
            Capability("posts", "Posts / Reels", ok, "Own: full. Others: public Business/Creator accounts"),
            Capability("comments", "Comments", PARTIAL if self.configured() else PERMISSION, "Your own media only"),
            Capability("replies", "Comment replies", PARTIAL if self.configured() else PERMISSION,
                       "Needs instagram_manage_comments; your own media only"),
            Capability("stories", "Stories", PARTIAL if self.configured() else PERMISSION, "Your own active stories"),
            Capability("highlights", "Highlights", NOT_PUBLIC, "Not exposed by the API"),
            Capability("mentions", "Mentions", PARTIAL if self.configured() else PERMISSION,
                       "Tagged media + @mentions seen in your captions/comments; story mentions need webhooks"),
            Capability("audience", "Audience demographics", PARTIAL if self.configured() else PERMISSION,
                       "Aggregate only; needs ≥100 followers"),
        ]

    def health(self) -> tuple[bool, int, str]:
        if not self.configured():
            return False, 0, "Not configured"
        start = time.perf_counter()
        try:
            self._call("GET", self.ig_id, fields="username")
        except ProviderError as exc:
            return False, int((time.perf_counter() - start) * 1000), str(exc)
        return True, int((time.perf_counter() - start) * 1000), "Connected"

    # -- data -------------------------------------------------------------------
    def get_profile(self, username: str) -> ProfileInfo:
        if self._is_own(username):
            d = self._call("GET", self.ig_id, fields=_PROFILE_FIELDS)
        else:
            q = f"business_discovery.username({username.lstrip('@')}){{{_PROFILE_FIELDS}}}"
            d = self._call("GET", self.ig_id, fields=q).get("business_discovery", {})
        return ProfileInfo(
            username=d.get("username", username), display_name=d.get("name", ""),
            bio=d.get("biography", ""), followers_count=d.get("followers_count"),
            following_count=d.get("follows_count"), posts_count=d.get("media_count"),
            account_type="Business/Creator", visibility="Public",
            external_url=d.get("website", ""), avatar=d.get("profile_picture_url", ""))

    def get_posts(self, username: str, limit: int = 30) -> list[Post]:
        if self._is_own(username):
            rows = self._paged(f"{self.ig_id}/media", limit, fields=_MEDIA_FIELDS)
            owner = self.own_username or username
        else:
            u = username.lstrip("@")
            q = f"business_discovery.username({u}){{media.limit({min(limit, 50)}){{{_MEDIA_FIELDS}}}}}"
            d = self._call("GET", self.ig_id, fields=q).get("business_discovery", {})
            rows, owner = (d.get("media") or {}).get("data", []), u
        return [_post(owner, r) for r in rows]

    def get_comments(self, post: Post) -> list[Comment]:
        rows = self._paged(f"{post.id}/comments", 200,
                           fields="id,text,username,timestamp,like_count,"
                                  "replies{id,text,username,timestamp,like_count}")
        return [_comment(r) for r in rows]

    def reply_to_comment(self, post: Post, comment_id: str, text: str) -> Comment:
        body = self._call("POST", f"{comment_id}/replies", message=text)
        return Comment(id=body.get("id", ""), username=self.own_username, text=text)

    def get_stories(self, username: str) -> list[Story]:
        if not self._is_own(username):
            raise self._no("other accounts' stories", PERMISSION)
        rows = self._paged(f"{self.ig_id}/stories", 50,
                           fields="id,media_type,media_url,thumbnail_url,timestamp,permalink")
        out = []
        for r in rows:
            video = r.get("media_type") == "VIDEO"
            out.append(Story(id=r["id"], owner=self.own_username or username,
                             media=MediaItem(url=r.get("thumbnail_url" if video else "media_url", "") or "",
                                             seed=r.get("media_url", "") if video else "", is_video=video),
                             timestamp=r.get("timestamp", "")))
        return out

    def get_mentions(self, username: str) -> list[Mention]:
        if not self._is_own(username):
            raise self._no("other accounts' mentions", PERMISSION)
        rows = self._paged(f"{self.ig_id}/tags", 50, fields="id,caption,username,timestamp,permalink")
        me = self.own_username or username
        return [Mention("tag", r.get("username", ""), me, ref=r["id"],
                        preview=(r.get("caption") or "Tagged in a post")[:140],
                        timestamp=r.get("timestamp", "")) for r in rows]

    def get_audience(self, username: str) -> Audience:
        if not self._is_own(username):
            return Audience(False, self.label, note="Demographics exist only for accounts you own.")
        try:
            body = self._call("GET", f"{self.ig_id}/insights", metric="follower_demographics",
                              period="lifetime", metric_type="total_value", breakdown="gender")
        except ProviderError as exc:
            return Audience(False, self.label, note=str(exc))
        results = []
        for item in body.get("data", []):
            for bd in (item.get("total_value") or {}).get("breakdowns", []):
                results.extend(bd.get("results", []))
        total = sum(float(r.get("value", 0)) for r in results) or 0.0
        if not total:
            return Audience(False, self.label,
                            note="Instagram returned no demographic data (needs ≥100 followers).")
        names = {"F": "Female", "M": "Male", "U": "Unknown"}
        gender = {names.get(r["dimension_values"][0], r["dimension_values"][0]):
                  round(100 * float(r["value"]) / total, 1) for r in results}
        return Audience(True, "Instagram Insights (authorised)", gender=gender,
                        note="Aggregate demographics reported by Instagram.")

    def get_followers(self, username, progress=None) -> tuple[list[Account], RetrievalStatus]:
        raise ProviderError(
            "Meta's API provides follower counts only, not the username list. "
            "Import your Instagram data export in Followers & Following.", NOT_PUBLIC)

    def get_following(self, username, progress=None) -> tuple[list[Account], RetrievalStatus]:
        raise ProviderError(
            "Meta's API provides following counts only, not the username list. "
            "Import your Instagram data export in Followers & Following.", NOT_PUBLIC)
