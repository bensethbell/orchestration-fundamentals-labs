# Feature Request: Workspaces with Roles and Assignment Notifications

## Background

TaskBoard currently has one flat list of tasks and users with no grouping or
permissions. A pilot customer wants to use TaskBoard across three separate
teams inside their company and needs those teams kept apart.

## Requested feature

Add multi-workspace support to TaskBoard:

1. **Workspaces and membership.** A workspace is a named container for tasks
   (e.g. "Engineering," "Marketing"). Every task belongs to exactly one
   workspace. Every user can belong to multiple workspaces, and within each
   workspace a user is either an **admin** or a **member**.

2. **Roles and enforcement.** All existing task endpoints must respect
   workspace boundaries and roles. A user should never be able to see,
   create, or modify a task in a workspace they don't belong to.
   - An **admin** can create and delete tasks, invite and remove members,
     and change any task.
   - A **member** can create tasks and edit tasks assigned to them, but
     cannot delete tasks or manage membership.

3. **Workspace switcher (UI).** The web UI should let a logged-in user see
   which workspaces they belong to and switch between them; the task list
   should only ever show tasks for the currently selected workspace.

4. **Assignment notifications.** When a task is assigned to a user (i.e. its
   `owner_id` is set or changed), that user should receive an email
   notification. For this exercise, "send an email" means calling a
   `notify(user, task)` function that logs the notification — you do not need
   to wire up a real mail provider.

## Constraints and notes for facilitators / participants

- This is intentionally underspecified in places (e.g., what happens to a
  task if its owner is removed from the workspace?). Participants should
  surface these as open questions in their task specs, not silently guess.
- The data model has a real dependency chain: nothing else can be built until
  workspaces and workspace membership exist in the schema. That's
  deliberate — it's the sequencing example for Module 1.
- The repo's `seed_demo.py` loads the demo data used in later labs. Use the
  table and column names it expects (they're listed at the top of the
  script), and don't modify it.
- Once the schema/migration piece is done, the API/permissions work, the
  frontend workspace switcher, and the notification hook are largely
  independent of each other and don't touch the same files — that's
  deliberate too, and it's what Module 3's parallel-worktree lab uses.
