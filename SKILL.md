---
name: goal-companion
description: Optional quiet goal-alignment helper for Codex runs. Use when the user explicitly invokes goal-companion, asks for a companion side thread, asks for long-goal check-ins or keepalive, requests goal-statement refinement, asks for Discord goal-progress delivery, or wants this skill updated. Do not trigger for ordinary short /goal starts, routine planning, or incidental mentions of goals unless the user clearly wants companion behavior.
---

# Goal Companion

Use this skill to keep long Codex goals sharp without adding noise. The main thread executes the work; when explicitly enabled, the companion side thread acts as a goal editor that proposes upgraded goal statements, acceptance criteria, stop conditions, risks, and next checkpoints. Default to quiet, checkpoint-only help unless the user asks for a side thread, keepalive, or Discord delivery.

## Quiet Defaults

- Do not create a side thread for ordinary short goals, routine planning, or ambiguous "goal" mentions.
- Do not create a heartbeat automation unless the user explicitly asks for ongoing check-ins, keepalive, or a long-run companion.
- Do not ask about Discord setup unless the user asks for Discord delivery.
- Do not show suggested goal statements unless the user asks or new evidence materially changes scope, acceptance criteria, risk, or stop conditions.
- Keep user-facing check-ins short and focused on meaningful changes since the previous check-in.

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

The installer is idempotent and upgrades the marker-delimited block when this skill's standing instruction changes. If the block already exists, continue without asking again unless the installer would write a change.

Only check optional Discord delivery when the user asks for Discord check-ins, explicitly enables a heartbeat that should post to Discord, or asks for Discord setup/status:

```powershell
py -3 C:\Users\Piculiar\.codex\skills\goal-companion\scripts\discord_webhook.py status
```

If Discord is unconfigured and the user asked for Discord delivery, tell them it is optional and give the hidden local setup prompt. Do not ask them to paste a webhook URL in chat:

```powershell
py -3 C:\Users\Piculiar\.codex\skills\goal-companion\scripts\discord_webhook.py configure
```

The webhook URL is a secret. It must live only in the local config at `%LOCALAPPDATA%\GoalCompanion\discord.json` by default, or the path named by `GOAL_COMPANION_DISCORD_CONFIG`. Never print, summarize, commit, or send the full webhook URL.

## Companion Setup

When this skill triggers, first choose the lightest useful mode:

- **Quiet checkpoint mode:** Default for short or unclear requests. Refine goal language inside the main thread only when useful. Do not create a side thread or heartbeat.
- **Side-thread mode:** Use only when the user explicitly asks for a companion/side thread or the run is clearly long and the user opted into Goal Companion for this run.
- **Keepalive mode:** Use only when the user explicitly asks for ongoing 25-minute check-ins, keepalive, or long-run heartbeat behavior.

For side-thread or keepalive mode:

1. Search for the Codex thread tools if they are not already loaded: `create_thread`, `send_message_to_thread`, `read_thread`, `set_thread_title`, and `set_thread_pinned`.
2. Search for `automation_update` if keepalive mode is enabled.
3. Create exactly one side thread for the active goal. Default to a projectless thread unless the side thread truly needs repo-local context. If using a project target, call `list_projects` first and prefer a local environment.
4. Prompt the side thread with the "Initial side-thread prompt" from `references/templates.md`, filled with the current goal, known constraints, current workspace/repo, and any explicit user preferences.
5. Rename the side thread to `Goal Companion - <short goal name>` and pin it when thread tools allow.
6. Keep the companion thread id in the main thread's visible working state so future checkpoint and heartbeat messages can target it.

If the thread tools are unavailable, continue in checkpoint-only mode: perform the same goal-refinement analysis inside the main thread and tell the user that a side thread could not be created.

## Checkpoint Loop

In quiet checkpoint mode, keep checkpoint thinking inside the main thread and surface only concise, useful goal guidance.

In side-thread or keepalive mode, send compact updates to the side thread at major state changes:

- After initial planning.
- After meaningful discovery changes the goal shape.
- After implementation reaches a stable milestone.
- After tests or verification produce results.
- When blocked, when scope expands, or when assumptions change.
- Before final response or goal completion.

Skip side-thread updates when nothing material changed. Prefer one well-timed checkpoint over many tiny pings.

Use the "Checkpoint update prompt" from `references/templates.md`. Every checkpoint response should include a Check-In Capsule:

- Since last check-in: what changed, in plain language.
- Evidence: tests, files, logs, screenshots, decisions, or observed behavior.
- Blockers or drift: anything slowing, widening, or changing the run.
- Suggested goal statements: include only when requested or when evidence changes scope, criteria, risk, or the likely stopping point.
- Next 25-minute focus: the clearest next move before the next heartbeat.

Ask the companion for revised goal statements only when new evidence changes scope, criteria, risk, or the likely stopping point.

The companion never silently changes the active goal. It returns suggested language. The main thread decides whether to show the suggestion to the user, incorporate it into a visible plan, or ask the user to accept a goal update.

## Keepalive

Do not create keepalive automations by default. When the user explicitly enables keepalive for a long goal, create or update a heartbeat automation attached to the main local thread:

- Name: `Goal Companion Keepalive - <short goal name>`
- Kind: `heartbeat`
- Destination: current thread
- Schedule: `RRULE:FREQ=MINUTELY;INTERVAL=25`
- Prompt: use the "Heartbeat keepalive prompt" from `references/templates.md`, filled with the companion thread id and current goal summary.

Before creating a heartbeat, inspect existing automations when possible and update a matching `Goal Companion Keepalive - ...` automation instead of creating a duplicate.

When keepalive is enabled, the heartbeat runs every 25 minutes while the goal is active. Each heartbeat should:

1. Compare the current visible state with the previous check-in.
2. Give the user a short public overview of what happened since the last check-in.
3. Send a compact checkpoint to the side thread with `send_message_to_thread`.
4. Return suggested updated goal statements only when the goal materially changed or the user requested them.
5. Name the next 25-minute focus and the next checkpoint question.

If there is no meaningful progress, say that plainly and suggest the smallest useful next move. If posting to Discord, send only the brief public progress review and omit the active goal and suggested goal statements. If the goal is done, blocked, canceled, or the companion thread id is missing, report that state and stop or pause the matching heartbeat automation when possible.

If automation tools are unavailable, fall back to manual checkpoint pings and tell the user the keepalive could not be installed.

## Discord Delivery

Discord delivery is opt-in and never prompted during normal first use. If the user explicitly requests it and Discord is configured, send a brief public review of what happened since the previous check-in to Discord after each enabled heartbeat and major checkpoint. Keep goal statements and goal-upgrade suggestions in the main thread and companion thread, not in Discord.

Use the bundled script instead of hand-crafting webhook requests:

```powershell
@'
{
  "since_last_checkin": "<one to three sentence public review of what changed since the previous check-in>"
}
'@ | py -3 C:\Users\Piculiar\.codex\skills\goal-companion\scripts\discord_webhook.py send
```

Safety rules:

- Send only public execution summaries, never private reasoning, raw diffs, secrets, credentials, environment variables, or personal data.
- Do not include the current goal or suggested goal statements in Discord payloads.
- Let `discord_webhook.py` sanitize webhook URLs, token-looking values, and mention pings before delivery.
- Keep Discord mentions disabled through `allowed_mentions: {"parse": []}`.
- If Discord sending fails, report it as non-blocking and continue the goal workflow.

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
