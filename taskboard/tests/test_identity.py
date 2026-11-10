import unittest

from flask import Flask

from app import identity


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "test"

    def test_header_identifies_user(self):
        with self.app.test_request_context(headers={"X-User-Id": "2"}):
            self.assertEqual(identity.get_current_user_id(), 2)

    def test_no_header_or_session_means_nobody(self):
        with self.app.test_request_context():
            self.assertIsNone(identity.get_current_user_id())

    def test_bad_header_means_nobody(self):
        with self.app.test_request_context(headers={"X-User-Id": "abc"}):
            self.assertIsNone(identity.get_current_user_id())

    def test_session_identifies_user(self):
        with self.app.test_request_context():
            identity.set_current_user_id(3)
            self.assertEqual(identity.get_current_user_id(), 3)


if __name__ == "__main__":
    unittest.main()
