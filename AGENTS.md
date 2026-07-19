# Workspace Rule

- When modifying files in this workspace, mirror the same change into the installed global Goal Companion skill at `C:\Users\Piculiar\.codex\skills\goal-companion` before finishing the turn.
- Preserve user config and merge idempotently; do not overwrite unrelated global changes.
- After mirroring, verify the touched workspace and global files match or report any mismatch clearly.
