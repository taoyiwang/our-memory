import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.datastructures import FileStorage

from services import image_service


class ImageServiceTests(unittest.TestCase):
    def test_rejects_file_with_image_extension_but_invalid_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            upload = FileStorage(
                stream=io.BytesIO(b"this is not an image"),
                filename="memory.jpg",
            )

            with patch.object(image_service.config, "PHOTO_DIR", temp_dir):
                with self.assertRaisesRegex(ValueError, "有效图片"):
                    image_service.save_upload(upload, event_id=7)

            self.assertFalse(Path(temp_dir, "event_7").exists())


if __name__ == "__main__":
    unittest.main()
