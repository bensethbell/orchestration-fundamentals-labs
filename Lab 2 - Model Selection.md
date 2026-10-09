# Lab 2: Matching Models and Effort Levels to Tasks

**Module:** Model Selection Strategy for Agentic Development
**Time:** 35 minutes
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

---

## 1. Assign a model + effort level to each task (10 min)

Below are four tasks against the TaskBoard codebase. For each, write down
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

**Task C — Workspace and membership schema migration.**
The foundational schema change from Lab 1: new `workspace` and
`workspace_member` tables, plus an added (nullable) `workspace_id` column
on `task`, without breaking any existing data or tests.

**Task D — Backward-compatibility investigation.**
Before building the workspace-scoped API, figure out: what should happen to
the existing single-workspace behavior for users who existed before
workspaces did? Should they get auto-enrolled into a default workspace?
Should old, workspace-less tasks stay visible to everyone? There's no single
correct answer here — the deliverable is a short written recommendation
with tradeoffs, not code.

Write your four answers before moving on — don't peek at the discussion
questions in section 3 yet.

---

## 2. Run at least two of them for real (20 min)

Pick at least two tasks from above — ideally one you rated low-risk and one
you rated high-risk or ambiguous — and actually run them against the
`taskboard` repo using the model/effort you chose.

For each one you run, record:

- **Wall-clock time** from prompt to a result you'd consider done.
- **What you had to correct or clarify**, if anything, after the first pass.
- **Whether the model asked you anything** or just proceeded — and whether
  that was the right call for this task.
- **Your gut read on whether the model/effort choice was right**, in
  hindsight. Would you downgrade it to save cost, or upgrade it because it
  struggled?

If time allows, run **Task C** (the schema migration) twice — once on
Haiku and once on your chosen model (Sonnet or Opus) — and compare the two
results directly. This is the clearest way to see the cost/quality tradeoff
in the room rather than just hearing about it. Look specifically at:
whether it noticed the "must not break existing tests" constraint, whether
it asked about the nullable column decision, and whether it wrote the
matching test file unprompted or you had to ask for it.

---

## 3. Discussion (5 min, group)

- For Task A, did anyone use something stronger than Haiku? What made you
  decide that, and in hindsight was it worth it?
- For Task C, did the model you picked flag the "don't break existing
  tests" constraint on its own, or did it need to be told? What does that
  tell you about how much you can trust a given model/effort combination
  with foundational, high-blast-radius changes?
- For Task D, how did the model handle being asked for a recommendation
  rather than code? Did it hedge, pick a side, or ask clarifying questions?
- Would anyone change their Task B assignment after actually running it?

---

## Done state

You should have a filled-in table of model/effort assignments for all four
tasks, actual run results (with notes) for at least two of them, and a
point of view — not just a guess — on where Haiku stops being enough and
where Opus/Fable is worth the extra cost for this specific codebase. Keep
whatever code Task C produced if you ran it with a strong model — it may be
usable as your team's schema-migration unit going into Lab 3.
