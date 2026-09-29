import os
import tempfile
import unittest

from app import create_app
from database import get_db


class UrlShortenerTests(unittest.TestCase):
    def setUp(self):
        self.database_file = tempfile.NamedTemporaryFile(delete=False)
        self.database_file.close()
        self.app = create_app({"TESTING": True, "DATABASE": self.database_file.name})
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.database_file.name)

    def test_creates_and_redirects_a_custom_link(self):
        response = self.client.post("/api/shorten", json={"original_url": "example.com/docs", "custom_url": "portfolio-demo"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["short_code"], "portfolio-demo")
        redirect_response = self.client.get("/portfolio-demo", follow_redirects=False)
        self.assertEqual(redirect_response.status_code, 302)
        self.assertEqual(redirect_response.headers["Location"], "https://example.com/docs")

    def test_rejects_invalid_requests_with_a_useful_400(self):
        cases = ({}, {"original_url": "ftp://example.com"}, {"original_url": "example.com", "expires_in_hours": "later"})
        for payload in cases:
            response = self.client.post("/api/shorten", json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)

    def test_rejects_an_alias_that_is_already_taken(self):
        payload = {"original_url": "https://example.com", "custom_url": "taken-link"}
        self.client.post("/api/shorten", json=payload)
        response = self.client.post("/api/shorten", json=payload)
        self.assertEqual(response.status_code, 409)

    def test_expired_link_returns_gone_page(self):
        with self.app.app_context():
            get_db().execute("INSERT INTO urls VALUES (?, ?, ?)", ("old-link", "https://example.com", 1))
            get_db().commit()
        response = self.client.get("/old-link")
        self.assertEqual(response.status_code, 410)

    def test_rate_limit_blocks_the_third_request_when_limit_is_two(self):
        limited_app = create_app(
            {
                "TESTING": True,
                "DATABASE": self.database_file.name,
                "RATE_LIMIT_MAX_REQUESTS": 2,
                "RATE_LIMIT_WINDOW_SECONDS": 300,
            }
        )
        limited_client = limited_app.test_client()
        payload = {"original_url": "https://example.com"}
        self.assertEqual(limited_client.post("/api/shorten", json=payload).status_code, 201)
        self.assertEqual(limited_client.post("/api/shorten", json=payload).status_code, 201)
        response = limited_client.post("/api/shorten", json=payload)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "300")


if __name__ == "__main__":
    unittest.main()
