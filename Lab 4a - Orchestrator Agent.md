# Lab 4a: Let an Orchestrator Agent Run the Workers

**Module:** Orchestrating Multiple Agent Sessions (optional extension)
**Time:** 45 minutes
**Codebase:** a fresh copy of the labs repo at the Lab 3 starting point
**Goal:** Build the same feature as Lab 3 (Units 2–4 on top of the
schema: the API, frontend and notifications units, called Units A, B and C
in Lab 3), but this time a single orchestrator agent does the coordinating
you did by hand in Lab 3. It sends one worker subagent to each unit in its
own worktree, checks their work, and merges it. You stay in charge of the
decisions.

Lab 3, Lab 4a and Lab 4b all produce the same result. Only the way the
agents are coordinated changes:

| | Lab 3 | Lab 4a (this lab) | Lab 4b |
|---|---|---|---|
| Who coordinates | You | An orchestrator agent | A team lead, plus teammates messaging each other |
| How work is isolated | One worktree per session | One worktree per subagent | No isolation: one shared checkout, each file has one owner |
| How it's combined | You merge | The orchestrator merges, after you approve | No merge: everyone edits the same files |

---

## 0. Start from the Lab 3 starting point (5 min)

Make a separate copy so this lab doesn't touch your Lab 3 result. The git
repo is `orchestration-fundamentals-labs/`; the app lives in its
`taskboard/` folder. From the folder that contains
`orchestration-fundamentals-labs/`:

```
git clone orchestration-fundamentals-labs labs-4a
cd labs-4a
git log --oneline
```

Find your workspace/membership schema commit (Unit 1) in the log and reset
to it, replacing `<sha>` with that commit's id. Tests only run from inside
`taskboard/`:

```
git reset --hard <sha>
cd taskboard
python -m unittest discover -s tests -v
cd ..
```

All tests should pass. Then copy your Lab 1 decomposition over
`taskboard/my-decomposition.md` (it replaces the example file already
there). The orchestrator reads its unit specs from that file:

```
cp <path-to-your-lab-1-decomposition> taskboard/my-decomposition.md
git add taskboard/my-decomposition.md
git commit -m "Add decomposition"
```

Commit it so the workers' worktrees include it. Everything else in this
lab runs from the repo root (`labs-4a/`), not from `taskboard/`.

---

## 1. Set up the agents (10 min)

You need three files under `.claude/` at the repo root. Create them on
`main` in `labs-4a`.

**`.claude/settings.json`** makes worktrees branch from your local `HEAD`.
By default Claude Code branches them from the remote's default branch,
which here is your Lab 3 repo's `main`, and that already has Lab 3's
merged code on it. The file also pre-approves running the tests, so three
parallel workers don't flood you with permission prompts:

```json
{
  "worktree": { "baseRef": "head" },
  "permissions": {
    "allow": [
      "Bash(python -m unittest *)",
      "Bash(cd taskboard && python -m unittest *)",
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ]
  }
}
```

**`.claude/agents/unit-builder.md`** is the worker. There is one
definition, and the orchestrator runs it three times, once per unit.
`model: sonnet` is only the default: the orchestrator picks a model and
effort level for each worker when it starts it, the same call you made by
hand in Labs 2 and 3:

```yaml
---
name: unit-builder
description: Implements one unit of the decomposition in its own worktree, then commits it.
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
isolation: worktree
permissionMode: acceptEdits
---
You implement exactly one unit of work, as given in your prompt: its
spec, acceptance criteria and the files you're allowed to touch.

- The app is in the taskboard/ folder of your worktree. File paths in
  your prompt are relative to the repo root (e.g. taskboard/app/routes.py).
- Edit only the files your prompt lists. If you need a change anywhere
  else, stop and say so in your report instead of making it.
- Don't change the schema in taskboard/app/db.py's SCHEMA string.
- Run `cd taskboard && python -m unittest discover -s tests -v` and make
  it pass.
- Commit your work on your current branch with a message naming the unit.

Report: your branch name (`git branch --show-current`), the files you
changed, the test count, and any spec question you had to decide yourself.
```

**`.claude/agents/orchestrator.md`** is the coordinator. Look at its
`tools` line: it can start `unit-builder` agents and nothing else, and it
has no `Edit` or `Write`, so it can't write code itself.

```yaml
---
name: orchestrator
description: Coordinates parallel unit-builder agents and merges their work.
tools: Agent(unit-builder), Read, Grep, Glob, Bash
model: opus
---
You coordinate a feature build. You never write code yourself.

1. Read taskboard/my-decomposition.md and taskboard/FEATURE_REQUEST.md.
   Unit 1 (the schema) is already on main. Plan Units 2-4: for each, the
   spec, acceptance criteria, allowed files (as paths from the repo root),
   and the model (haiku, sonnet or opus) and effort level you'll run its
   worker at, with one sentence on why, based on the unit's complexity
   and risk. Show the plan and wait for the user to approve it.
2. Start three unit-builder agents in parallel, all in one message, one
   per unit, each at the model and effort the user approved. Give each its
   full spec. Tell the frontend and API units to use the same workspace
   query parameter, `?workspace_id=`.
3. When all three report back, check each one yourself. Don't take its
   summary on trust:
   - `git diff --stat main...<branch>`: flag files outside its allowed list.
   - Run the tests inside its worktree, from its taskboard/ folder.
   - Name any function more than one branch changed.
   Show a status table and a proposed merge order, then wait for the
   user's go-ahead.
4. Merge one branch at a time with `git merge --no-ff`. After each merge,
   run the full test suite and check `git rev-parse main`.
5. If a merge conflicts or the tests fail, stop. Show the user the
   conflict or failure and suggest options. Don't resolve it yourself.
```

Commit the agent files, then start the orchestrator as your main session,
from the repo root (`labs-4a/`). Start it from a terminal where your
Python venv is active, so the workers can run the tests:

```
git add .claude
git commit -m "Add orchestrator and unit-builder agents"
claude --agent orchestrator
```

The startup header should show `@orchestrator`.

---

## 2. Run it (20 min)

```
> Build Units 2-4 from taskboard/my-decomposition.md.
```

There are two checkpoints, and at each one you decide:

1. **The plan.** Before anything runs, read the orchestrator's plan for
   each unit. Are the file scopes right? Did it give the frontend and API
   units the same query parameter? Compare its model and effort picks
   with the ones you used in Lab 3: where it disagrees, whose reasoning
   is better? Correct it now if needed. A bad brief
   costs more here than in Lab 3, because you won't see the work until all
   three workers have finished.
2. **The merge.** Read its status table. Compare its merge order with the
   one you used in Lab 3. Approve it, or tell it a different order.

While the workers run, the panel below the prompt shows the three
`unit-builder` agents. Select one and press Enter to see what it's doing.

If the orchestrator stops at a conflict, that's working as designed. You
resolve it, either yourself or by telling it what to do.

---

## 3. Verify like Lab 3 (10 min)

The orchestrator saying "merged, tests pass" is a claim. Check it:

```
git log --oneline --graph -8
cd taskboard
python -m unittest discover -s tests -v
```

Then run the **Demo it** walkthrough from Lab 3, steps 1 to 9. Several of
the problems it catches only show up when the units are put together:
login route names, which status code non-members get, and whether the
notification log line actually appears in the server terminal. A check
of each branch on its own doesn't catch them.

---

## Debrief

Be ready to answer these:

- Which of your Lab 3 jobs did the orchestrator do well? Which did it get
  wrong, or skip?
- The orchestrator has no `Edit` or `Write`, but it has `Bash`. What
  could it still do that you didn't intend? How would you lock that down?
- Where did you have to step in? Was that at the checkpoints you
  expected?
- The orchestrator and the workers each have their own context window.
  What did the orchestrator know that a worker didn't, and the other way
  round?

## Clean up

Worktrees that subagents leave behind stay on disk until Claude Code's
periodic sweep removes them. To remove them now:

```
git worktree list
git worktree remove --force <path>
```

If git says a worktree is locked, run `git worktree unlock <path>` first.
