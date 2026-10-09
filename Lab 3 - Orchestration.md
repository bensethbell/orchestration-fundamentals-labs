# Lab 3: Orchestrating Parallel Agent Sessions

**Module:** Orchestrating Multiple Agent Sessions
**Time:** 60 minutes
**Codebase:** `taskboard/`
**Goal:** Take the decomposition from Lab 1 and actually run multiple Claude Code sessions in parallel using git worktrees,
then reconcile and merge their output.

This is the payoff lab — everything in Modules 1 and 2 was setup for this.

**Where to run things.** The git repo is `orchestration-fundamentals-labs/`
and the app is in its `taskboard/` folder. Run commands from
`orchestration-fundamentals-labs/taskboard/` (where you've been working
since Lab 1) unless a step says otherwise. A worktree is a full copy of
the repo, so inside each worktree session the app is in that worktree's
own `taskboard/` folder.

---

## 0. Land the foundation first, sequentially (10 min)

Worktrees let you run agents on **separate, non-overlapping work** at the
same time. They do not help with work that has to happen in order. Your
schema/migration unit (Unit 1 from Lab 1) is a hard dependency for
everything else, so it goes first, on `main`, with no parallelism:

1. Start from a clean `main`. Your Lab 2 work stays on its own `lab2-*`
   branches:
   ```
   git switch main
   git status
   ```
   `git status` should show nothing to commit. Then build the schema unit:
   ```
   claude
   > Implement the workspace/membership schema unit from FEATURE_REQUEST.md:
   > [paste your Lab 1 spec for this unit, acceptance criteria included]
   ```
2. Verify it yourself — don't just trust the model's summary:
   ```
   python -m unittest discover -s tests -v
   ```
   All tests (old and new) should pass. Then load the demo workspaces:
   ```
   python seed_demo.py
   ```
   It should report the Engineering and Marketing workspaces. If it says
   the tables don't match, the schema doesn't use the names from Lab 1.
   Fix the schema, not the script. Finally, confirm your existing
   `taskboard.db` really gained the new column:
   ```
   python -c "import sqlite3; print([r[1] for r in sqlite3.connect('taskboard.db').execute('PRAGMA table_info(task)')])"
   ```
   The list should end with `workspace_id`. If it doesn't, the unit only
   changed `CREATE TABLE IF NOT EXISTS`, which never alters a table that
   already exists. Tests and `seed_demo.py` still pass in that case, but
   creating a task in a workspace fails later in the demo. Fix the unit so
   it adds the column to existing databases.
3. Commit it to `main`:
   ```
   git add -A && git commit -m "Add workspace and membership schema"
   ```

Everything below assumes this step is done and committed. If your group is
running behind, the facilitator has a pre-built version of this commit
available — ask for it rather than let it block the rest of the lab.

---

## 1. Set up worktrees for the independent units (10 min)

From your Lab 1 decomposition, you should have at least two or three units
that don't touch the same files and don't depend on each other. For the
TaskBoard feature, that's typically:

- **Unit A — API & permission enforcement** (mainly `app/routes.py`,
  `app/db.py` additions for role checks)
- **Unit B — Frontend workspace switcher** (mainly
  `app/templates/index.html`, plus a small new route to list a user's
  workspaces for the UI)
- **Unit C — Assignment notifications** (a new small module, e.g.
  `app/notifications.py`, plus a hook where `owner_id` gets set)

Create one worktree per unit. **Each `claude --worktree` command opens a
full interactive session and takes over your terminal — it will not hand
control back until you exit it.** Open three separate terminal tabs or
windows first, then run one command in each (don't paste all three into
one terminal expecting them to queue up — only the first will run):

Tab 1:
```
claude --worktree unit-a-api
```
Tab 2:
```
claude --worktree unit-b-frontend
```
Tab 3:
```
claude --worktree unit-c-notifications
```

**Alternatives to three tabs, if you're comfortable with the CLI flags**
(per `claude --help` — try one yourself before relying on it live, the
same way the three-tabs approach above was only caught by actually
running it):
- `--bg` / `--background` starts the session in the background and
  returns control immediately, so all three *can* be pasted into one
  terminal one after another without blocking. Pass the unit's spec as
  the trailing prompt so it starts working right away:
  ```
  claude --worktree unit-a-api --bg "Implement the API & permission enforcement unit: ..."
  ```
  Check on them with `claude agents` (lists all background sessions and
  their ids), `claude logs <id>` (peek at output without attaching), and
  `claude attach <id>` (take one over interactively, e.g. to answer a
  permission prompt). `claude rm <id>` removes a finished session and its
  worktree together.
- `--tmux` creates a tmux session for the worktree automatically — a
  native iTerm2 pane if you're on iTerm2, or a real tmux session otherwise
  (`--tmux=classic` to force that):
  ```
  claude --worktree unit-a-api --tmux
  ```
  Still one command per unit, but you get a split-pane layout instead of
  managing tabs by hand. If tmux is new to you, its pane-switching keys
  (`Ctrl-b` then an arrow, by default) are one more thing to juggle
  mid-lab.

Three plain tabs stays the default instruction above because it needs no
extra explanation going into a lab that's already teaching worktrees —
reach for `--bg` or `--tmux` only if you already know them.

Each command opens an isolated session with its own working directory and
branch under `.claude/worktrees/` at the repo root (not inside
`taskboard/`). Confirm you actually have three separate
directories before proceeding, and **note the exact branch name next to
each one** — Claude Code names it `worktree-<name>` (e.g.
`worktree-unit-a-api`), not just `<name>`, so check rather than assume
when you get to the merge step below. Run this from a fourth terminal tab
on `main` (or from inside the Bash tool of any one of the three sessions —
they all see the same repo):

```
git worktree list
```

**Checkpoint:** if two of your "independent" units turn out to want to
touch the same file (for example, both A and B need to add a route to
`app/routes.py`), that's a real signal your Lab 1 decomposition wasn't as
independent as you thought — note it, don't just push through a merge
conflict later. You have two reasonable options: adjust the file boundary
now (e.g., have Unit B's route live in a new `app/workspace_views.py`
instead), or accept the overlap and plan to resolve it by hand at merge
time.

---

## 2. Launch the three sessions (25 min)

In each worktree session, hand over the corresponding unit spec from your
Lab 1 decomposition — description, acceptance criteria, dependencies,
verification step — the same way you would brief a contractor who can't ask
you follow-up questions mid-task. Example for Unit A:

```
> Implement the API & permission enforcement unit:
> [paste your spec]
> The app is in the taskboard/ folder; run tests from there.
> The workspace/membership schema already exists on main (see
> taskboard/app/db.py). Do not modify the schema. Add tests in
> taskboard/tests/test_workspace_permissions.py.
```

Include the "app is in the taskboard/ folder" line in all three briefs:
the worktree session starts at the repo root, so without it the agent may
look for `app/` in the wrong place.

If you're using custom subagents rather than three top-level sessions,
apply least-privilege tool scoping per agent — a research/investigation
agent shouldn't have `Write`/`Edit` at all, and each implementation agent
should only need `Read`, `Edit`, `Write`, `Bash` for its own file scope:

```yaml
---
name: api-permissions-agent
description: Implements workspace-scoped API permission checks
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
---
```

While the three sessions work, do not sit idle — this is a good moment to:
- Re-read each unit's acceptance criteria so you know what "done" looks
  like before the agent tells you it's done.
- Draft the merge order you'll use in step 3. Hint: the API/permissions
  unit and the notifications unit both edit `create_task`/`update_task`
  in `app/db.py` — that's a structural overlap, not avoidable by better
  file boundaries, since notifications hook the exact function
  permissions-scoping also touches. Merge the frontend and notifications
  units first (no overlap with each other), and save the API/permissions
  unit for last — that's where the one real conflict will be.

As each session finishes, verify it **inside its own worktree**, before
merging anything. Tests only run from the `taskboard/` folder, so in the
worktree run:
```
cd taskboard
python -m unittest discover -s tests -v
```

---

## 2b. Optional: add an orchestrator agent (15 min, only if you have time)

Skip this if your three sessions are still running at the end of step 2. It
is extra, and step 3 does not depend on it.

Up to now you have been the orchestrator: you briefed three agents, checked
their output, and you are about to choose a merge order. In this step you
hand the *checking* part to a fourth agent. You keep the decisions.

1. On `main` (not inside a worktree), create
   `taskboard/.claude/agents/integration-reviewer.md`. Write the frontmatter and
   prompt yourself. Your agent must:
   - be **read-only**: no `Edit` or `Write` in its `tools` list. It reports,
     and you merge.
   - know each unit's expected file scope (copy this from your Lab 1
     decomposition).
   - for each `worktree-*` branch: list the files it changed compared with
     `main`, flag any file outside that unit's scope, and run the test suite
     from the `taskboard/` folder of that unit's worktree.
   - name any function that more than one branch changed.
   - finish with a recommended merge order and what to check after each
     merge, and then stop.

   Choose its `model` the way you did in Lab 2, and be ready to say why.

2. Open a fourth terminal tab in `taskboard/` on `main`, start a new
   `claude` session (subagents are loaded when a session starts), and run:
   ```
   > Use the integration-reviewer agent to review the three worktree units.
   ```

3. Compare its report with what you worked out yourself in step 2:
   - Did it find the `create_task` / `update_task` overlap in `app/db.py`?
   - Is its merge order the same as yours? If not, which order is right, and
     why?
   - Did it flag any out-of-scope file that you missed, or flag one that
     was actually fine?
   - Did it keep to read-only? Look at `git status` in each worktree
     afterwards.

**Extension, if you still have time:** when a unit fails its tests, have
the orchestrator write a short fix brief (the failing test, the likely
cause, and the file it belongs in). Paste that brief into the unit's own
worktree session yourself. Don't give the orchestrator write access to fix
the problem directly. Think about why that line matters before you cross it
in your real work.

---

## 3. Reconcile and merge (15 min)

Merge one unit at a time, verifying between each merge rather than merging
all three and debugging the pile-up at once.

1. From `main` (use the branch name you noted from `git worktree list` in
   step 1 — it's `worktree-unit-b-frontend`, not `unit-b-frontend`,
   unless you renamed it). Start with the frontend and notifications
   units — neither overlaps the other, so expect a clean merge:
   ```
   git merge worktree-unit-b-frontend --no-ff
   python -m unittest discover -s tests -v
   ```
   ```
   git merge worktree-unit-c-notifications --no-ff
   python -m unittest discover -s tests -v
   ```
2. Now the API/permissions unit, which shares `app/db.py`'s `create_task`
   with the notifications unit (already merged) — for different reasons,
   each editing a different part of the function:
   ```
   git merge worktree-unit-a-api --no-ff
   ```
   **This may or may not actually show a conflict** — git only conflicts
   on overlapping *lines*, not overlapping functions, so if the two units'
   changes land on different lines (e.g. one at the signature/`INSERT`,
   the other at the return/notify block) it can merge cleanly with no
   conflict markers at all. Either way, open `app/db.py` afterward and
   confirm the merged `create_task` has **both** changes — the new
   parameter the permissions unit added *and* the notification call the
   other unit added. A clean auto-merge is a textual interleave, not a
   correctness guarantee; check it rather than assume it. This is expected here, not a
   sign the decomposition failed; it's the one genuinely structural
   overlap (notifications has to hook the same function permissions-
   scoping touches). For any *other* conflict you didn't expect, that's
   when to ask: is this real, or did a unit quietly touch something
   outside its stated scope? Check the diff (`git diff main~1`) before
   assuming it's a normal merge conflict.
   ```
   python -m unittest discover -s tests -v
   ```
3. **After every merge, confirm `main` actually moved to where you think
   it did — don't just eyeball `git log --graph`.** A `--graph` listing
   with `--all` shows every branch at once and is easy to misread. Run
   `git rev-parse main` and check it against the commit you just merged.
   Skipping this is exactly how a merge can be silently missed — the next
   merge proceeds on a stale base, and nothing looks wrong until a test
   count comes back lower than expected.
4. After all three are merged, run the full suite once more, then do the
   actual demo walkthrough below — passing unit tests is not the same as
   confirming the feature works for a real user.

### Demo it

**The demo data comes from `seed_demo.py`**, which you've already run in
Lab 1 and in step 0 above: users Ada (id 1), Priya (id 2) and Grace (id 3),
workspaces Engineering (id 1) and Marketing (id 2), with Ada an admin of
Engineering and a member of Marketing, and Priya a member of Engineering.
Grace is deliberately in no workspace, for the empty-state check below.
Run it once more to be sure everything is there (it only adds missing rows
and never deletes anything), then start the server on port 5001:
```
python seed_demo.py
python run.py
```
The steps below assume the task you create in step 2 gets id 1. If you
created tasks earlier while testing, use the `id` that step 2 returns
instead.

**There is no "Create Task" button or form anywhere on the page — there
never has been, not before this feature and not after.** The browser is
only for logging in, switching workspaces, and viewing the task list.
Every creation, update, reassignment, and deletion happens through the
API — curl below, or any HTTP client. This was true of the original
TaskBoard app too (its own README creates the first task via curl, not a
form); none of Units 1–4 were ever asked to add a creation form, so don't
look for one.

Do these seven steps in order. Each one has three parts: what it's
testing, the exact command to run, and what the result should be. The
command is always the line starting with `curl` — nothing else in these
steps is something you type.

**Step 1 — view the page as Ada.**
Open `http://localhost:5001/login/1` in your browser, then
`http://localhost:5001/`.
Expected: a workspace switcher, and Engineering's tasks (empty so far).

**Step 2 — Ada creates a task with no owner specified.**
Run (this is one single line — if it wraps visually that's fine, don't
add any line breaks of your own):
```
curl -X POST "http://localhost:5001/api/tasks?workspace_id=1" -H "Content-Type: application/json" -H "X-User-Id: 1" -d '{"title": "Ship the feature"}'
```
Expected: the response JSON has `"owner": "Ada"` (it defaulted to her
automatically). Separately, check the terminal where `python run.py` is
running (not the terminal where you ran curl) — it should print a new
line containing `Notifying ada@example.com: ...`.

**Step 3 — confirm the task is scoped to Engineering, not visible in Marketing.**
In your browser, go to `http://localhost:5001/?workspace_id=2`.
Expected: "Ship the feature" is not listed there.

**Step 4 — view the page as Grace, who has no workspace.**
Open `http://localhost:5001/login/3`, then `http://localhost:5001/`.
Expected: an empty-state message like "you're not in a workspace yet" —
not an error page.

**Step 5 — confirm Grace is blocked from Engineering's data at the API level too.**
Run:
```
curl -i "http://localhost:5001/api/tasks?workspace_id=1" -H "X-User-Id: 3"
```
Expected: `403`, and no task data in the response body.

**Step 6 — Ada reassigns the task to Priya, a real Engineering member.**
Run (one single line):
```
curl -X PATCH "http://localhost:5001/api/tasks/1?workspace_id=1" -H "Content-Type: application/json" -H "X-User-Id: 1" -d '{"owner_id": 2}'
```
Expected: the response JSON now has `"owner": "Priya"`. Check the
server's terminal again — a second line, `Notifying priya@example.com:
...`, should now be there too.

**Step 7 — Ada tries to reassign the same task to Grace instead.**
Run (one single line):
```
curl -i -X PATCH "http://localhost:5001/api/tasks/1?workspace_id=1" -H "Content-Type: application/json" -H "X-User-Id: 1" -d '{"owner_id": 3}'
```
Expected: `400`, rejected. This is correct behavior, not a bug — Grace
isn't a member of Engineering, so she can't be assigned a task there.

**Step 8 — Priya (a member, not an admin) tries to delete the task.**
Run:
```
curl -i -X DELETE "http://localhost:5001/api/tasks/1?workspace_id=1" -H "X-User-Id: 2"
```
Expected: `403`.

**Step 9 — Ada (the admin) deletes it.**
Run:
```
curl -i -X DELETE "http://localhost:5001/api/tasks/1?workspace_id=1" -H "X-User-Id: 1"
```
Expected: `204`.

If every "Expected" above matched what you actually saw, that's the
actual done state — not just a green test suite.

### Merge/review checklist

- [ ] Each unit was verified independently in its own worktree before
      merging into `main`.
- [ ] Merges happened one at a time, not all at once.
- [ ] Each merge was confirmed with `git rev-parse main`, not just a
      glance at `git log --graph` — a misread graph can make it look like
      a merge landed when it didn't.
- [ ] No unit silently touched a file outside its stated scope — if one
      did, that's worth a note for next time you decompose a feature.
- [ ] The full test suite passes after all merges.
- [ ] You manually exercised the feature end to end, not just via unit
      tests.
- [ ] Any open questions from Lab 1 that turned out to matter during
      implementation are written down, with how you actually resolved them.

### Clean up

The worktrees live at the repo root, so run this from
`orchestration-fundamentals-labs/`, one level up from `taskboard/`:

```
cd ..
git worktree list
git worktree remove .claude/worktrees/unit-a-api
git worktree remove .claude/worktrees/unit-b-frontend
git worktree remove .claude/worktrees/unit-c-notifications
```

---

## Done state

`main` has workspaces, roles, permission enforcement, a frontend switcher,
and assignment notifications, all merged and passing tests, built by three
agent sessions that ran at the same time instead of one session working
through the list serially. Be ready to talk for two minutes about where
your decomposition held up under real implementation and where it didn't —
that gap is the actual lesson of today, more than the final code is.
