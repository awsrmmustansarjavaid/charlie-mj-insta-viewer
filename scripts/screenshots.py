"""Render screenshots of every key screen (offscreen). Usage: python scripts/screenshots.py OUTDIR"""
import os
import sys
import tempfile
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication

from app.core.paths import get_data_directory
from app.data.database import Database
from app.services.monitor import run_cycle
from app.ui.context import AppContext
from app.ui.main_window import MainWindow
from app.ui.viewers import PostViewer, StoryViewer

out = Path(sys.argv[1] if len(sys.argv) > 1 else "shots"); out.mkdir(parents=True, exist_ok=True)
d = get_data_directory(tempfile.mkdtemp())
db = Database(d / "database" / "t.sqlite3"); db.initialize()
app = QApplication([]); ctx = AppContext(db, d)
ctx.snapshots.take("travel.diary", "followers"); ctx.snapshots.take("travel.diary", "following")
run_cycle(db, ctx.registry, "travel.diary")
db.upsert_monitor("travel.diary", 60)
db.save_setting("demo_epoch", 2); ctx.invalidate()
run_cycle(db, ctx.registry, "travel.diary")
ctx.snapshots.take("travel.diary", "followers")
w = MainWindow(ctx); w.resize(1480, 920); w.show()

def pump(n=40):
    for _ in range(n):
        app.processEvents(); time.sleep(0.02)

for key in ["dashboard", "feed", "profile", "followers", "insights", "engagement", "mentions",
            "snapshots", "timeline", "monitor", "providers", "settings", "compare"]:
    w.show_page(key); pump(60)
    w.grab().save(str(out / f"{key}.png"))
posts = ctx.registry.call("get_posts", "travel.diary", 20)
pv = PostViewer(ctx, posts, 0, w, 587); pv.show(); pump(60); pv.grab().save(str(out / "post_viewer.png"))
pv.tabs.setCurrentIndex(1); pump(10); pv.grab().save(str(out / "post_viewer_emoji.png")); pv.close()
sv = StoryViewer(ctx, [("travel.diary", ctx.registry.call("get_stories", "travel.diary"))], 0, w)
sv.show(); pump(30); sv.grab().save(str(out / "story_viewer.png")); sv.close()
print("done", len(list(out.glob("*.png"))))
