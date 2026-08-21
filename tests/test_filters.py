import unittest

from app import create_app


class DateCnFilterTests(unittest.TestCase):
    """date_cn 过滤器跨平台行为（不依赖 %-m 等 GNU 扩展）。"""

    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True)

    def test_formats_chinese_date(self):
        with self.app.test_request_context():
            self.assertEqual(
                self.app.jinja_env.filters["date_cn"]("2026-08-24"),
                "2026年8月24日",
            )

    def test_zero_padded_day_kept_numeric(self):
        with self.app.test_request_context():
            self.assertEqual(
                self.app.jinja_env.filters["date_cn"]("2026-07-05"),
                "2026年7月5日",
            )

    def test_invalid_value_returns_as_is(self):
        with self.app.test_request_context():
            self.assertEqual(
                self.app.jinja_env.filters["date_cn"]("not-a-date"),
                "not-a-date",
            )


if __name__ == "__main__":
    unittest.main()
