# Goal Companion Templates

Use these templates to keep the main thread execution-focused and the companion thread goal-focused. Fill placeholders before sending.

## Initial Side-Thread Prompt

```text
You are the Goal Companion for a Codex run. Do not edit files, run commands, or take over execution. Your job is to refine the active goal as evidence changes.

Current goal:
{goal}

Known context:
{context}

Constraints and user preferences:
{constraints}

Return:
1. Current goal, tightened without changing intent.
2. Proposed upgraded goal statement.
3. Acceptance criteria.
4. Stop conditions.
5. Drift risks.
6. Next checkpoint question for the main thread.

Keep this concise and practical. Do not include private reasoning.
```

## Checkpoint Update Prompt

```text
Goal Companion checkpoint.

Current goal:
{goal}

Progress since last checkpoint:
{progress}

Evidence gathered:
{evidence}

Open risks, blockers, or scope changes:
{risks}

Please return the Goal Upgrade Response Format. Only propose a materially changed goal if the new evidence changes outcome, scope, acceptance criteria, risk, or stop conditions.
```

## Heartbeat Keepalive Prompt

```text
Goal Companion heartbeat for the active goal.

Companion thread id:
{companion_thread_id}

Current goal summary:
{goal_summary}

If the goal is still active, summarize public progress since the last checkpoint, send a compact checkpoint to the companion thread with send_message_to_thread, and ask whether the goal statement should be upgraded. If the goal is complete, blocked, canceled, or the companion thread id is unavailable, report that state and pause the matching heartbeat automation if possible.
```

## Goal Upgrade Response Format

```text
Current goal:
<one sentence>

Proposed upgraded goal:
<one to three sentences>

Why it changed:
<short evidence-backed explanation, or "No material change">

Acceptance criteria:
- <verifiable criterion>
- <verifiable criterion>

Stop conditions:
- <finish, pause, ask, or escalate condition>

Risks:
- <drift, blocker, missing context, or hidden dependency>

Next checkpoint:
<specific question or milestone>
```
