# Lab 1: Decomposing a Feature Into Agent-Ready Units of Work

**Module:** Decomposing Complex Features for Multi-Agent Execution
**Time:** 35 minutes
**Codebase:** `taskboard/` (see `README.md` and `FEATURE_REQUEST.md` in the repo)
**Goal:** Turn the Workspaces & Roles feature request into a set of units of
work that (a) an agent could execute mostly unsupervised, and (b) you could
verify without re-reading every line of the diff.

---

## 0. Before you start (5 min)

1. Confirm you can run the existing test suite and have it pass:
   ```
   python -m unittest discover -s tests -v
   ```
   You should see 4 passing tests. If you don't, raise your hand now — don't
   carry a broken environment into the rest of the day.
2. Open and actually read `FEATURE_REQUEST.md` in the repo. Don't skim it —
   the ambiguities in it are intentional and you'll need to notice them.
3. Skim `app/db.py`, `app/routes.py`, and `app/templates/index.html` so you
   know roughly where things live. You don't need to understand every line.
4. Load the demo data:
   ```
   python seed_demo.py
   ```
   This adds three users: Ada (id 1), Priya (id 2) and Grace (id 3). It will
   also say there are no workspace tables yet. That's expected, because the
   workspace tables are part of the feature you're about to decompose. Read
   the next section before you start decomposing.

### Build around `seed_demo.py`

The repo already includes a demo-data script, `seed_demo.py`. Once the
workspace tables exist, running it again adds the Engineering (id 1) and
Marketing (id 2) workspaces, makes Ada an admin of Engineering and a member
of Marketing, makes Priya a member of Engineering, and leaves Grace out of
every workspace. Lab 3's demo depends on exactly this data, so treat the
script as a fixed part of the codebase:

- **Use its table and column names in your schema unit:**
  `workspace (id, name)` and `workspace_member (workspace_id, user_id, role)`,
  with `role` either `'admin'` or `'member'`. These are the same names as the
  worked example below.
- **Give your schema unit an acceptance criterion for it:** against the
  `taskboard.db` you already have (don't delete it), `python seed_demo.py`
  runs without errors and reports both workspaces.
- **Your schema unit has to work with that existing database.** Running
  `seed_demo.py` just now created `taskboard.db` with the original `task`
  table, and `CREATE TABLE IF NOT EXISTS` never changes a table that already
  exists. Any new `task` column has to be added to the existing database
  too, or it will be missing when Lab 3's demo needs it.
- **No unit should modify `seed_demo.py`.** If a unit seems to need different
  demo data, write that down as an open question instead.

---

## 1. What makes a unit of work "agent-ready"? (covered in the lecture — skim it as a reference)

A unit of work is agent-ready when it has all four of these:

- **Bounded scope.** It touches a small, identifiable set of files and does
  one coherent thing — not "build the backend," but "add a `workspace` table
  and a `workspace_member` join table, with a migration that runs against
  the existing `taskboard.db`."
- **A clear definition of done (acceptance criteria).** Something you could
  check mechanically or with a quick read, not "make it work well."
- **Named dependencies.** What must already exist before this unit can
  start, and what it blocks.
- **A verification step.** How you (not the agent) will confirm it's
  actually done — a test to run, an endpoint to curl, a page to look at.

A task that fails any of these isn't wrong to delegate, but it's higher risk
— you should expect to review more carefully, or split it further.

### Worked example — bad unit of work

> "Add workspaces to the app."

Why it's bad: unbounded scope (touches schema, routes, templates, and
permissions all at once), no acceptance criteria, no stated dependencies,
no way to verify partial progress. An agent given this will make a pile of
plausible-looking decisions you now have to review as one giant diff.

### Worked example — good unit of work

> **Unit: Workspace and membership schema**
> Add a `workspace` table (`id`, `name`) and a `workspace_member` table
> (`workspace_id`, `user_id`, `role` — either `admin` or `member`) to
> `app/db.py`, following the existing style (plain `sqlite3`, schema defined
> in the `SCHEMA` string, accessor functions below it — no ORM). Add a
> `workspace_id` column to the existing `task` table (nullable for now, so
> existing rows don't break). Because `taskboard.db` already exists,
> `init_db()` must also add that column to existing databases: if `task` has
> no `workspace_id` column, run
> `ALTER TABLE task ADD COLUMN workspace_id INTEGER`.
>
> **Acceptance criteria:**
> - `SCHEMA` includes both new tables and the altered `task` table.
> - Existing tests in `tests/test_tasks.py` still pass unmodified.
> - New accessor functions exist: `create_workspace(name)`,
>   `add_member(workspace_id, user_id, role)`, `list_workspaces_for_user(user_id)`,
>   `get_member_role(workspace_id, user_id)` (returns `None` for a
>   non-member; the permissions unit uses it to check roles).
> - A short new test file `tests/test_workspaces.py` covers creating a
>   workspace, adding a member, and listing workspaces for a user.
> - Against the existing `taskboard.db` (without deleting it), existing
>   tasks are kept, `task` has a `workspace_id` column, and
>   `python seed_demo.py` runs cleanly and reports the Engineering and
>   Marketing workspaces.
>
> **Depends on:** nothing (this is the foundation).
> **Blocks:** the API/permissions unit, the frontend switcher unit, and the
> notification unit all assume this schema exists.

Notice what's different: an agent working from the second version can
self-check against the acceptance criteria before handing it back to you,
and you can verify it in under two minutes by running the test file.

---

## 2. Decompose the feature yourself (20 min)

Working alone or in pairs, produce a written decomposition of
`FEATURE_REQUEST.md` in the style of the "good" example above. At minimum,
identify:

1. **The units of work.** Aim for 4: one foundation unit that everything
   else depends on, plus three independent units you'll run in parallel
   worktrees in Lab 3. As a hint (not an answer key — you should reason to
   this yourself first): the feature has a schema piece, an
   API/permissions-enforcement piece, a frontend workspace-switcher piece,
   and a notification piece. If one of those feels too big, break it into
   steps inside that unit rather than adding more units.
2. **For each unit:** a one-paragraph description, 3-5 acceptance criteria,
   explicit dependencies (what must be done first), and how you'd verify it.
3. **A dependency graph or ordered list** showing what can run in parallel
   and what can't. You should be able to say out loud: "these three units
   have no file overlap and no dependency on each other, so they could run
   as separate agent sessions at the same time."
4. **At least two open questions** the feature request left ambiguous (for
   example: what happens to a task when its owner is removed from the
   workspace? Can a user with zero workspaces still use the app?). Write
   down how you'd resolve each one — don't just flag it and move on.

Write this in a scratch file (`my-decomposition.md` is fine, it's not
graded) or on paper — you'll use it directly in Lab 3, so keep it somewhere
you can find again.

### If you get stuck

- Re-read the "Constraints and notes" section at the bottom of
  `FEATURE_REQUEST.md` — it's telling you the shape of the dependency graph.
- Ask: "if I handed this exact paragraph to a capable developer and left
  the room for an hour, would they come back with something I could
  actually review, or would they come back with questions?" If the latter,
  the unit is underspecified.
- If you're genuinely stuck past the 20-minute mark, the facilitator has a
  reference decomposition available — ask for a hint rather than a full
  answer if you want to keep working it out yourself.

---

## 3. Pair-share and self-check (10 min)

Trade decompositions with a neighbor (or review your own against this
checklist if working solo):

- [ ] Could a stranger execute unit 1 without asking you a clarifying
      question? If not, what's missing?
- [ ] Does every unit have acceptance criteria you could check without
      reading the full diff?
- [ ] Is the dependency chain explicit — could you say confidently which
      units block which?
- [ ] Have you named at least two ambiguities the feature request left open,
      with your own resolution for each?
- [ ] Does your schema unit use the table and column names `seed_demo.py`
      expects, with an acceptance criterion that the script runs cleanly?
- [ ] Are there at least two or three units with no file overlap and no
      dependency on each other? (You'll need this for Lab 3.)

If you and your partner decomposed the feature differently, that's fine and
expected — discuss where and why, since there's rarely one right
decomposition, only better- and worse-specified ones.

---

## Done state

You should leave this lab with a written decomposition (units, acceptance
criteria, dependencies, open questions) that you'll hand to Claude Code in
Lab 3 (to run in parallel worktrees). Keep the file somewhere you can find
it — you'll need it again after Lab 2.
