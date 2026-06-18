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

Please return the Check-In Capsule and Goal Upgrade Response Format. Always include a concise overview of what happened since the previous check-in. Include suggested goal statements alongside the summary. Only recommend replacing the active goal when the new evidence changes outcome, scope, acceptance criteria, risk, or stop conditions.
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

Run every 25 minutes while this goal is active. If the goal is still active, give the user a short public overview of what happened since the last check-in, send a compact checkpoint to the companion thread with send_message_to_thread, and return suggested updated goal statements alongside the summary. If the goal is complete, blocked, canceled, or the companion thread id is unavailable, report that state and pause the matching heartbeat automation if possible.
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
- Recommended: <best current goal statement>
- Tighter: <smaller/simpler version, or "Not needed">
- Stretch: <broader version only if useful, or "Not needed">

Next 25-minute focus:
<specific next action or checkpoint question>
```

## Discord Check-In Payload

Pass this JSON shape to `scripts/discord_webhook.py send`. Include public summaries only.

```json
{
  "goal": "<current public goal>",
  "since_last_checkin": "<what happened since the last check-in>",
  "evidence": [
    "<test, file, log summary, screenshot summary, decision, or observed behavior>"
  ],
  "blockers_or_drift": [
    "<blocker, scope change, uncertainty, or None>"
  ],
  "suggested_goal_statements": {
    "Recommended": "<best current goal statement>",
    "Tighter": "<smaller/simpler version, or Not needed>",
    "Stretch": "<broader version only if useful, or Not needed>"
  },
  "next_25_minute_focus": "<specific next action or checkpoint question>"
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

Do not include raw diffs, private reasoning, webhook URLs, credentials, API keys, environment variables, or personal data in Discord payloads.

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
