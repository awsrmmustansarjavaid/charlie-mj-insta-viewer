import json
import zipfile

import pytest

from app.providers import data_export as de
from app.providers.base import ProviderError
from app.providers.demo import DemoProvider
from app.providers.graph_api import GraphApiProvider


def test_demo_has_587_complete_lists():
    d = DemoProvider()
    f, st = d.get_followers("travel.diary")
    g, _ = d.get_following("travel.diary")
    assert len(f) == 587 and len(g) == 587 and st.complete and st.expected_count == 587
    assert len({a.username for a in f}) == 587


def test_demo_epoch_changes_lists():
    a = {x.username for x in DemoProvider(0).get_followers("t")[0]}
    b = {x.username for x in DemoProvider(1).get_followers("t")[0]}
    assert len(b - a) == 5 and len(a - b) == 3


FOLLOWERS = [{"title": "", "string_list_data": [
    {"href": "https://www.instagram.com/alice", "value": "alice", "timestamp": 1700000000}]},
    {"string_list_data": [{"href": "https://www.instagram.com/bob", "value": "bob", "timestamp": 1700000500}]}]
FOLLOWING = {"relationships_following": [
    {"title": "carol", "string_list_data": [{"href": "https://www.instagram.com/carol", "timestamp": 1700001000}]},
    {"string_list_data": [{"href": "https://www.instagram.com/_u/dave"}]}]}


def _zip(tmp_path):
    p = tmp_path / "export.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("connections/followers_and_following/followers_1.json", json.dumps(FOLLOWERS[:1]))
        zf.writestr("connections/followers_and_following/followers_2.json", json.dumps(FOLLOWERS[1:]))
        zf.writestr("connections/followers_and_following/following.json", json.dumps(FOLLOWING))
    return p


def test_export_zip_merges_followers_files_and_keeps_timestamps(tmp_path):
    accs, st = de.load_export(_zip(tmp_path), "followers")
    assert [a.username for a in accs] == ["alice", "bob"] and st.complete
    assert accs[0].followed_at.startswith("2023-11-14")


def test_export_following_title_and_href_fallbacks(tmp_path):
    accs, _ = de.load_export(_zip(tmp_path), "following")
    assert [a.username for a in accs] == ["carol", "dave"]


def test_plain_text_and_csv(tmp_path):
    t = tmp_path / "l.txt"
    t.write_text("@a\nb\n\nA\n")
    assert [a.username for a in de.load_export(t, "followers")[0]] == ["a", "b"]
    c = tmp_path / "l.csv"
    c.write_text("username,display_name\nx,X Y\n")
    assert de.load_export(c, "followers")[0][0].display_name == "X Y"


def test_zip_without_expected_file_errors(tmp_path):
    p = tmp_path / "e.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("x.txt", "1")
    with pytest.raises(ValueError):
        de.load_export(p, "followers")


def make_graph(responses):
    calls = []

    def http(method, url, params):
        calls.append((method, url, params))
        for key, val in responses.items():
            if key in url:
                return val(params) if callable(val) else val
        raise AssertionError(url)
    g = GraphApiProvider("TOKEN", "123", "me", http=http)
    return g, calls


def test_graph_not_configured_is_permission_required():
    with pytest.raises(ProviderError) as e:
        GraphApiProvider().get_profile("me")
    assert e.value.status == "PERMISSION REQUIRED"


def test_graph_lists_are_not_public():
    g, _ = make_graph({})
    for fn in (g.get_followers, g.get_following):
        with pytest.raises(ProviderError) as e:
            fn("me")
        assert e.value.status == "NOT PUBLICLY AVAILABLE"


def test_graph_profile_and_comments_with_replies():
    g, calls = make_graph({
        "/123/comments".replace("/123", "/99"): {"data": [{"id": "c1", "text": "hi 😍", "username": "u", "like_count": 2,
            "replies": {"data": [{"id": "r1", "text": "yo", "username": "v"}]}}]},
        "/123": {"username": "me", "name": "Me", "followers_count": 10, "follows_count": 5, "media_count": 3},
    })
    prof = g.get_profile("me")
    assert prof.followers_count == 10 and prof.following_count == 5
    from app.providers.base import Post
    cm = g.get_comments(Post("99", "me"))
    assert cm[0].replies[0].text == "yo" and cm[0].likes == 2
    assert calls[-1][2]["access_token"] == "TOKEN"


def test_graph_business_discovery_for_other_account():
    g, calls = make_graph({"/123": {"business_discovery": {"username": "brand", "followers_count": 99}}})
    assert g.get_profile("@brand").followers_count == 99
    assert "business_discovery.username(brand)" in calls[0][2]["fields"]


def test_graph_audience_percentages():
    g, _ = make_graph({"insights": {"data": [{"total_value": {"breakdowns": [{"results": [
        {"dimension_values": ["F"], "value": 60}, {"dimension_values": ["M"], "value": 30},
        {"dimension_values": ["U"], "value": 10}]}]}}]}})
    a = g.get_audience("me")
    assert a.available and a.gender == {"Female": 60.0, "Male": 30.0, "Unknown": 10.0}


def test_graph_refuses_http():
    from app.providers.graph_api import default_http
    with pytest.raises(ProviderError):
        default_http("GET", "http://insecure.example", {})
