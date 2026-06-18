# Goal Companion Skill

![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=for-the-badge)
![Status](https://img.shields.io/badge/status-experimental-2563eb?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.x-16a34a?style=for-the-badge)

A Codex skill that gives long-running goals a second brain.

Goal Companion creates a background side thread for active Codex goals, feeds it compact checkpoints, and asks it to suggest sharper goal statements as the work unfolds. The main thread keeps building. The companion keeps the mission honest.

## Why

Long Codex runs can start with a goal that feels clear, then drift as discovery, blockers, tests, and scope changes pile up. Goal Companion turns that drift into an explicit feedback loop:

- What is the current goal now that we know more?
- What evidence proves the goal is done?
- What should stay out of scope?
- When should the agent stop, pause, escalate, or ask the user?

It is basically a quiet goal editor riding shotgun.

## What It Does

- Creates a Codex background side thread for goal refinement.
- Sends milestone checkpoints after planning, discovery, implementation, testing, blockers, and finalization.
- Suggests upgraded goal statements without silently changing the active goal.
- Defines acceptance criteria, stop conditions, risks, and next checkpoint questions.
- Includes an idempotent installer for a standing Codex instruction.
- Supports a heartbeat workflow so long goals keep their companion awake.

## Important Limitation

This skill does **not** patch Codex's native `/goal` command or install a true product-level slash-command hook.

Instead, it works through:

1. Skill trigger metadata.
2. A standing instruction in `AGENTS.md`.
3. Codex thread and automation tools when available.

That means it can behave like an upgraded goal mode, but it still depends on Codex seeing the goal-start context.

## Install

Clone this repo into your Codex skills directory.

### Windows PowerShell

```powershell
git clone https://github.com/bhupendrafire-ai/goal-companion-skill "$env:USERPROFILE\.codex\skills\goal-companion"
```

### macOS / Linux

```bash
git clone https://github.com/bhupendrafire-ai/goal-companion-skill ~/.codex/skills/goal-companion
```

Restart Codex or open a fresh thread if the skill does not appear immediately.

## First Use

Invoke it explicitly once:

```text
Use $goal-companion with this goal: Build the dashboard and keep the run aligned until it is verified.
```

On first use, the skill checks whether this block exists in your Codex `AGENTS.md`:

```md
<!-- goal-companion:start -->
# Goal Companion
- Whenever I start a goal, use goal-companion and create a background side thread to refine goal statements.
- During long goals, keep the companion active with heartbeat and milestone checkpoint updates, and stop the keepalive when the goal finishes.
<!-- goal-companion:end -->
```

If the block is missing, the skill runs a dry-run and asks before changing global Codex behavior.

## Usage

Explicit invocation:

```text
Use $goal-companion to create a side thread that refines this goal as the run proceeds.
```

Goal-style invocation after the standing instruction is installed:

```text
/goal Build and verify the export workflow end to end.
```

The companion should then help refine the active objective as checkpoints come in.

## How It Works

```mermaid
flowchart LR
    A[Main Codex Goal] --> B[Goal Companion Skill]
    B --> C[Background Side Thread]
    A --> D[Milestone Checkpoints]
    D --> C
    C --> E[Upgraded Goal Suggestions]
    E --> A
    B --> F[Heartbeat Keepalive]
    F --> A
```

The side thread does not execute the task. It reviews progress summaries and returns better goal language, criteria, risks, and stopping rules.

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── templates.md
└── scripts/
    └── install_standing_instruction.py
```

## Safety

Goal Companion is intentionally conservative:

- It does not silently rewrite your active goal.
- It asks before installing global standing instructions.
- It keeps companion updates compact and public.
- It falls back to checkpoint-only mode if thread or automation tools are unavailable.
- It pauses keepalive behavior when the goal finishes, is canceled, or is blocked.

## Roadmap Ideas

- Smarter duplicate side-thread detection.
- A local status file for active companion thread IDs.
- Optional Obsidian/second-brain handoff summaries.
- A dashboard view for active goals and companion suggestions.
- Native `/goal` integration if Codex exposes slash-command hooks.

## License

No license has been added yet. Add one before others reuse or redistribute this skill.

---

Built as a first public repo and a small experiment in making long agent runs feel less blurry.
