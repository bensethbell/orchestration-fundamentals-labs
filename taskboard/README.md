# TaskBoard

A deliberately small task-tracking app used as the shared practice codebase
for the "Orchestration Fundamentals for Agentic Development" course.

## What it does

A single-workspace task board: users, tasks, and a simple status field
(`todo` / `in_progress` / `done`). A minimal HTML page lists tasks; a small
JSON API backs it.

## Project layout

```
app/
  __init__.py     Flask app factory
  db.py           SQLite access layer (no ORM, plain sqlite3) and schema
  routes.py       HTTP routes (page + JSON API)
  templates/      Jinja templates
tests/
  test_tasks.py   unittest-based API tests
run.py            Local dev server entrypoint
seed_demo.py      Loads the demo users (and, once they exist, workspaces)
FEATURE_REQUEST.md   The feature you'll be decomposing and building today
```

## Setup

```
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Demo data

```
python seed_demo.py
```

Adds the demo users Ada (1), Priya (2) and Grace (3). Once the workspace
schema from today's feature exists, running it again also adds the
Engineering and Marketing workspaces and their members. It's safe to run
repeatedly and never deletes anything. Don't modify it: the feature is
built around the table names it expects.

## Running it

```
python run.py
```

Visit http://localhost:5001 — the task list is empty until you create tasks
through the API:

```
curl -X POST http://localhost:5001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Try out TaskBoard"}'
```

## Running the tests

```
python -m unittest discover -s tests -v
```

All four tests should pass before you start today's exercises. If they
don't, flag it during the environment check at the start of class rather
than partway through a lab.

## Today's exercise

See `FEATURE_REQUEST.md` for the feature you'll be decomposing, building,
and orchestrating across today's three modules.
