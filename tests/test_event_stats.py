"""事件统计：event_stats 返回计数与累计天数。"""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import config
from app import create_app


class EventStatsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "timeline.db")
        self.photo_dir = str(Path(self.temp_dir.name) / "photos")
        Path(self.photo_dir).mkdir()

        self.db_patch = patch.object(config, "DB_PATH", self.db_path)
        self.photo_patch = patch.object(config, "PHOTO_DIR", self.photo_dir)
        self.db_patch.start()
        self.photo_patch.start()

        self.app = create_app()
        self.app.config.update(TESTING=True)

        with self.app.app_context():
            from database import get_db, now

            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO timeline (name, password_hash, created_at) VALUES (?, ?, ?)",
                    ("我们的故事", "hash", now()),
                )
                conn.commit()
                self.timeline_id = conn.execute(
                    "SELECT id FROM timeline LIMIT 1"
                ).fetchone()["id"]
            finally:
                conn.close()

    def tearDown(self):
        self.photo_patch.stop()
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def insert_event(self, event_date):
        from database import get_db, now

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO event (timeline_id, title, event_date, created_at) "
                "VALUES (?, ?, ?, ?)",
                (self.timeline_id, "测试", event_date, now()),
            )
            conn.commit()
        finally:
            conn.close()

    def test_no_events_returns_zero(self):
        from models.event import event_stats

        count, days = event_stats(self.timeline_id)
        self.assertEqual(count, 0)
        self.assertEqual(days, 0)

    def test_days_from_earliest_to_today(self):
        from models.event import event_stats

        self.insert_event((date.today() - timedelta(days=9)).isoformat())
        self.insert_event(date.today().isoformat())

        count, days = event_stats(self.timeline_id)
        self.assertEqual(count, 2)
        self.assertEqual(days, 10)  # 最早那天算起，含今天

    def test_single_event_today_counts_one_day(self):
        from models.event import event_stats

        self.insert_event(date.today().isoformat())
        count, days = event_stats(self.timeline_id)
        self.assertEqual(count, 1)
        self.assertEqual(days, 1)


if __name__ == "__main__":
    unittest.main()
