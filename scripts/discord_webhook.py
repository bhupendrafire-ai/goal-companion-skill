#!/usr/bin/env python3
"""Configure and send Goal Companion check-ins to Discord safely."""

from __future__ import annotations

import argparse
import datetime as dt
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from typing import Any
from urllib import error, parse, request


DISCORD_WEBHOOK_RE = re.compile(
    r"^https://(?:discord(?:app)?\.com)/api/webhooks/\d+/[A-Za-z0-9._~-]+/?$"
)
DISCORD_WEBHOOK_FIND_RE = re.compile(
    r"https://(?:discord(?:app)?\.com)/api/webhooks/\d+/[A-Za-z0-9._~-]+/?"
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(token|secret|password|api[_-]?key|authorization)\b\s*[:=]\s*[^\s,;]+"
)
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
MENTION_RE = re.compile(r"<(@[!&]?|#)\d+>")
MOJIBAKE_BOM = "ï»¿"
SUMMARY_KEYS = ("since_last_checkin", "review", "summary", "progress", "changes")


def default_config_path() -> Path:
    configured = os.environ.get("GOAL_COMPANION_DISCORD_CONFIG")
    if configured:
        return Path(configured).expanduser()
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / ".config"
    return root / "GoalCompanion" / "discord.json"


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def validate_webhook_url(url: str) -> str:
    candidate = url.strip()
    if not DISCORD_WEBHOOK_RE.match(candidate):
        raise ValueError(
            "Expected a Discord webhook URL like "
            "https://discord.com/api/webhooks/<id>/<token>."
        )
    return candidate.rstrip("/")


def webhook_fingerprint(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"fingerprint={digest}"


def redacted_config_status(config: dict[str, Any]) -> str:
    url = str(config.get("webhook_url", ""))
    if not url:
        return "unconfigured"
    return f"configured ({webhook_fingerprint(url)})"


def restrict_permissions(path: Path) -> None:
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    if os.name == "nt":
        username = os.environ.get("USERNAME")
        if not username:
            return
        try:
            subprocess.run(
                [
                    "icacls",
                    str(path),
                    "/inheritance:r",
                    "/grant:r",
                    f"{username}:F",
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError:
            pass


def load_config(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Discord config is not a JSON object.")
    if "webhook_url" in data:
        data["webhook_url"] = validate_webhook_url(str(data["webhook_url"]))
    return data


def save_config(path: Path, webhook_url: str) -> dict[str, Any]:
    config = {
        "webhook_url": validate_webhook_url(webhook_url),
        "updated_at": now_iso(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
        handle.write("\n")
    restrict_permissions(path)
    return config


def clear_config(path: Path) -> bool:
    if not path.exists():
        return False
    path.unlink()
    return True


def sanitize_text(value: Any, limit: int = 900) -> str:
    if value is None:
        text = "None"
    elif isinstance(value, (list, tuple, set)):
        text = "\n".join(f"- {sanitize_text(item, 240)}" for item in value) or "None"
    elif isinstance(value, dict):
        text = "\n".join(
            f"- {sanitize_text(key, 80)}: {sanitize_text(item, 240)}"
            for key, item in value.items()
        ) or "None"
    else:
        text = str(value)

    text = DISCORD_WEBHOOK_FIND_RE.sub("[redacted discord webhook]", text)
    text = SECRET_ASSIGNMENT_RE.sub(lambda m: f"{m.group(1)}=[redacted]", text)
    text = BEARER_RE.sub("Bearer [redacted]", text)
    text = text.replace("@everyone", "@\u200beveryone")
    text = text.replace("@here", "@\u200bhere")
    text = MENTION_RE.sub("[redacted mention]", text)
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    if len(text) > limit:
        return text[: max(0, limit - 15)].rstrip() + "\n[truncated]"
    return text


def normalize_payload_text(raw: str) -> str:
    text = raw.strip()
    while text.startswith("\ufeff"):
        text = text[1:].lstrip()
    while text.startswith(MOJIBAKE_BOM):
        text = text[len(MOJIBAKE_BOM) :].lstrip()
    return text


def load_checkin_payload(path: Path | None) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    raw = normalize_payload_text(raw)
    if not raw:
        raise ValueError("No check-in payload provided.")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"since_last_checkin": raw}
    if not isinstance(parsed, dict):
        raise ValueError("Check-in payload must be a JSON object or plain text.")
    return parsed


def first_summary_value(checkin: dict[str, Any]) -> Any:
    for key in SUMMARY_KEYS:
        value = checkin.get(key)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def nested_checkin_from_text(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    text = normalize_payload_text(value)
    if not text.startswith("{"):
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def public_review(checkin: dict[str, Any]) -> str:
    review = first_summary_value(checkin)
    nested = nested_checkin_from_text(review)
    if nested is not None:
        review = first_summary_value(nested)
    text = sanitize_text(
        review or "No meaningful progress was recorded since the last check-in.",
        1200,
    ).strip()
    if not text or text.lower() in {"none", "- none"}:
        return "No meaningful progress was recorded since the last check-in."
    return text


def discord_payload(checkin: dict[str, Any]) -> dict[str, Any]:
    title = sanitize_text(checkin.get("title", "Goal Companion Check-In"), 240)
    review = public_review(checkin)

    return {
        "username": "Goal Companion",
        "content": "Goal Companion check-in",
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "title": title,
                "description": review,
                "color": 3447003,
                "timestamp": now_iso(),
                "footer": {"text": "Public progress review. Mentions disabled."},
            }
        ],
    }


def webhook_wait_url(webhook_url: str) -> str:
    parsed = parse.urlparse(webhook_url)
    query = parse.parse_qs(parsed.query, keep_blank_values=True)
    query["wait"] = ["true"]
    return parse.urlunparse(parsed._replace(query=parse.urlencode(query, doseq=True)))


def post_to_discord(
    webhook_url: str,
    payload: dict[str, Any],
    timeout: int = 15,
    retry_once: bool = True,
    validate: bool = True,
) -> tuple[bool, str]:
    target_url = validate_webhook_url(webhook_url) if validate else webhook_url
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        webhook_wait_url(target_url),
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "goal-companion"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            if 200 <= status < 300:
                return True, f"Discord webhook sent successfully (HTTP {status})."
            return False, f"Discord webhook returned HTTP {status}."
    except error.HTTPError as exc:
        if exc.code == 429 and retry_once:
            retry_after = 1.0
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
                parsed = json.loads(error_body)
                retry_after = float(parsed.get("retry_after", retry_after))
            except Exception:
                retry_after = 1.0
            time.sleep(min(max(retry_after, 0.0), 5.0))
            return post_to_discord(
                webhook_url, payload, timeout, retry_once=False, validate=validate
            )
        return False, f"Discord webhook failed with HTTP {exc.code}."
    except error.URLError as exc:
        return False, f"Discord webhook request failed: {sanitize_text(exc.reason, 200)}"


def configured_url(config_path: Path) -> str:
    config = load_config(config_path)
    if not config:
        raise ValueError(
            "Discord webhook is not configured. Run `discord_webhook.py configure` first."
        )
    return validate_webhook_url(str(config["webhook_url"]))


def cmd_configure(args: argparse.Namespace) -> int:
    path = args.config
    print("Paste the Discord webhook URL below. Input is hidden and will not be echoed.")
    print("Do not paste the webhook URL into Codex chat or public logs.")
    url = getpass.getpass("Discord webhook URL: ")
    try:
        config = save_config(path, url)
    except ValueError as exc:
        print(f"Discord webhook not saved: {exc}", file=sys.stderr)
        return 2
    print(f"Discord webhook saved to local config: {path}")
    print(redacted_config_status(config))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    print(f"Discord webhook config: {args.config}")
    print(redacted_config_status(config or {}))
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    removed = clear_config(args.config)
    print("Discord webhook config removed." if removed else "Discord webhook was not configured.")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    if not args.yes:
        confirmation = input("Send a safe test message to Discord? Type 'send' to continue: ")
        if confirmation.strip().lower() != "send":
            print("Discord test canceled.")
            return 1
    url = configured_url(args.config)
    payload = discord_payload(
        {
            "title": "Goal Companion Test",
            "since_last_checkin": (
                "Discord delivery is configured and this safe test message rendered "
                "as a brief progress review."
            ),
        }
    )
    ok, message = post_to_discord(url, payload, timeout=args.timeout)
    print(message)
    return 0 if ok else 1


def cmd_send(args: argparse.Namespace) -> int:
    url = configured_url(args.config)
    try:
        checkin = load_checkin_payload(args.payload_file)
    except ValueError as exc:
        print(f"Discord check-in not sent: {exc}", file=sys.stderr)
        return 2
    payload = discord_payload(checkin)
    ok, message = post_to_discord(url, payload, timeout=args.timeout)
    print(message)
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Configure and send Goal Companion Discord check-ins."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="Config path. Defaults to %%LOCALAPPDATA%%\\GoalCompanion\\discord.json.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    configure = subparsers.add_parser("configure", help="Prompt for and save webhook URL.")
    configure.set_defaults(func=cmd_configure)

    status = subparsers.add_parser("status", help="Show redacted configuration status.")
    status.set_defaults(func=cmd_status)

    clear = subparsers.add_parser("clear", help="Remove stored webhook config.")
    clear.set_defaults(func=cmd_clear)

    test = subparsers.add_parser("test", help="Send a safe test Discord message.")
    test.add_argument("--yes", action="store_true", help="Confirm sending the test message.")
    test.add_argument("--timeout", type=int, default=15)
    test.set_defaults(func=cmd_test)

    send = subparsers.add_parser("send", help="Send a check-in payload from stdin or file.")
    send.add_argument("--payload-file", type=Path)
    send.add_argument("--timeout", type=int, default=15)
    send.set_defaults(func=cmd_send)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.config = args.config.expanduser()
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
