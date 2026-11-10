# Task Decomposition - Taskboard (reference)

A complete reference decomposition for Labs 4a and 4b. If you finished
your own in Lab 1, you may copy yours over this file instead.


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


## Unit 2 — API & permission enforcement
(depends on Unit 1; independent
of Units 3 and 4)
- All task endpoints take/require a workspace context and filter by it.
- `role == "member"` can create tasks and edit tasks they own; only `role
  == "admin"` can delete tasks or manage membership.
- The current user comes from `identity.get_current_user_id()` (already in
  the app). No identified user → 401.
- Requests for a workspace the user doesn't belong to return 403, with no
  task data in the body.
- A task created without `owner_id` is owned by its creator. Assigning a
  task to someone who isn't a member of its workspace → 400.
- Acceptance: `tests/test_workspace_permissions.py` covers an admin action,
  a blocked member action, and a blocked cross-workspace request.
- Verify: unit tests + a manual curl walkthrough of the three cases above.

## Unit 3 — Frontend workspace switcher
(depends on Unit 1's schema
existing but not on Unit 2's enforcement; independent of Units 2 and 4)
- New route (e.g. `GET /api/my-workspaces`) listing the current user's
  workspaces.
- `index.html` gets a simple switcher (a dropdown or list of links) and
  only renders tasks for the selected workspace. The page's user is
  `identity.get_current_user_id()` (set by visiting `/login/<user_id>`), and
  the selected workspace is `?workspace_id=`, the same parameter the API uses.
- File overlap: shares `app/routes.py` with Unit 2. Keep to `index()` and the
  new route so the two don't collide.
- Acceptance: switching workspaces changes the visible task list; a user
  in zero workspaces sees an empty state, not an error.
- Verify: manual browser check; no new backend logic beyond the one route,
  so heavy testing isn't the point here — visual correctness is.

## Unit 4 — Assignment notifications
(depends on Unit 1's schema existing;
independent of Units 2 and 3)
- Add `app/notifications.py` with `notify(user, task)` that logs (doesn't
  send real email) a message like `"Notifying {user.email}: assigned to
  {task.title}"`.
- Log at INFO level on a module logger; `run.py` already prints INFO lines.
- Hook it into the code path where `owner_id` is set or changed on a task
  (in `update_task` and task creation with an owner).
- File overlap: shares `app/db.py` with Unit 2. Touch only `create_task` and
  `update_task` there.
- Acceptance: `tests/test_notifications.py` confirms `notify` is called
  (or the log line appears) when ownership changes, and is not called when
  it doesn't.
- Verify: unit test + manual check of log output.

## Dependency graph

```
Unit 1 (schema)
   |
   +--> Unit 2 (API & permissions)     \
   +--> Unit 3 (frontend switcher)      >  independent of each other
   +--> Unit 4 (notifications)         /
```

Unit 1 is strictly sequential. Units 2, 3, and 4 have no file overlap
(routes/permissions logic vs. template/one new route vs. a new standalone
module) and no dependency on each other — that's the set to hand to three
parallel worktrees in Lab 3.

## Open questions worth surfacing (and a reasonable resolution for each)

- **What happens to a task when its owner is removed from the workspace?**
  Reasonable default: the task's `owner_id` is cleared (set to null) rather
  than the task being deleted or the removal being blocked.
- **Can a user with zero workspaces still use the app?** Reasonable
  default: yes, they see an empty state prompting them to be invited to a
  workspace, rather than an error page.
