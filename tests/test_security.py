import io
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config
from app import create_app
from PIL import Image


class SecurityTests(unittest.TestCase):
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
        self.client = self.app.test_client()

    def tearDown(self):
        self.photo_patch.stop()
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def csrf_token(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def test_login_post_without_csrf_token_is_rejected(self):
        response = self.client.post("/login", data={"password": "123456"})
        self.assertEqual(response.status_code, 400)

    def test_login_with_csrf_token_creates_session(self):
        token = self.csrf_token()
        response = self.client.post(
            "/login", data={"password": "123456", "csrf_token": token}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"].endswith("/"), True)

    def test_logout_requires_post_and_csrf_token(self):
        token = self.csrf_token()
        self.client.post("/login", data={"password": "123456", "csrf_token": token})

        get_response = self.client.get("/logout")
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post("/logout")
        self.assertEqual(post_response.status_code, 400)

    def test_new_event_with_photos_saves_photos(self):
        token = self.csrf_token()
        self.client.post("/login", data={"password": "123456", "csrf_token": token})

        buf = io.BytesIO()
        Image.new("RGB", (200, 150), "red").save(buf, format="JPEG")
        buf.seek(0)

        data = {
            "csrf_token": token,
            "title": "周末露营",
            "event_date": "2026-08-21",
            "location": "杭州",
            "content": "湖边过夜",
            "photos": (buf, "camp.jpg"),
        }
        response = self.client.post("/event/new", data=data,
                                    content_type="multipart/form-data")
        self.assertEqual(response.status_code, 302)
        location = response.headers["Location"]
        self.assertIn("/event/", location)

        # 事件已创建，且照片落库 + 落盘
        event_id = int(location.rstrip("/").split("/")[-1])
        detail = self.client.get(location)
        self.assertEqual(detail.status_code, 200)
        self.assertIn("周末露营".encode(), detail.data)

        event_dir = Path(self.photo_dir) / f"event_{event_id}"
        self.assertTrue(event_dir.exists())
        webp_files = [p for p in event_dir.glob("*.webp") if "_thumb" not in p.name]
        self.assertEqual(len(webp_files), 1)


if __name__ == "__main__":
    unittest.main()
