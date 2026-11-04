"""Offscreen smoke tests: every page opens, viewers render, key flows work."""

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.core.paths import get_data_directory  # noqa: E402
from app.data.database import Database  # noqa: E402
from app.ui.context import AppContext  # noqa: E402
from app.ui.main_window import MainWindow  # noqa: E402
from app.ui.viewers import PostViewer, StoryViewer  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def win(qapp, tmp_path):
    d = get_data_directory(str(tmp_path))
    db = Database(d / "database" / "t.sqlite3")
    db.initialize()
    ctx = AppContext(db, d)
    w = MainWindow(ctx)
    w.show()
    yield w
    w.scheduler.timer.stop()
    w._really_quit = True
    w.close()


def pump(app, n=25):
    for _ in range(n):
        app.processEvents()
        time.sleep(0.01)


def test_every_page_opens(qapp, win):
    for key in win.pages:
        win.show_page(key)
        pump(qapp)
    assert len(win.pages) == 17


def test_followers_page_shows_complete_587(qapp, win):
    win.ctx.snapshots.take("travel.diary", "followers")
    win.ctx.snapshots.take("travel.diary", "following")
    win.show_page("followers")
    pump(qapp)
    page = win.pages["followers"]
    assert page.model.rowCount() == 587 and "587 of 587 loaded" in page.loaded.text()
    assert page.tabbar.tabText(2).startswith("Mutuals")


def test_post_viewer_navigation_and_comments(qapp, win):
    posts = win.ctx.registry.call("get_posts", "travel.diary", 10)
    v = PostViewer(win.ctx, posts, 0, win, 587)
    v.show()
    pump(qapp, 60)
    assert "comment(s) retrieved" in v.comments_view.toPlainText()
    v.go(1)
    assert v.i == 1
    v.close()


def test_demo_reply_roundtrip(qapp, win):
    prov = win.ctx.registry.active
    post = prov.get_posts("travel.diary", 1)[0]
    c = prov.get_comments(post)[0]
    prov.reply_to_comment(post, c.id, "thanks!")
    assert prov.get_comments(post)[0].replies[-1].text == "thanks!"


def test_story_viewer_advances(qapp, win):
    stories = win.ctx.registry.call("get_stories", "travel.diary")
    v = StoryViewer(win.ctx, [("travel.diary", stories)], 0, win)
    v.show()
    v.next()
    assert v.s == 1
    v.close()


def test_theme_switch_applies(qapp, win):
    win.ctx.theme.mode, win.ctx.theme.card_style = "Light", "Minimal"
    win.ctx.save_theme()
    pump(qapp)
    assert "#F3F5FB" in qapp.styleSheet()


def test_followers_search_filters_rows(qapp, win):
    win.ctx.snapshots.take("travel.diary", "followers")
    win.show_page("followers")
    pump(qapp)
    page = win.pages["followers"]
    page.search.setText("zoe")
    pump(qapp, 5)
    shown = page.proxy.rowCount()
    assert 0 < shown < 587
    assert all("zoe" in page.proxy.data(page.proxy.index(r, 2)) for r in range(shown))
