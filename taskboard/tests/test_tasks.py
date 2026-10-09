import os
import tempfile
import unittest

from app import create_app


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({"DATABASE_PATH": self.db_path, "TESTING": True})
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_list_tasks_empty(self):
        resp = self.client.get("/api/tasks")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_create_task(self):
        resp = self.client.post("/api/tasks", json={"title": "Write lab guide"})
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["title"], "Write lab guide")
        self.assertEqual(body["status"], "todo")

    def test_update_task_status(self):
        create_resp = self.client.post("/api/tasks", json={"title": "Ship feature"})
        task_id = create_resp.get_json()["id"]

        update_resp = self.client.patch(f"/api/tasks/{task_id}", json={"status": "done"})
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.get_json()["status"], "done")

    def test_update_missing_task_404s(self):
        resp = self.client.patch("/api/tasks/999", json={"status": "done"})
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
