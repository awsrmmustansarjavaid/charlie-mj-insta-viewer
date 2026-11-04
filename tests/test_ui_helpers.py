import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from app.ui.viewers import richtext  # noqa: E402
from app.utils import ago_long  # noqa: E402


def test_richtext_links_mentions_and_does_not_corrupt_markup():
    out = richtext("Trip with @peak.gear #bali & <b>x</b>", "#8B5CF6")
    assert 'href="user:peak.gear"' in out and "#bali</span>" in out
    assert out.count("<a ") == 1 and "&lt;b&gt;" in out and "&amp;" in out
    # the accent colour must survive intact (previous bug re-matched '#8B5CF6')
    assert out.count("#8B5CF6") == 2


def test_ago_long():
    assert ago_long("") == ""
    assert ago_long("2000-01-01T00:00:00+00:00").endswith("w ago")
