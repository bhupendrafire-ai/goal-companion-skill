from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "discord_webhook.py"
SPEC = importlib.util.spec_from_file_location("discord_webhook", MODULE_PATH)
assert SPEC is not None
discord_webhook = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(discord_webhook)


class DiscordWebhookPayloadTests(unittest.TestCase):
    def test_payload_renders_brief_review_only(self) -> None:
        payload = discord_webhook.discord_payload(
            {
                "goal": "Complete the long production goal.",
                "since_last_checkin": "Added the export recorder and verified the focused tests.",
                "evidence": ["Focused tests passed."],
                "blockers_or_drift": "None",
                "suggested_goal_statements": {
                    "Recommended": "A goal statement that belongs in Codex, not Discord."
                },
                "next_25_minute_focus": "Continue verification.",
            }
        )

        embed = payload["embeds"][0]
        rendered = json.dumps(payload)

        self.assertEqual(
            embed["description"],
            "Added the export recorder and verified the focused tests.",
        )
        self.assertNotIn("fields", embed)
        self.assertNotIn("Complete the long production goal", rendered)
        self.assertNotIn("Suggested goal", rendered)
        self.assertEqual(payload["allowed_mentions"], {"parse": []})

    def test_load_checkin_payload_strips_bom_before_json_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "checkin.json"
            payload_path.write_text(
                '\ufeff{"since_last_checkin": "Parsed cleanly."}',
                encoding="utf-8",
            )

            payload = discord_webhook.load_checkin_payload(payload_path)

        self.assertEqual(payload["since_last_checkin"], "Parsed cleanly.")

    def test_load_checkin_payload_strips_mojibake_bom_before_json_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload_path = Path(tmp) / "checkin.json"
            payload_path.write_text(
                f'{discord_webhook.MOJIBAKE_BOM}{{"since_last_checkin": "Parsed cleanly."}}',
                encoding="utf-8",
            )

            payload = discord_webhook.load_checkin_payload(payload_path)

        self.assertEqual(payload["since_last_checkin"], "Parsed cleanly.")

    def test_public_review_handles_nested_json_text(self) -> None:
        review = discord_webhook.public_review(
            {
                "since_last_checkin": (
                    '\ufeff{"goal": "Hidden from Discord", '
                    '"since_last_checkin": "Nested summary wins."}'
                )
            }
        )

        self.assertEqual(review, "Nested summary wins.")


if __name__ == "__main__":
    unittest.main()
