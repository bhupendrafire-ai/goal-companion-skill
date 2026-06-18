#!/usr/bin/env python3
"""Install the Goal Companion standing instruction block idempotently."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


START_MARKER = "<!-- goal-companion:start -->"
END_MARKER = "<!-- goal-companion:end -->"
STANDING_BLOCK = """<!-- goal-companion:start -->
# Goal Companion
- Whenever I start a goal, use goal-companion and create a background side thread to refine goal statements.
- During long goals, keep the companion active with heartbeat and milestone checkpoint updates, and stop the keepalive when the goal finishes.
<!-- goal-companion:end -->
"""


def default_agents_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    base = Path(codex_home) if codex_home else Path.home() / ".codex"
    return base / "AGENTS.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append the Goal Companion standing instruction block to Codex AGENTS.md."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned change without writing the file.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=default_agents_path(),
        help="Path to AGENTS.md. Defaults to CODEX_HOME/AGENTS.md or ~/.codex/AGENTS.md.",
    )
    return parser.parse_args()


def append_block(existing: str) -> str:
    text = existing.rstrip()
    if text:
        return f"{text}\n\n{STANDING_BLOCK}"
    return STANDING_BLOCK


def main() -> int:
    args = parse_args()
    target = args.path.expanduser()

    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    has_start = START_MARKER in existing
    has_end = END_MARKER in existing

    if has_start and has_end:
        print(f"Goal Companion standing instruction already present: {target}")
        return 0

    if has_start != has_end:
        print(
            f"Refusing to edit {target}: found only one Goal Companion marker.",
            file=sys.stderr,
        )
        return 2

    updated = append_block(existing)

    if args.dry_run:
        print(f"Would append Goal Companion standing instruction to: {target}")
        print()
        print(STANDING_BLOCK, end="")
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(updated, encoding="utf-8")
    print(f"Installed Goal Companion standing instruction: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
