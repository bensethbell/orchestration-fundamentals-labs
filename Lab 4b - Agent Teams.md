# Lab 4b: Build It with an Agent Team

**Module:** Orchestrating Multiple Agent Sessions (optional extension)
**Time:** 45 minutes
**Codebase:** a fresh copy of the labs repo at the Lab 3 starting point
**Goal:** Build the same feature as Lab 3 and Lab 4a (Units 2–4 on top of
the schema: the API, frontend and notifications units, called Units A, B
and C in Lab 3), this time with Claude Code **agent teams**. A lead session
creates a shared task list and spawns teammates. The teammates claim
tasks and message each other directly, with no human in between.

| | Lab 3 | Lab 4a | Lab 4b (this lab) |
|---|---|---|---|
| Who coordinates | You | An orchestrator agent | A team lead, plus teammates messaging each other |
| How work is isolated | One worktree per session | One worktree per subagent | No isolation: one shared checkout, each file has one owner |
| How it's combined | You merge | The orchestrator merges, after you approve | No merge: everyone edits the same files |

The last row is the main thing to learn here. Teammates don't get their
own worktrees. All of them edit the same working directory at the same
time, so there is no merge step to catch a collision. Two teammates
editing the same file just overwrite each other. Coordination has to
happen **before and during** the work, not at a merge afterwards.

**Agent teams are experimental**, and they use a lot more tokens than a
single session. Agent teams need an interactive session, so they don't
work with `claude -p`.

---

## 0. Start from the Lab 3 starting point (5 min)

This is the same setup as Lab 4a, in a separate copy. The git repo is
`orchestration-fundamentals-labs/`; the app lives in its `taskboard/`
folder. From the folder that contains `orchestration-fundamentals-labs/`:

```
git clone orchestration-fundamentals-labs labs-4b
cd labs-4b
git log --oneline
```

Replace `<sha>` with your Unit 1 schema commit. Your decomposition
replaces the example `taskboard/my-decomposition.md`, and tests only run
from inside `taskboard/`:

```
git reset --hard <sha>
cp <path-to-your-lab-1-decomposition> taskboard/my-decomposition.md
cd taskboard
python -m unittest discover -s tests -v
cd ..
```

Everything else in this lab runs from the repo root (`labs-4b/`).

---

## 1. Turn on agent teams (5 min)

Create `.claude/settings.json` at the root of `labs-4b`. This turns agent teams
on for this project only, and pre-approves the commands every teammate
will run. Teammates' permission prompts all appear in the lead's terminal,
so without this you'll be approving prompts for three agents at once:

```json
{
  "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" },
  "permissions": {
    "allow": [
      "Edit",
      "Write",
      "Bash(python -m unittest *)",
      "Bash(cd taskboard && python -m unittest *)",
      "Bash(git status *)",
      "Bash(git diff *)"
    ]
  }
}
```

Allowing `Edit` and `Write` everywhere is fine in a throwaway clone. Don't
copy it into a real project.

Start the lead from the repo root, in a terminal where your Python venv
is active:

```
claude
```

All teammates run inside this one terminal by default. If you use tmux or
iTerm2 and want a split pane for each teammate, start with
`claude --teammate-mode tmux` instead. That's optional.

---

## 2. Decide who owns which file (10 min)

This is the step that replaces Lab 3's merge. In Lab 3 the overlaps
showed up as merge conflicts. Here they would show up as silently lost
edits. Before you spawn anyone, write down one owner for every file.

Two files are needed by more than one unit:

- `taskboard/app/routes.py`: the API unit rewrites the task routes, and
  the frontend unit needs a route to list workspaces and the `/` page.
- `taskboard/app/db.py`: the API unit changes `create_task` and
  `update_task`, and the notifications unit needs to hook the same two
  functions.

Choose how to handle each overlap. Two patterns work:

- **One owner, others ask.** The API teammate owns `db.py`. The
  notifications teammate writes `taskboard/app/notifications.py` and
  **messages** the API teammate to add the `notify(...)` calls.
- **Split the file.** The frontend teammate puts its routes in a new
  `taskboard/app/workspace_views.py`. Then `routes.py` has only one owner.

You can also order the work: make the notifications hook a task that
depends on the API teammate's `db.py` task. The shared task list won't
let anyone claim a task until the tasks it depends on are done.

Write your ownership table down. You'll paste it into the spawn prompt.

Also pick a model for each teammate, the same way you did in Lab 3. Every
teammate is a full Claude session, and a team uses far more tokens than
one session, so don't default all three to the strongest model. A
reasonable starting point: Sonnet for `api` and `frontend`, Haiku for
`notifications` (a small, well-bounded module).

---

## 3. Spawn the team (20 min)

Give the lead the whole brief in one prompt. Teammates load
`CLAUDE.md` and the project files, but **not** the lead's conversation,
so anything they need to know has to be in this prompt:

```
> Create an agent team to build Units 2-4 from taskboard/my-decomposition.md.
> Unit 1 (the schema) is already done. Don't change the SCHEMA string.
> The app is in the taskboard/ folder; run tests from there.
>
> Spawn three teammates: api (Sonnet), frontend (Sonnet) and
> notifications (Haiku). [Change the models to your own picks.]
> Each one gets its unit's spec and acceptance criteria from
> taskboard/my-decomposition.md.
>
> File ownership (only the owner edits a file; anyone else messages the owner):
> [paste your table from step 2]
>
> Rules for every teammate:
> - The selected workspace is passed as ?workspace_id= everywhere.
> - While working, run only your own test file. Others are editing too.
> - Message the teammate who owns a file instead of editing it.
>
> Don't implement anything yourself. Wait for the teammates to finish,
> then run the full test suite and report.
```

While it runs:

- Teammates appear in the panel below the prompt. Use the **up and down
  arrows** to select one and **Enter** to see its work. Type there to
  message it directly. **Escape** goes back.
- **Ctrl+T** shows the shared task list.
- Watch the messages between teammates. Does `notifications` actually ask
  `api` to add the hook, or does it edit `db.py` itself?

If the lead starts writing code itself, tell it: "Wait for your teammates
to complete their tasks before proceeding."

When everyone is done, ask the lead to shut the team down:

```
> Ask all teammates to shut down.
```

---

## 4. Verify like Lab 3 (5 min)

There's nothing to merge, but there is still something to check:

```
git status
git diff --stat
cd taskboard
python -m unittest discover -s tests -v
```

Look through `git diff` for edits by someone who didn't own the file. Then
run the **Demo it** walkthrough from Lab 3, steps 1 to 9. Commit when
you're happy with it.

---

## Debrief

Be ready to answer these:

- Did your ownership rules hold? Find one place where a teammate messaged
  another instead of editing the file. Find one place where the rules
  weren't followed, if there is one.
- In Lab 3 you found overlaps at merge time. Here they had to be designed
  out up front. Which way caught more problems?
- The teammates could talk to each other directly. Did that solve
  anything the Lab 3 sessions couldn't, such as agreeing on the query
  parameter?
- Compare Labs 3, 4a and 4b on cost, speed, how much you had to step in,
  and how much you trusted the result. For which kind of work would you
  pick each one?

## If something goes wrong

- **No teammates appear:** the lead may have used plain subagents
  instead. Ask again and explicitly ask for an agent team.
- **A teammate stops early:** select it in the panel and give it more
  instructions, or ask the lead to spawn a replacement.
- **A task looks stuck:** task status can lag. Check whether the work is
  actually done, then tell the lead to mark it complete.
- **You resumed the session and the teammates are gone:** `/resume`
  doesn't bring teammates back. Ask the lead to spawn new ones.
