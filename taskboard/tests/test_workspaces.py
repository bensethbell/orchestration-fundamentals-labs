import os
import tempfile
import unittest

from app import create_app
from app.db import (
    add_member,
    create_workspace,
    get_db,
    get_member_role,
    list_workspaces_for_user,
)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({"DATABASE_PATH": self.db_path, "TESTING": True})
        self.ctx = self.app.app_context()
        self.ctx.push()
        db = get_db()
        db.execute("INSERT INTO user (id, name, email) VALUES (1, 'Ada', 'a@x.com')")
        db.execute("INSERT INTO user (id, name, email) VALUES (2, 'Grace', 'g@x.com')")
        db.commit()

    def tearDown(self):
        self.ctx.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_workspace(self):
        ws = create_workspace("Engineering")
        self.assertEqual(ws["name"], "Engineering")
        self.assertIsNotNone(ws["id"])

    def test_add_member_with_role(self):
        ws = create_workspace("Engineering")
        add_member(ws["id"], 1, "admin")
        self.assertEqual(get_member_role(ws["id"], 1), "admin")

    def test_list_workspaces_for_user_with_several(self):
        eng = create_workspace("Engineering")
        mkt = create_workspace("Marketing")
        other = create_workspace("Other")
        add_member(eng["id"], 1, "admin")
        add_member(mkt["id"], 1, "member")
        add_member(other["id"], 2, "member")
        result = list_workspaces_for_user(1)
        self.assertEqual([w["name"] for w in result], ["Engineering", "Marketing"])
        self.assertEqual([w["role"] for w in result], ["admin", "member"])

    def test_non_member_gets_no_role(self):
        ws = create_workspace("Engineering")
        add_member(ws["id"], 1, "admin")
        self.assertIsNone(get_member_role(ws["id"], 2))
        self.assertEqual(list_workspaces_for_user(2), [])


if __name__ == "__main__":
    unittest.main()
