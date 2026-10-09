# Unit 1 Reference Decomposition — Workspaces & Roles

Updated copy of Unit 1 from `my-decomposition.md` (v1). Everything else is
unchanged from v1. What changed:

- **Existing database.** Students create `taskboard.db` in Lab 1 step 0 by
  running `seed_demo.py`. Adding `workspace_id` to the
  `CREATE TABLE IF NOT EXISTS task` statement does nothing on a database
  that already exists, so Unit 1 also has to add the column to it. Added to
  the description, one new acceptance criterion, and the verify step.
- **`seed_demo.py`.** The Lab 1 handout requires the schema unit to use the
  names `seed_demo.py` expects and to run it cleanly. That is now part of
  the new criterion and the verify step.

---

## Unit 1 — Workspace and membership schema

**Description:** Add the data model that everything else depends on. In
`app/db.py`, add a `workspace` table (`id`, `name`) and a
`workspace_member` join table (`workspace_id`, `user_id`, `role`, where
`role` is `admin` or `member`), following the existing style — plain
`sqlite3`, schema in the `SCHEMA` string, accessor functions below it, no
ORM. Add a nullable `workspace_id` column to the existing `task` table so
current rows don't break. `taskboard.db` already exists, so `init_db()`
must also add the column to existing databases: if `task` has no
`workspace_id` column, run `ALTER TABLE task ADD COLUMN workspace_id
INTEGER`. Add accessor functions: `create_workspace(name)`,
`add_member(workspace_id, user_id, role)`,
`list_workspaces_for_user(user_id)`, `get_member_role(workspace_id,
user_id)`.

**Acceptance criteria:**
- `SCHEMA` defines `workspace` and `workspace_member`, and `task` gains a
  nullable `workspace_id` column.
- All four existing tests in `tests/test_tasks.py` still pass unmodified.
- `create_workspace`, `add_member`, `list_workspaces_for_user`, and
  `get_member_role` all exist and behave as named (e.g.
  `get_member_role` returns `None` for a non-member rather than raising).
- A new `tests/test_workspaces.py` covers: creating a workspace, adding a
  member with a role, listing workspaces for a user who belongs to
  several, and confirming a non-member gets no role back.
- No changes to `app/routes.py` or templates in this unit — scope stays in
  `app/db.py` and its test file.
- Against the existing `taskboard.db` (without deleting it), existing tasks
  are kept, `task` has a `workspace_id` column, and `python seed_demo.py`
  runs cleanly and reports the Engineering and Marketing workspaces.

**Depends on:** nothing — this is the foundation.
**Blocks:** Units 2, 3, and 4 — none of them can be written against real
tables until this lands.

**Verify:** `python -m unittest discover -s tests -v` — expect the
original 4 tests plus the new workspace tests, all green. Then, against the
existing database:

```
python seed_demo.py
python -c "import sqlite3; print([r[1] for r in sqlite3.connect('taskboard.db').execute('PRAGMA table_info(task)')])"
```

`seed_demo.py` should report the Engineering and Marketing workspaces, and
the column list should end with `workspace_id`.
