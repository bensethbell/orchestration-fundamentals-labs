# Lab 4a: Let an Orchestrator Agent Run the Workers

**Module:** Orchestrating Multiple Agent Sessions (optional extension)
**Time:** 45 minutes
**Codebase:** the `lab-4a-start` branch of the labs repo (a fresh app at the Lab 3 starting point)
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

## 0. Switch to the Lab 4a branch (5 min)

This lab has its own branch, `lab-4a-start`. It holds a fresh copy of the app at
the Lab 3 starting point: the starter app plus a reference Unit 1 (the
workspace schema), with none of Lab 3's code. It also has a complete
reference decomposition in `taskboard/my-decomposition.md` and the agent files this lab uses, under `.claude/`.
Your Lab 3 work stays safe on `main`.

From your `orchestration-fundamentals-labs/` repo:

```
git status
git worktree list
```

`git status` should show nothing to commit; commit or stash anything left
over from Lab 3 first. If `git worktree list` still shows Lab 3 worktrees,
run Lab 3's clean-up step first. Then switch branches and give the app a
fresh database (`taskboard.db` isn't tracked by git, so your Lab 3 tasks
would otherwise follow you onto this branch):

```
git fetch origin
git switch lab-4a-start
cd taskboard
rm -f taskboard.db
python seed_demo.py
python -m unittest discover -s tests -v
cd ..
```

`seed_demo.py` should report the Engineering and Marketing workspaces, and
all tests should pass.

**Optional:** to use your own Lab 1 decomposition instead of the reference
one, copy it over `taskboard/my-decomposition.md` and commit it:

```
cp <path-to-your-lab-1-decomposition> taskboard/my-decomposition.md
git commit -am "Use my decomposition"
```

Everything else in this lab runs from the repo root, not from `taskboard/`.

---

## 1. Set up the agents (10 min)

The branch already has three files under `.claude/` at the repo root. You
don't need to create them, but read each one before you start: they are
the whole design of this lab. They're reproduced below.

**`.claude/settings.json`** makes worktrees branch from your local `HEAD`,
which is `lab-4a-start`. By default Claude Code branches them from the
remote's default branch, `origin/main`, which has neither the schema nor
these agent files. The file also pre-approves running the tests and the git
commands the orchestrator uses to check and merge, so you aren't approving
a prompt for every step:

```json
{
  "worktree": { "baseRef": "head" },
  "permissions": {
    "allow": [
      "Bash(python -m unittest *)",
      "Bash(cd taskboard && python -m unittest *)",
      "Bash(git status *)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git branch *)",
      "Bash(git merge *)",
      "Bash(git rev-parse *)",
      "Bash(git worktree *)"
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
   Unit 1 (the schema) is already on the current branch; run
   `git branch --show-current` and call that branch BASE. Plan Units 2-4: for each, the
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
   - `git diff --stat BASE...<branch>`: flag files outside its allowed list.
   - Run the tests inside its worktree, from its taskboard/ folder.
   - Name any function more than one branch changed.
   Show a status table and a proposed merge order, then wait for the
   user's go-ahead.
4. Merge into BASE one branch at a time with `git merge --no-ff`. After
   each merge, run the full test suite and check `git rev-parse HEAD`.
5. If a merge conflicts or the tests fail, stop. Show the user the
   conflict or failure and suggest options. Don't resolve it yourself.
```

Start the orchestrator as your main session, from the repo root
(`orchestration-fundamentals-labs/`). Start it from a terminal where your
Python venv is active, so the workers can run the tests:

```
claude --agent orchestrator
```

The first time you start Claude Code in a new folder it asks whether you
trust the folder. The highlighted answer is **"No, exit"**, so pressing
Enter quits. Press the down arrow to select "Yes, I trust this folder",
then Enter.

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
   The orchestrator may also change the shape of the plan, for example
   proposing a small extra unit that runs first because all three workers
   would otherwise each write the same helper. That's a legitimate
   orchestration decision, not a malfunction. Decide whether you agree,
   just as you would if a colleague suggested it.
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

Then run the **Demo it** walkthrough from Lab 3, steps 1 to 9, including
its `python seed_demo.py` and `python run.py` setup. Every expected result
comes from `taskboard/FEATURE_REQUEST.md`, so if a step doesn't match, the
merged code is wrong, not the walkthrough. The demo checks things no single
worker's tests can: that the switcher page and the API agree on
`?workspace_id=`, that a non-member gets `403` from the merged routes, and
that the notification line appears in the server terminal when the API
assigns a task. If a step fails, describe the failure to the orchestrator
and let it send a worker to fix it; that's one more round of the loop you
just ran.

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
