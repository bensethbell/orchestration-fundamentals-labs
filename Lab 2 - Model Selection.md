# Lab 2: Matching Models and Effort Levels to Tasks

**Module:** Model Selection Strategy for Agentic Development
**Time:** 30 minutes
**Codebase:** `taskboard/`
**Goal:** Practice choosing a model and effort level based on a task's
complexity, risk, and cost — then verify your choice against what actually
happens when you run it.

---

## 0. Quick reference (keep this open)

| Model | Best for | Watch out for |
|---|---|---|
| **Haiku** | Small, well-specified, low-risk tasks; fast iteration | Underspecified or ambiguous work — it will guess rather than investigate |
| **Sonnet** | The default for most day-to-day implementation work | — |
| **Opus** | Architecture decisions, anything touching shared/foundational code, higher-risk changes | Cost/latency if overused on trivial tasks |
| **Fable** | Long, ambiguous, or investigative work where the model should explore before acting | Not available on every plan — check before you plan around it |

**Effort level** (`low` / `medium` / `high` / `xhigh` / `max`) is a separate
dial from model choice — it controls how much the model reasons/verifies
before answering, independent of which model you picked. A cheap model at
high effort and a strong model at low effort are both valid choices
depending on the task.

Switching commands:
```
/model            # opens picker
/model opus       # switch directly
/model sonnet
/model haiku
```
Press `s` in the picker to apply for the current session only, without
changing your default.

To set the effort level, start the session with it:
```
claude --effort high
```

---

## 1. Assign a model + effort level to each task (5 min)

Below are three tasks against the TaskBoard codebase. For each, write down
(a) which model you'd use, (b) which effort level, and (c) one sentence on
why — specifically referencing complexity, risk, or cost, not just "this
one seems hard."

**Task A — Health check endpoint.**
Add a `GET /health` route that returns `{"status": "ok"}` with a 200. No
database access, no auth, one route.

**Task B — Input validation on task creation.**
`POST /api/tasks` currently trusts `data["title"]` to exist and be
reasonable. Add validation: reject empty/whitespace-only titles, cap title
length at 200 characters, return a 400 with a clear error message on
failure, and add tests covering both the rejection and success paths.

**Task C — Backward-compatibility investigation.**
Before building the workspace-scoped API, figure out: what should happen to
the existing single-workspace behavior for users who existed before
workspaces did? Should they get auto-enrolled into a default workspace?
Should old, workspace-less tasks stay visible to everyone? There's no single
correct answer here — the deliverable is a short written recommendation
with tradeoffs, not code.

Write your three answers before moving on — don't peek at the discussion
questions in section 3 yet.

---

## 2. Run at least two of them for real (20 min)

Pick at least two tasks from above — ideally one you rated low-risk and one
you rated high-risk or ambiguous — and actually run them against the
`taskboard` repo using the model/effort you chose.

**Run each task on its own branch.** Lab 3 starts from a clean `main`, so
keep Lab 2's changes off it. Before you start a task:

```
git switch main
git switch -c lab2-task-a
```

Run the task in Claude Code and record your notes. Then commit whatever it
changed to that branch and go back to `main`:

```
git add -A
git commit -m "Lab 2: Task A"
git switch main
```

Use a new branch for each task you run (`lab2-task-b`, `lab2-task-c`).
Don't skip the commit: uncommitted changes follow you when you switch
branches, so they would end up back on `main`. If a task changed no files
(Task C's deliverable is a written recommendation), there is nothing to
commit; just switch back.

For each one you run, record:

- **Wall-clock time** from prompt to a result you'd consider done.
- **What you had to correct or clarify**, if anything, after the first pass.
- **Whether the model asked you anything** or just proceeded — and whether
  that was the right call for this task.
- **Your gut read on whether the model/effort choice was right**, in
  hindsight. Would you downgrade it to save cost, or upgrade it because it
  struggled?

If time allows, run **Task B** twice, each on its own branch from `main`
(`lab2-task-b-haiku`, `lab2-task-b-sonnet`): once on Haiku at `high`
effort and once on Sonnet at `medium`. Then compare the two results
directly. This is the clearest way to see the model-versus-effort tradeoff
in the room rather than just hearing about it. Look specifically at:
whether each one handled the edge cases (whitespace-only titles, a title of
exactly 200 characters), whether it wrote tests for both the rejection and
success paths without being asked twice, and how long each took.

---

## 3. Discussion (5 min, group)

- For Task A, did anyone use something stronger than Haiku? What made you
  decide that, and in hindsight was it worth it?
- For Task C, how did the model handle being asked for a recommendation
  rather than code? Did it hedge, pick a side, or ask clarifying questions?
- Would anyone change their Task B assignment after actually running it?
  If you did the Haiku-versus-Sonnet comparison, did the cheaper model at
  higher effort hold up, or did it miss something?

---

## Done state

You should have a filled-in table of model/effort assignments for all three
tasks, actual run results (with notes) for at least two of them, and a
point of view — not just a guess — on where Haiku stops being enough and
where Opus/Fable is worth the extra cost for this specific codebase. You
should also be back on a clean `main`, with each task's changes on its own
`lab2-*` branch: run `git switch main` and check that `git status` shows
nothing to commit. Lab 3 builds on `main`.
