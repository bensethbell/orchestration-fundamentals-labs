"""Load the demo data used throughout the course labs.

    python seed_demo.py

Safe to run as often as you like: it only adds rows that are missing and
never deletes anything.

Users are seeded right away. Workspaces and memberships are seeded only once
the workspace schema exists (Unit 1 of the feature), so run this again after
that unit lands. It expects these exact names, as given in Lab 1:

    workspace        (id, name)
    workspace_member (workspace_id, user_id, role)   role is 'admin' or 'member'
"""
import sqlite3

from app import create_app
from app.db import get_db

USERS = [
    (1, "Ada", "ada@example.com"),
    (2, "Priya", "priya@example.com"),
    (3, "Grace", "grace@example.com"),
]
WORKSPACES = [(1, "Engineering"), (2, "Marketing")]
# Grace is deliberately in no workspace, for the empty-state check in Lab 3.
MEMBERSHIPS = [(1, 1, "admin"), (1, 2, "member"), (2, 1, "member")]


def table_exists(db, name):
    row = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)
    ).fetchone()
    return row is not None


def main():
    app = create_app()
    with app.app_context():
        db = get_db()
        db.executemany("INSERT OR IGNORE INTO user (id, name, email) VALUES (?, ?, ?)", USERS)
        db.commit()
        print("Users: Ada (1), Priya (2), Grace (3)")

        if not (table_exists(db, "workspace") and table_exists(db, "workspace_member")):
            print("No workspace tables yet, so workspaces were skipped.")
            print("That's expected before Unit 1. Run this again once it lands.")
            return

        try:
            db.executemany("INSERT OR IGNORE INTO workspace (id, name) VALUES (?, ?)", WORKSPACES)
            db.executemany(
                "INSERT INTO workspace_member (workspace_id, user_id, role)"
                " SELECT ?, ?, ? WHERE NOT EXISTS ("
                "  SELECT 1 FROM workspace_member WHERE workspace_id = ? AND user_id = ?)",
                [(w, u, r, w, u) for w, u, r in MEMBERSHIPS],
            )
        except sqlite3.OperationalError as e:
            db.rollback()
            raise SystemExit(
                f"Couldn't seed workspaces: {e}\n"
                "The workspace tables don't match the names this script expects "
                "(see the top of seed_demo.py)."
            )
        db.commit()
        print("Workspaces: Engineering (1), Marketing (2)")
        print("Members: Ada admin of Engineering, Priya member of Engineering,"
              " Ada member of Marketing. Grace is in no workspace.")


if __name__ == "__main__":
    main()
