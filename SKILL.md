---
name: goal-companion
description: Create and coordinate a Codex background side thread that refines active goal statements during /goal starts, goal updates, long-running goals, resumed goals, or explicit goal refinement requests. Use when the user starts or resumes a /goal, asks to keep a long Codex run aligned, wants upgraded goal statements, wants a side chat or companion thread for goal coaching, or mentions goal drift, stop conditions, acceptance criteria, checkpoints, or keeping a goal companion alive.
---

# Goal Companion

Use this skill to keep long Codex goals sharp. The main thread executes the work; the companion side thread acts as a goal editor that proposes upgraded goal statements, acceptance criteria, stop conditions, risks, and next checkpoints.

## First-Use Bootstrap

Before creating a companion thread, check whether the standing instruction block is present in `C:\Users\Piculiar\.codex\AGENTS.md`:

```text
<!-- goal-companion:start -->
```

If the block is absent:

1. Run a dry-run:

```powershell
py -3 C:\Users\Piculiar\.codex\skills\goal-companion\scripts\install_standing_instruction.py --dry-run
```

2. Tell the user this changes global Codex instructions and ask for explicit approval before writing.
3. After approval, run:

```powershell
py -3 C:\Users\Piculiar\.codex\skills\goal-companion\scripts\install_standing_instruction.py
```

The installer is idempotent. If the block already exists, do not ask again and continue.

## Companion Setup

When this skill triggers:

1. Search for the Codex thread tools if they are not already loaded: `create_thread`, `send_message_to_thread`, `read_thread`, `set_thread_title`, and `set_thread_pinned`.
2. Search for `automation_update` if it is not already loaded and the goal is expected to run longer than one focused turn.
3. Create exactly one side thread for the active goal. Default to a projectless thread unless the side thread truly needs repo-local context. If using a project target, call `list_projects` first and prefer a local environment.
4. Prompt the side thread with the "Initial side-thread prompt" from `references/templates.md`, filled with the current goal, known constraints, current workspace/repo, and any explicit user preferences.
5. Rename the side thread to `Goal Companion - <short goal name>` and pin it when thread tools allow.
6. Keep the companion thread id in the main thread's visible working state so future checkpoint and heartbeat messages can target it.

If the thread tools are unavailable, continue in checkpoint-only mode: perform the same goal-refinement analysis inside the main thread and tell the user that a side thread could not be created.

## Checkpoint Loop

Send compact updates to the side thread at these moments:

- After initial planning.
- After meaningful discovery changes the goal shape.
- After implementation reaches a stable milestone.
- After tests or verification produce results.
- When blocked, when scope expands, or when assumptions change.
- Before final response or goal completion.

Use the "Checkpoint update prompt" from `references/templates.md`. Ask the companion for a revised goal only when new evidence changes scope, criteria, risk, or the likely stopping point.

The companion never silently changes the active goal. It returns suggested language. The main thread decides whether to show the suggestion to the user, incorporate it into a visible plan, or ask the user to accept a goal update.

## Keepalive

For long goals, create or update a heartbeat automation attached to the main local thread:

- Name: `Goal Companion Keepalive - <short goal name>`
- Kind: `heartbeat`
- Destination: current thread
- Schedule: `RRULE:FREQ=MINUTELY;INTERVAL=25`
- Prompt: use the "Heartbeat keepalive prompt" from `references/templates.md`, filled with the companion thread id and current goal summary.

Before creating a heartbeat, inspect existing automations when possible and update a matching `Goal Companion Keepalive - ...` automation instead of creating a duplicate.

The heartbeat should wake the main thread, summarize progress publicly, send a compact checkpoint to the side thread with `send_message_to_thread`, and ask for an upgraded goal statement only if the active goal is still running. If the goal is done, blocked, canceled, or the companion thread id is missing, the heartbeat should report that clearly and stop or pause itself when possible.

If automation tools are unavailable, fall back to manual checkpoint pings and tell the user the keepalive could not be installed.

## Upgrade Heuristics

Ask the companion to improve the goal along these dimensions:

- Outcome: make the desired end state concrete and verifiable.
- Boundaries: separate in-scope work from tempting side quests.
- Evidence: name tests, screenshots, logs, docs, or demos that prove completion.
- Stop conditions: define when to finish, pause, escalate, or ask the user.
- Risk: identify drift, missing context, blocked dependencies, and hidden global changes.
- Handoff: keep a compact final capsule so future resumes start from the latest real goal.

Prefer small, timely upgrades over dramatic rewrites. A good upgraded goal should make the next action easier.

## Cleanup

When the goal completes, is canceled, or is genuinely blocked:

1. Send a final checkpoint to the companion thread.
2. Ask for a final handoff capsule and final goal statement.
3. Pause the matching heartbeat automation. Delete it only if the user explicitly asks for removal.
4. Leave the side thread pinned if it contains useful handoff context; unpin or archive only when the user asks.
