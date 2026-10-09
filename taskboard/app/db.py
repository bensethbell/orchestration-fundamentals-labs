import sqlite3
from datetime import datetime

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'todo',
    created_at TEXT NOT NULL,
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES user (id)
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()
    app.teardown_appcontext(close_db)


def list_tasks():
    rows = get_db().execute(
        """
        SELECT task.*, user.name AS owner_name
        FROM task
        LEFT JOIN user ON user.id = task.owner_id
        ORDER BY task.created_at DESC
        """
    ).fetchall()
    return [row_to_task_dict(r) for r in rows]


def get_task(task_id):
    row = get_db().execute(
        """
        SELECT task.*, user.name AS owner_name
        FROM task
        LEFT JOIN user ON user.id = task.owner_id
        WHERE task.id = ?
        """,
        (task_id,),
    ).fetchone()
    return row_to_task_dict(row) if row else None


def create_task(title, description="", status="todo", owner_id=None):
    db = get_db()
    cur = db.execute(
        "INSERT INTO task (title, description, status, created_at, owner_id) VALUES (?, ?, ?, ?, ?)",
        (title, description, status, datetime.utcnow().isoformat(), owner_id),
    )
    db.commit()
    return get_task(cur.lastrowid)


def update_task(task_id, **fields):
    if not fields:
        return get_task(task_id)
    db = get_db()
    columns = ", ".join(f"{key} = ?" for key in fields)
    values = list(fields.values()) + [task_id]
    db.execute(f"UPDATE task SET {columns} WHERE id = ?", values)
    db.commit()
    return get_task(task_id)


def list_users():
    rows = get_db().execute("SELECT * FROM user").fetchall()
    return [{"id": r["id"], "name": r["name"], "email": r["email"]} for r in rows]


def row_to_task_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "owner": row["owner_name"],
    }
