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

Previous check-in:
{previous_checkin}

Progress since last checkpoint:
{progress}

Evidence gathered:
{evidence}

Open risks, blockers, or scope changes:
{risks}

Please return a concise Check-In Capsule. Always include what meaningfully changed since the previous check-in. Include suggested goal statements only when requested or when new evidence changes outcome, scope, acceptance criteria, risk, or stop conditions.
```

## Heartbeat Keepalive Prompt

```text
Goal Companion heartbeat for the active goal.

Companion thread id:
{companion_thread_id}

Current goal summary:
{goal_summary}

Previous check-in:
{previous_checkin}

Run only when keepalive was explicitly enabled for this goal. If the goal is still active, give the user a short public overview of meaningful changes since the last check-in, send one compact checkpoint to the companion thread with send_message_to_thread, and include suggested updated goal statements only when the goal materially changed or the user requested them. If Discord is configured for this enabled keepalive, send only the brief public overview there; do not include the current goal or suggested goal statements in the Discord message. If the goal is complete, blocked, canceled, or the companion thread id is unavailable, report that state and pause the matching heartbeat automation if possible.
```

## Check-In Capsule

```text
Since last check-in:
<plain-language summary of meaningful progress, decisions, verification, or lack of movement>

Evidence:
- <test, file, log, screenshot, decision, or observation>

Blockers or drift:
- <blocker, scope change, uncertainty, or "None">

Suggested goal statements:
- <include only if requested or materially changed; otherwise write "No material change">

Next 25-minute focus:
<specific next action or checkpoint question>
```

## Discord Check-In Payload

Pass this JSON shape to `scripts/discord_webhook.py send`. Include only a brief public review of what changed since the previous check-in.

```json
{
  "since_last_checkin": "<one to three sentence review of what happened since the last check-in>"
}
```

The resulting Discord request must include:

```json
{
  "allowed_mentions": {
    "parse": []
  }
}
```

Do not include the current goal, suggested goal statements, raw diffs, private reasoning, webhook URLs, credentials, API keys, environment variables, or personal data in Discord payloads.

## Goal Upgrade Response Format

```text
Current goal:
<one sentence>

Suggested goal statements:
- Recommended: <one to three sentences>
- Tighter: <smaller/simpler version, or "Not needed">
- Stretch: <broader version only if useful, or "Not needed">

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
