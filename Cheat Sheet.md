# Orchestration Fundamentals — Quick Reference

*Keep this open in a tab. One page, no fluff.*

## Is this task agent-ready?

A unit of work is ready to hand off when it has all four:
1. **Bounded scope** — touches an identifiable, small set of files
2. **Acceptance criteria** — checkable without reading the whole diff
3. **Named dependencies** — what it needs first, what it blocks
4. **A verification step** — a test, a curl, a page you can look at

## Model decision table

| Situation | Model |
|---|---|
| Small, well-specified, low-risk | Haiku |
| Default for day-to-day implementation | Sonnet |
| Architecture decisions, foundational/shared code, higher-risk changes | Opus |
| Long, ambiguous, investigative work | Fable (if available on your plan) |

Effort level (`low`/`medium`/`high`/`xhigh`/`max`) is independent of model
choice — it's how much the model reasons/verifies, not which model runs.

```
/model            # open picker
/model opus       # switch now
s                 # (in picker) apply to this session only
```

## Git worktrees for parallel sessions

```
claude --worktree <name>      # new isolated session + branch (interactive —
                               # takes over the terminal; one tab per unit)
git worktree list             # see all active worktrees + their branches
git worktree remove <path>    # clean up when done
```

Branch created is `worktree-<name>`, not `<name>` — check `git worktree
list` before merging rather than assuming.

Running all three at once: default to **one terminal tab per command** —
simplest, nothing new to learn. If you already know the flags:
`--bg`/`--background` runs it non-interactively in the background (manage
with `claude agents`, `claude logs <id>`, `claude attach <id>`); `--tmux`
auto-creates an iTerm2 pane or tmux session for it instead.

Use worktrees only for units with **no file overlap and no dependency** on
each other. Sequential/dependent work still goes on `main`, one at a time.

## Subagent tool scoping (least privilege)

```yaml
---
name: my-agent
description: when Claude should delegate to this agent
tools: Read, Edit, Write, Bash   # omit this field = full access, not none
model: sonnet                     # or opus, haiku, inherit
---
```

Research/investigation-only agents: no `Write`/`Edit`. Subagents can't ask
you clarifying questions and auto-deny permission prompts in the
background — keep approval-gated actions in the main session.

## Merge discipline

Merge one unit at a time. Verify (tests + a manual check) between each
merge, not after all of them. If a "merge conflict" shows up, check whether
a unit quietly touched files outside its stated scope before assuming it's
a normal git conflict.
